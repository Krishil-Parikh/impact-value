"""
AI service for generating reports.
Supports Google Gemini (default) and OpenRouter as providers.
Provider is selected via AI_PROVIDER in .env ("gemini" | "openrouter").

Report formats match the ISRI sample documents:
  - Barrier Analysis  → Barrier_Analysis_Report.pdf format
  - Strategic Roadmap → Roadmap Document.docx format
"""
import asyncio
import httpx
import re
from typing import Dict, List, Optional
import datetime
import logging
from config.settings import (
    AI_PROVIDER,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GEMINI_API_URL,
    OPENROUTER_API_KEY,
    OPENROUTER_API_URL,
    OPENROUTER_MODEL,
    OPENROUTER_SITE_URL,
    OPENROUTER_SITE_NAME,
    AI_TEMPERATURE,
    AI_MAX_TOKENS,
    AI_TIMEOUT,
)

logger = logging.getLogger(__name__)

# Retry config
MAX_CONTINUATION_RETRIES = 2
MAX_CHUNK_RETRIES = 2
RATE_LIMIT_RETRIES = 3
RATE_LIMIT_BACKOFF = [30, 60, 90]

# ── Cost / KPI labels ─────────────────────────────────────────────────────────

COST_FACTOR_LABELS = [
    "Aftermarket Services/Warranty", "Depreciation", "Labour",
    "Maintenance & Repair", "Raw Materials & Consumables", "Rental & Operating Lease",
    "Research & Development", "Selling, General & Administrative", "Utilities",
    "EBIT", "Financing Costs (Interest)", "Taxation & Compliance",
    "Supply Chain & Logistics", "Technology & Digital Infrastructure",
    "Training & Skill Development", "Regulatory Compliance", "Insurance",
    "Marketing & Customer Acquisition", "Environmental & Social Responsibility",
    "Quality Control & Assurance",
]

KPI_FACTOR_LABELS = [
    "Asset & Equipment Efficiency", "Utilities Efficiency", "Inventory Efficiency",
    "Process Quality", "Product Quality", "Safety & Security",
    "Planning & Scheduling Effectiveness", "Time to Market", "Production Flexibility",
    "Customer Satisfaction", "Supply Chain Efficiency", "Market Share Growth",
    "Employee Productivity", "Return on Investment (ROI)", "Financial Health & Stability",
    "Talent Retention", "Customer Retention Rate",
]

COST_BARRIER_WEIGHTS = [
    [0,0,2,0,0,0,2,1,0,2,1,1,1,3,3,1,1,1,2,1],  # B1
    [0,0,2,0,0,0,1,1,0,1,1,1,1,2,2,1,1,1,1,1],  # B2
    [0,0,2,0,0,0,1,1,0,1,1,1,1,3,3,1,1,1,2,1],  # B3
    [0,0,2,0,0,0,2,1,0,1,1,1,1,3,3,1,1,1,2,1],  # B4
    [0,0,2,0,0,0,2,1,0,2,1,1,1,3,3,1,1,1,2,1],  # B5
    [0,0,2,0,0,0,1,1,0,1,1,1,1,2,2,1,1,1,1,1],  # B6
    [0,0,2,0,0,0,1,1,0,1,1,1,1,2,2,1,1,1,1,1],  # B7
    [0,0,2,0,0,0,1,1,0,1,1,1,1,2,2,1,1,1,1,1],  # B8
    [0,0,2,0,0,0,1,2,0,3,3,1,2,1,1,1,1,1,1,1],  # B9
    [2,1,3,2,2,1,3,3,2,3,2,2,3,3,3,3,1,3,2,3],  # B10
    [0,0,2,0,0,0,1,1,0,2,2,1,2,1,1,1,1,1,1,1],  # B11
    [0,0,2,0,0,0,2,1,0,3,2,3,2,1,1,3,1,1,1,1],  # B12
    [0,0,2,0,0,0,1,1,0,2,2,3,2,1,1,3,1,1,1,1],  # B13
    [0,0,2,0,0,0,1,1,0,2,2,3,2,1,1,3,1,1,1,1],  # B14
    [0,0,2,0,0,0,1,1,0,2,1,1,2,3,3,1,1,1,1,1],  # B15
]

KPI_BARRIER_WEIGHTS = [
    [1,1,1,2,2,1,2,1,2,1,1,2,3,2,2,3,2],  # B1
    [1,1,1,2,2,1,2,1,2,1,1,2,3,2,2,3,2],  # B2
    [1,1,1,2,2,1,2,2,2,1,1,1,3,2,2,3,2],  # B3
    [1,1,1,2,2,1,2,2,2,1,1,1,3,2,2,3,2],  # B4
    [1,1,1,2,2,1,2,2,2,1,1,1,3,2,2,2,2],  # B5
    [1,0,1,2,2,2,1,1,2,2,1,2,1,3,3,1,2],  # B6
    [1,0,1,2,2,2,1,1,2,2,1,2,1,2,2,1,2],  # B7
    [1,0,1,2,2,1,2,2,2,1,1,1,2,2,2,1,1],  # B8
    [2,1,2,1,1,0,1,2,2,1,2,2,2,3,3,1,1],  # B9
    [3,2,3,3,3,2,3,3,3,3,3,3,3,3,3,2,3],  # B10
    [2,1,2,1,1,1,2,2,2,1,3,1,2,2,2,1,2],  # B11
    [1,0,1,1,1,0,1,2,1,1,2,1,1,3,3,1,1],  # B12
    [1,0,1,2,2,2,1,1,2,2,1,2,1,3,3,1,2],  # B13
    [1,0,1,2,2,2,1,1,2,2,1,2,1,3,3,1,2],  # B14
    [1,0,1,2,2,2,1,1,2,2,1,1,1,2,2,1,3],  # B15
]


# ── ISRI Barrier Knowledge Base ───────────────────────────────────────────────
# Sourced verbatim from Roadmap Document.docx and barrier_analysis PDFs.
# Each entry contains the prescriptive framework the AI must adapt to the company.

BARRIER_KNOWLEDGE_BASE: Dict[int, Dict] = {
    1: {
        "name": "Lack of training for workers and Managers",
        "drivers": [
            "Employee acceptance by motivation and incentives",
            "Top management support and Participation",
        ],
        "root_cause_template": (
            "The deficiency in training is not simply a resource issue; it is a significant cultural "
            "and strategic failure. Our analysis shows this barrier is strongly influenced by a lack of "
            "both top-down commitment from leadership and bottom-up motivation for employees to embrace "
            "new skills. Without leadership actively championing the cause and employees feeling personally "
            "invested in the outcomes, any training initiative is destined to fail."
        ),
        "strategic_goal": "To create a sustainable training culture driven by visible leadership support and tangible employee benefits.",
        "phases": {
            1: {
                "name": "Demonstrate Commitment", "duration": "First 3 Months",
                "actions": [
                    {"title": '"Leadership in Learning" Kick-off', "driver_ref": "Driver 2",
                     "description": "The Director/CEO must personally launch the new training initiative at a company-wide meeting. They must not only announce the program but be the first person to enroll in a relevant module (e.g., a manager's course on digital transformation).",
                     "owner": "Director / CEO"},
                    {"title": "Define a 'Skill-Up Bonus' Structure", "driver_ref": "Driver 1",
                     "description": "Work with HR to define a clear, simple incentive. Any employee who successfully completes a specific certification receives a one-time 'Skill-Up Bonus' (e.g., ₹5,000 per certification).",
                     "owner": "HR Manager"},
                ]
            },
            2: {
                "name": "Implement & Motivate", "duration": "Next 6 Months",
                "actions": [
                    {"title": '"Manager-as-Mentor" Program', "driver_ref": "Driver 2",
                     "description": "Require all department managers to dedicate 2 hours per month to personally mentor their team members on the new skills. This makes training an active management responsibility, not a passive HR task.",
                     "owner": "All Department Heads"},
                    {"title": 'Create a "Hall of Skills"', "driver_ref": "Driver 1",
                     "description": "Create a physical or digital notice board that publicly recognizes every employee who completes a training course or earns a certification, creating a powerful low-cost motivator.",
                     "owner": "HR Manager / Production Head"},
                ]
            },
            3: {
                "name": "Embed into the Culture", "duration": "12+ Months",
                "actions": [
                    {"title": "Link Training to Promotions", "driver_ref": "Driver 1 & 2",
                     "description": "Formalize the process so that completion of specific advanced training modules becomes a prerequisite for promotions to senior operator or supervisory roles.",
                     "owner": "Director / HR Manager"},
                    {"title": "Allocate Training in Annual Budget", "driver_ref": "Driver 2",
                     "description": "Top management must approve a dedicated line item for training in the annual budget, demonstrating long-term financial commitment to employee development.",
                     "owner": "Finance Head / CEO"},
                ]
            },
        },
    },
    2: {
        "name": "Resistance to change",
        "drivers": [
            "Employee acceptance by motivation and incentives",
            "Rapid deployment through Cloud IoT",
            "Balanced and empowered team",
            "Top management support and Participation",
        ],
        "root_cause_template": (
            "Resistance to change within the organization is not simply stubbornness; it is often a "
            "response to fear of the unknown, a lack of clear direction from leadership, and a feeling "
            "of disempowerment among employees. Our analysis shows this resistance is strongly influenced "
            "by a top-down failure to lead the change and a bottom-up failure to involve and empower the "
            "teams who must implement it."
        ),
        "strategic_goal": "To transform resistance into active participation by creating a clear vision, empowering teams, and making change easy and rewarding.",
        "phases": {
            1: {
                "name": "Set the Stage for Change", "duration": "First 3 Months",
                "actions": [
                    {"title": '"Vision and Safety Net" Town Hall', "driver_ref": "Driver 4",
                     "description": "The Director/CEO must hold a company-wide meeting to clearly explain why the change is necessary and provide a 'safety net' promise: this technology is here to make jobs better and more secure, not to replace anyone.",
                     "owner": "Director / CEO"},
                    {"title": 'Form a Cross-Functional "Change Team"', "driver_ref": "Driver 3",
                     "description": "Create a small, balanced team with members from different departments (e.g., one senior operator, one young engineer, one supervisor). Empower this team to be the primary decision-makers for the initial pilot project.",
                     "owner": "Production Head"},
                ]
            },
            2: {
                "name": "Make Change Easy and Rewarding", "duration": "Next 6 Months",
                "actions": [
                    {"title": 'Launch a "Low-Disruption" Pilot Project', "driver_ref": "Driver 2",
                     "description": "Use a cloud-based IoT solution to launch a pilot that is easy and fast to deploy (e.g., monitoring a non-critical machine). A quick, successful deployment builds confidence and shows that change doesn't have to be difficult.",
                     "owner": "Change Team / IT Head"},
                    {"title": '"Early Adopter" Incentive Program', "driver_ref": "Driver 1",
                     "description": "Publicly recognize and reward employees who actively participate in the pilot project. This could be a certificate, a small bonus, or a team lunch, creating a positive buzz around the change.",
                     "owner": "HR Manager"},
                ]
            },
            3: {
                "name": "Empower and Scale", "duration": "12+ Months",
                "actions": [
                    {"title": "Delegate Rollout Decisions", "driver_ref": "Driver 3",
                     "description": "Empower the Change Team to lead the plan for the next phase of the rollout. When employees see their peers leading the change, resistance decreases dramatically.",
                     "owner": "Production Head / Change Team"},
                    {"title": 'Formalize "Change Leadership" in Roles', "driver_ref": "Driver 1 & 4",
                     "description": "Update job descriptions for supervisors and managers to include 'leading and supporting change initiatives' as a key responsibility, linked to performance reviews.",
                     "owner": "HR Manager / Director"},
                ]
            },
        },
    },
    3: {
        "name": "Lack of digital culture and training",
        "drivers": [
            "Confidence of customers in Internet transactions",
            "Simulation for Decision-Making",
            "Employee acceptance by motivation and incentives",
            "Change of organizational culture through decentralization",
        ],
        "root_cause_template": (
            "A weak digital culture is a primary obstacle to modernization, characterized by a workforce "
            "that is untrained and unmotivated to adopt new tools. Our analysis shows this is strongly "
            "influenced by a centralized culture that stifles initiative and a failure to provide safe, "
            "practical ways for employees to learn. Ultimately, this internal weakness impacts the company's "
            "ability to operate in a modern way, which erodes the confidence of digitally-savvy customers."
        ),
        "strategic_goal": "To build a vibrant digital culture by decentralizing learning, making it safe to experiment, and motivating employees to embrace new skills.",
        "phases": {
            1: {
                "name": "Decentralize Ownership & Provide Safe Tools", "duration": "First 3 Months",
                "actions": [
                    {"title": 'Create Departmental "Digital Upskilling" Plans', "driver_ref": "Driver 4",
                     "description": "Instead of a single top-down training plan, empower each department head to create a simple upskilling plan for their own team, focusing on one or two digital tools most relevant to their work.",
                     "owner": "All Department Heads"},
                    {"title": 'Introduce a "Digital Sandbox" Environment', "driver_ref": "Driver 2",
                     "description": "Create a training or simulation version of your key software/systems where employees can practice using new digital tools without any fear of making a mistake in the live production environment.",
                     "owner": "IT Head"},
                ]
            },
            2: {
                "name": "Motivate and Demonstrate Value", "duration": "Next 6 Months",
                "actions": [
                    {"title": 'Launch a "Digital Star of the Month" Program', "driver_ref": "Driver 3",
                     "description": "Motivate employees by publicly celebrating the individual who most effectively uses a new digital tool to improve a process. Reward with a certificate, a small bonus, and recognition on the company notice board.",
                     "owner": "HR Manager"},
                    {"title": "Simulate a Customer Success Story", "driver_ref": "Driver 1 & 2",
                     "description": "Use simulation tools to create a demonstration showing how using digital tools internally (e.g., for quality control) directly leads to a better product for the customer, connecting employee actions to customer value.",
                     "owner": "Sales Head / Production Head"},
                ]
            },
            3: {
                "name": "Embed and Formalize the Digital Culture", "duration": "12+ Months",
                "actions": [
                    {"title": 'Transition "Digital Upskilling" to a Core Job Responsibility', "driver_ref": "Driver 4",
                     "description": "Update job descriptions for all roles to include a responsibility for 'maintaining and improving relevant digital skills', making learning a formal part of everyone's job.",
                     "owner": "Director / HR Manager"},
                    {"title": "Link Digital Proficiency to Career Growth", "driver_ref": "Driver 3",
                     "description": "Formalize a system where demonstrated expertise in key digital tools is a mandatory requirement for consideration for promotions or higher pay grades.",
                     "owner": "HR Manager"},
                ]
            },
        },
    },
    4: {
        "name": "Higher investment in employees' training",
        "drivers": [
            "Continued specialized skills training",
            "Top management support and Participation",
            "Strategic digitized vision",
        ],
        "root_cause_template": (
            "The perception of training as a 'high cost' rather than a strategic investment is a significant "
            "barrier to growth. Our analysis shows this issue is strongly influenced by a lack of a clear, "
            "overarching digital vision from leadership. Without a strategic purpose, training expenses seem "
            "unjustified and disconnected from business goals. Top management must not only define this vision "
            "but also actively participate to demonstrate that skill development is a core business priority."
        ),
        "strategic_goal": "To reframe training from a high cost into a necessary, high-return investment by directly linking it to the company's strategic vision.",
        "phases": {
            1: {
                "name": 'Define the "Why"', "duration": "First 3 Months",
                "actions": [
                    {"title": '"Factory of the Future" Vision Statement', "driver_ref": "Driver 3",
                     "description": "Top management must create and communicate a simple, one-page vision for the company's digital future (e.g., 'By 2027, we will be a smart factory that uses data to reduce waste by 20%').",
                     "owner": "Director / CEO"},
                    {"title": '"Invest in the Vision" Leadership Pledge', "driver_ref": "Driver 2",
                     "description": "The Director must publicly commit a specific, non-negotiable budget for training for the next year, framing it as a necessary investment to achieve the strategic vision.",
                     "owner": "Director / CEO"},
                ]
            },
            2: {
                "name": "Targeted, High-Impact Training", "duration": "Next 6 Months",
                "actions": [
                    {"title": '"Vision-Critical" Skills Program', "driver_ref": "Driver 1 & 3",
                     "description": "Instead of generic training, focus exclusively on specialized skills that directly support the new vision. If the goal is reducing waste, training should focus on data analytics for process control.",
                     "owner": "Production Head / HR Manager"},
                    {"title": '"Top Management Teaches" Session', "driver_ref": "Driver 2",
                     "description": "Require senior managers to personally host one short knowledge-sharing session per quarter, explaining how the new skills align with the company's strategic goals.",
                     "owner": "All Department Heads"},
                ]
            },
            3: {
                "name": "Empower and Scale", "duration": "12+ Months",
                "actions": [
                    {"title": "Delegate Rollout Decisions", "driver_ref": "Driver 3",
                     "description": "Empower trained teams to lead the next phase of the skills rollout. When employees see their peers leading development, investment perception shifts permanently.",
                     "owner": "Production Head / Training Lead"},
                    {"title": 'Formalize "Change Leadership" in Roles', "driver_ref": "Driver 1 & 2",
                     "description": "Update job descriptions for supervisors to include 'leading and supporting capability development initiatives' as a key responsibility, linked to performance reviews.",
                     "owner": "HR Manager / Director"},
                ]
            },
        },
    },
    5: {
        "name": "Lack of knowledge management systems",
        "drivers": [
            "Confidence of customers in Internet transactions",
            "Integrated Systems Across Departments and Suppliers",
            "Maximizing asset utilization",
            "Customized Solutions for Existing Setups",
        ],
        "root_cause_template": (
            "The absence of a formal knowledge management system (KMS) leads to critical information being "
            "siloed, lost, or inaccessible. Our analysis shows this is strongly influenced by a lack of "
            "integrated systems to share information and a failure to tie knowledge management to a high-value "
            "business outcome, such as maximizing asset utilization. This internal chaos ultimately damages "
            "customer confidence, as they perceive the company as disorganized and inefficient."
        ),
        "strategic_goal": "To create a focused knowledge management system that improves asset utilization, supports customization, and builds customer confidence.",
        "phases": {
            1: {
                "name": "Focus on a High-Value Problem", "duration": "First 3 Months",
                "actions": [
                    {"title": 'Create an "Asset Knowledge Hub"', "driver_ref": "Driver 3",
                     "description": "Instead of a generic company-wide wiki, create a focused KMS dedicated to maximizing asset utilization — storing maintenance schedules, repair histories, and best-practice procedures for your top 5 most critical machines.",
                     "owner": "Production Head"},
                    {"title": "Digitize Customization Blueprints", "driver_ref": "Driver 4",
                     "description": "Scan and upload all technical drawings and notes related to customized solutions created for clients into a secure, accessible digital folder, preventing loss of critical intellectual property.",
                     "owner": "Engineering / Design Head"},
                ]
            },
            2: {
                "name": "Integrate and Share Knowledge", "duration": "Next 6 Months",
                "actions": [
                    {"title": "Link Maintenance Logs to the Knowledge Hub", "driver_ref": "Driver 2 & 3",
                     "description": "Integrate your maintenance team's daily logs directly into the Asset Knowledge Hub, ensuring every repair and observation is captured for troubleshooting future problems and maximizing uptime.",
                     "owner": "Maintenance Head"},
                    {"title": 'Share "Asset Performance Reports" with Key Customers', "driver_ref": "Driver 1",
                     "description": "For customers whose products rely on your critical machines, proactively share a simplified performance report from the Knowledge Hub (e.g., 'Machine X had 99.8% uptime last month'). This transparency builds immense customer confidence.",
                     "owner": "Sales Head"},
                ]
            },
            3: {
                "name": "Expand and Scale the System", "duration": "12+ Months",
                "actions": [
                    {"title": 'Create a "Supplier Knowledge Portal"', "driver_ref": "Driver 2",
                     "description": "Provide key material and parts suppliers with limited access to relevant parts of your KMS such as inventory levels and production forecasts, improving supply chain efficiency.",
                     "owner": "Supply Chain Head"},
                    {"title": "Evolve into a Full-Fledged KMS", "driver_ref": "All Drivers",
                     "description": "Using the Asset Knowledge Hub as a model, expand the system to other departments like Sales (customer histories) and HR (training materials), creating a truly integrated knowledge-sharing culture.",
                     "owner": "Director / IT Head"},
                ]
            },
        },
    },
    6: {
        "name": "Regulatory compliance issues",
        "drivers": [
            "Top management support and Participation",
            "Robust Cybersecurity Measures",
            "Continued specialized skills training",
            "Integrated Systems Across Departments and Suppliers",
            "Enhanced corporate control",
        ],
        "root_cause_template": (
            "Failures in regulatory compliance are a critical business risk, stemming from a lack of strategic "
            "ownership, inadequate systems, and unprepared staff. Our analysis shows this barrier is driven by "
            "a lack of top-down commitment to establish and enforce clear controls. Without leadership support, "
            "systems are not integrated, staff are not trained on specific regulations (like DPDPA or MPCB rules), "
            "and cybersecurity is neglected, leaving the company exposed to significant legal and financial penalties."
        ),
        "strategic_goal": "To establish a resilient, top-down compliance framework that is systematic, secure, and deeply understood by all relevant personnel.",
        "phases": {
            1: {
                "name": "Establish Leadership & Control", "duration": "First 3 Months",
                "actions": [
                    {"title": 'Form a "Compliance Steering Committee"', "driver_ref": "Driver 1 & 5",
                     "description": "The Director must create and personally chair a committee with heads of Production, IT, and HR. Their first task is to formally document the top 5 regulatory requirements the business must adhere to.",
                     "owner": "Director / CEO"},
                    {"title": "Mandate Foundational Cybersecurity Training", "driver_ref": "Driver 2 & 3",
                     "description": "All employees who handle digital data must complete a mandatory training module on basic cybersecurity hygiene and the principles of India's DPDPA law.",
                     "owner": "IT Head / HR Manager"},
                ]
            },
            2: {
                "name": "Implement Systems & Skills", "duration": "Next 6 Months",
                "actions": [
                    {"title": '"Single Source of Truth" Data Project', "driver_ref": "Driver 4",
                     "description": "Initiate a project to integrate data from the two most critical systems (e.g., production line PLC and raw material inventory) into one central dashboard for compliance reporting.",
                     "owner": "IT Head / Production Head"},
                    {"title": "Conduct Role-Specific Compliance Training", "driver_ref": "Driver 3",
                     "description": "Provide specialized training on specific regulations only to the teams that need it: maintenance team on MPCB waste disposal rules, design team on BIS product standards.",
                     "owner": "Department Heads"},
                ]
            },
            3: {
                "name": "Automate, Audit & Secure", "duration": "12+ Months",
                "actions": [
                    {"title": "Implement Secure Data-Sharing Protocol with Key Supplier", "driver_ref": "Driver 2 & 4",
                     "description": "Extend your integrated system by creating a secure, encrypted data link with one major supplier to track material traceability — a common regulatory requirement.",
                     "owner": "Supply Chain Head"},
                    {"title": '"Management-Led" Internal Audits', "driver_ref": "Driver 1 & 5",
                     "description": "The Compliance Steering Committee, led by top management, must conduct quarterly internal audits to verify that documented controls and procedures are being followed.",
                     "owner": "Director / Compliance Steering Committee"},
                ]
            },
        },
    },
    7: {
        "name": "Lack of Standards and Reference Architecture",
        "drivers": [
            "Employee acceptance by motivation and incentives",
            "Rapid deployment through Cloud IoT",
            "Change of organizational culture through decentralization",
            "Scalability of IoT Solutions",
        ],
        "root_cause_template": (
            "The absence of technical standards and a guiding reference architecture creates a chaotic 'wild west' "
            "approach to technology, leading to incompatible systems, security risks, and an inability to scale. "
            "Our analysis shows this technical problem is deeply linked to a centralized culture where teams are "
            "not empowered to own and implement standards. Overcoming this requires making standards easy to adopt "
            "via the cloud and creating a culture that rewards adherence."
        ),
        "strategic_goal": "To establish and culturally embed a core set of technical standards that enables rapid, scalable, and coherent IoT deployment.",
        "phases": {
            1: {
                "name": "Define the Standard & Empower a Team", "duration": "First 3 Months",
                "actions": [
                    {"title": "Select a Standard Cloud IoT Platform", "driver_ref": "Driver 2 & 4",
                     "description": "Choose a single, reputable cloud provider (e.g., AWS, Azure) to be the standard for all future IoT projects. This immediately provides a scalable reference architecture and pre-defined tools enabling rapid deployment.",
                     "owner": "IT Head / Director"},
                    {"title": 'Form and Empower an "Architecture Guild"', "driver_ref": "Driver 3",
                     "description": "Create a small, decentralized team with members from IT, Production, and Maintenance. Empower this guild to select the top 3 initial technical standards (e.g., MQTT for messaging) for the chosen cloud platform.",
                     "owner": "Director"},
                ]
            },
            2: {
                "name": "Drive Adoption through Incentives", "duration": "Next 6 Months",
                "actions": [
                    {"title": '"Standardization Challenge"', "driver_ref": "Driver 1",
                     "description": "Launch an incentive program that rewards the first team to successfully deploy a project that fully complies with the 3 new standards set by the Architecture Guild.",
                     "owner": "HR Manager / Architecture Guild"},
                    {"title": '"Template-Based" Project Deployment', "driver_ref": "Driver 2",
                     "description": "Use the cloud platform to create a simple, reusable project template (e.g., a Standard Machine Monitoring Kit) that allows other teams to rapidly deploy new standardized solutions without deep technical expertise.",
                     "owner": "IT Head"},
                ]
            },
            3: {
                "name": "Scale and Formalize", "duration": "12+ Months",
                "actions": [
                    {"title": '"Scalability Review" for All New Projects', "driver_ref": "Driver 4",
                     "description": "Mandate that no new technology project can be approved without a review by the Architecture Guild to ensure it adheres to established standards and is built for future scalability.",
                     "owner": "Architecture Guild / Director"},
                    {"title": "Link Adherence to Team Performance", "driver_ref": "Driver 1 & 3",
                     "description": "Include 'adherence to company technical standards' as a metric in performance reviews for all technical and production departments, making following standards a formal part of the job.",
                     "owner": "Department Heads / HR Manager"},
                ]
            },
        },
    },
    8: {
        "name": "Lack of Internet coverage and IT facilities",
        "drivers": [
            "Reduced upfront investment as pay-per-service cloud analytics and Storage Cost are rental",
            "Internet facility from government at reduced price",
            "Change of organizational culture through decentralization",
            "Strategic digitized vision",
        ],
        "root_cause_template": (
            "Inadequate internet and IT facilities create a fundamental bottleneck, preventing the adoption of "
            "modern digital tools. Our analysis shows this infrastructure problem is influenced by a lack of "
            "strategic vision to justify targeted investment. Without a clear plan, the company cannot effectively "
            "leverage available financial drivers (like government schemes and pay-per-use cloud services) to "
            "affordably solve its connectivity gaps."
        ),
        "strategic_goal": "To provide reliable, cost-effective connectivity to all critical operational areas by aligning strategic vision with smart financial decisions and empowered local teams.",
        "phases": {
            1: {
                "name": "Strategic Assessment & Quick Wins", "duration": "First 3 Months",
                "actions": [
                    {"title": '"Connectivity Heatmap" Aligned with Vision', "driver_ref": "Driver 4",
                     "description": "Develop a simple map of your facility colour-coded by current internet quality, overlaid with the top 3 areas most critical to your strategic digitized vision — identifying where investment is most needed.",
                     "owner": "IT Head / Director"},
                    {"title": "Apply for Government Internet Schemes", "driver_ref": "Driver 2",
                     "description": "Actively research and apply for programs like PM-WANI or Bharat Net-related schemes that offer subsidized, high-speed internet connectivity for businesses in industrial areas.",
                     "owner": "Admin / Finance Head"},
                ]
            },
            2: {
                "name": "Decentralized & Affordable Solutions", "duration": "Next 6 Months",
                "actions": [
                    {"title": 'Empower "Connectivity Captains" for Remote Sites', "driver_ref": "Driver 3",
                     "description": "For areas with poor coverage, empower a local site manager as the 'Connectivity Captain' with a dedicated budget to deploy a localized solution (e.g., a dedicated 4G/5G router) rather than waiting for a central IT solution.",
                     "owner": "Director / Site Managers"},
                    {"title": "Shift Data Storage to a Pay-Per-Service Cloud", "driver_ref": "Driver 1",
                     "description": "Migrate heavy data storage from on-premise servers to a pay-per-use cloud solution, reducing the immediate investment needed for IT hardware and freeing up capital for connectivity upgrades.",
                     "owner": "IT Head"},
                ]
            },
            3: {
                "name": "Build a Resilient, Hybrid Infrastructure", "duration": "12+ Months",
                "actions": [
                    {"title": "Deploy Edge Computing for Low-Bandwidth Areas", "driver_ref": "Driver 1 & 4",
                     "description": "In areas where high-speed internet is not feasible, implement edge computing gateways that process data locally and only send small essential summaries to the cloud, reducing bandwidth requirements.",
                     "owner": "IT Head"},
                    {"title": "Formalize Decentralized IT Budgets", "driver_ref": "Driver 3",
                     "description": "As part of the annual budget, allocate a small dedicated IT/connectivity budget to each department or site, empowering them to manage their own specific needs.",
                     "owner": "Finance Head / Director"},
                ]
            },
        },
    },
    9: {
        "name": "Limited Access to Funding and Credit",
        "drivers": [
            "Reduced upfront investment (pay-per-service model)",
            "Maximizing asset utilization",
            "Simulation for Decision-Making",
            "Productive and Preventive Maintenance",
            "Development of a Data-Driven Business Case for Lenders",
        ],
        "root_cause_template": (
            "Limited access to funding is a major growth constraint, often stemming from an inability to present "
            "a compelling, low-risk case to lenders. Our analysis shows this barrier is strongly influenced by a "
            "failure to demonstrate operational efficiency and to translate technical needs into a clear, "
            "data-driven financial plan. By focusing on maximizing existing assets and building a professional "
            "business case, the company can significantly improve its attractiveness to financial institutions."
        ),
        "strategic_goal": "To build a powerful, data-driven business case that proves operational efficiency and de-risks investment for potential lenders.",
        "phases": {
            1: {
                "name": "Optimize Internally", "duration": "First 3 Months",
                "actions": [
                    {"title": "Implement an Asset Utilization Monitoring Program", "driver_ref": "Driver 2",
                     "description": "Install simple IoT sensors on your top 3 most critical machines to track uptime, downtime, and output. The goal is to gather baseline data that proves you are already using your current assets effectively.",
                     "owner": "Production Head"},
                    {"title": "Strengthen the Preventive Maintenance Schedule", "driver_ref": "Driver 4",
                     "description": "Use data from asset monitoring to create a data-informed preventive maintenance schedule. A documented history of proactive maintenance is a key indicator of low operational risk for lenders.",
                     "owner": "Maintenance Head"},
                ]
            },
            2: {
                "name": "De-Risk the Ask", "duration": "Next 6 Months",
                "actions": [
                    {"title": 'Shift to a "Cloud-First" IT Strategy', "driver_ref": "Driver 1",
                     "description": "For any new software needs, adopt pay-per-service cloud solutions instead of buying on-premise servers. This drastically reduces the required upfront capital investment for your technology plan.",
                     "owner": "IT Head"},
                    {"title": '"Digital Twin" Simulation of the Proposed Project', "driver_ref": "Driver 3",
                     "description": "Use simulation software to model the financial impact of your proposed investment, projecting expected ROI, payback period, and key financial benefits — providing a robust forecast to show lenders.",
                     "owner": "Finance Head / Director"},
                ]
            },
            3: {
                "name": "Engage with Lenders", "duration": "12+ Months",
                "actions": [
                    {"title": "Construct the Formal Data-Driven Business Case", "driver_ref": "Driver 5",
                     "description": "Combine outputs from the previous steps into a single professional business case: (a) proof of current asset efficiency, (b) lower capital request due to cloud strategy, and (c) financial projections from simulation.",
                     "owner": "Director / Finance Head"},
                    {"title": "Proactive Engagement with Financial Institutions", "driver_ref": "Driver 5",
                     "description": "Schedule meetings with bank managers (especially those with SME or technology financing departments like SIDBI) to personally present your data-driven business case, significantly increasing chances of approval.",
                     "owner": "Director"},
                ]
            },
        },
    },
    10: {
        "name": "Future viability & profitability",
        "drivers": [
            "Strategic digitized vision",
            "Reduced upfront investment as pay-per-service",
            "Maximizing asset utilization",
            "Integrated Systems Across Departments and Suppliers",
            "Big Data Analytics",
            "Customized Solutions for Existing Setups",
        ],
        "root_cause_template": (
            "The critical doubt over the future viability and profitability of IoT investment stems from a "
            "disconnect between technological capabilities and clear business outcomes. Our analysis shows that "
            "to solve this, a powerful strategic vision is needed to guide technology choices, which must then "
            "be made financially feasible. The path to profitability lies in first integrating systems to achieve "
            "internal efficiencies, then using analytics to find new opportunities."
        ),
        "strategic_goal": "To execute an end-to-end strategy that transforms data into demonstrable profitability and secures the company's future.",
        "phases": {
            1: {
                "name": "Set the Vision & Financial Foundation", "duration": "First 3 Months",
                "actions": [
                    {"title": 'Publish the "Smart Factory 2027" Vision', "driver_ref": "Driver 1",
                     "description": "The Director must define and communicate a clear strategic vision with a tangible goal, e.g., 'By 2027, we will use data to become a zero-downtime, premium quality supplier.'",
                     "owner": "Director / CEO"},
                    {"title": '"OpEx-First" Technology Policy', "driver_ref": "Driver 2",
                     "description": "Mandate that all new technology investments must first be evaluated for a pay-per-service or rental model before any large upfront capital purchase is considered, immediately lowering financial risk.",
                     "owner": "Finance Head"},
                ]
            },
            2: {
                "name": "Integrate for Efficiency & Intelligence", "duration": "Next 6 Months",
                "actions": [
                    {"title": '"Project Unify"', "driver_ref": "Driver 4",
                     "description": "Initiate a project to integrate the two most critical data silos: your main production machine data and your raw material inventory system, creating the foundational data set for analysis.",
                     "owner": "IT Head"},
                    {"title": '"Uptime Challenge" — Focus on Asset Utilization', "driver_ref": "Driver 3",
                     "description": "Using the newly integrated data, launch a company-wide challenge to increase the uptime and output of your most valuable asset by 10% in 6 months, with clear tracking visible to all.",
                     "owner": "Production Head"},
                ]
            },
            3: {
                "name": "Analyze for New Revenue", "duration": "12+ Months",
                "actions": [
                    {"title": "Deploy a BI Analytics Dashboard", "driver_ref": "Driver 5",
                     "description": "Implement a business intelligence tool (like Microsoft Power BI or Tableau) to analyze the data from Project Unify. The first goal is to create a report identifying the top 3 causes of downtime or defects.",
                     "owner": "IT Head / Analyst"},
                    {"title": 'Pilot a "Predictive Quality" Service', "driver_ref": "Driver 6",
                     "description": "Use insights from your analytics dashboard to create a new, high-value customized service for your top client — a 'Predictive Quality' service that prevents defects before they happen, turning internal efficiency into profitable revenue.",
                     "owner": "Sales Head / Director"},
                ]
            },
        },
    },
    11: {
        "name": "Dependency on External Vendors",
        "drivers": [
            "Continued specialized skills training",
            "Balanced and empowered team",
            "Maximizing asset utilization",
            "Top management support and Participation",
            "Integrated Systems Across Departments and Suppliers",
        ],
        "root_cause_template": (
            "A high dependency on external vendors creates significant business risk, including high costs, loss of "
            "control, and being trapped by a third party's technical limitations. Our analysis shows this dependency "
            "is driven by a lack of internal skills and system ownership, a problem that can only be solved with "
            "clear, unwavering support from top management to invest in building in-house capability."
        ),
        "strategic_goal": "To systematically reduce vendor dependency by building a skilled internal team that can own, manage, and optimize your core operational systems.",
        "phases": {
            1: {
                "name": "Leadership Commitment & Foundational Skills", "duration": "First 3 Months",
                "actions": [
                    {"title": '"Own Our Operations" Strategic Mandate', "driver_ref": "Driver 4",
                     "description": "Top management must issue a clear directive that the company's long-term goal is to build internal expertise to manage all critical operational systems, providing the authority and budget for the following steps.",
                     "owner": "Director / CEO"},
                    {"title": '"Level 1 Certification" Training Program', "driver_ref": "Driver 1",
                     "description": "Identify 3-4 employees from Production and Maintenance and enroll them in a 'Level 1' certification course for your most critical vendor-supplied system, with the goal of handling all basic troubleshooting internally.",
                     "owner": "HR Manager / Production Head"},
                ]
            },
            2: {
                "name": "Empowerment and System Ownership", "duration": "Next 6 Months",
                "actions": [
                    {"title": 'Form the "Internal Tech Support" Team', "driver_ref": "Driver 2",
                     "description": "Formally designate the newly trained employees as the official Internal Tech Support team, empowering them with the responsibility to be the first point of contact for any system issue before contacting the external vendor.",
                     "owner": "Production Head"},
                    {"title": "Integrate Asset Monitoring with an Internal Dashboard", "driver_ref": "Driver 3 & 5",
                     "description": "Task the new internal team with pulling data from your vendor's system (via API if possible) into your own internal dashboard to monitor asset utilization — the first step towards owning your own data.",
                     "owner": "Internal Tech Support Team / IT Head"},
                ]
            },
            3: {
                "name": "Build Independence", "duration": "12+ Months",
                "actions": [
                    {"title": '"Level 2" Advanced Training & Customization', "driver_ref": "Driver 1",
                     "description": "Invest in advanced Level 2 training for your internal team, focusing on system customization and integration — building the skills needed to modify and adapt the system without vendor support.",
                     "owner": "Director / HR Manager"},
                    {"title": 'Renegotiate Vendor Contract to a "Support-Only" Model', "driver_ref": "All Drivers",
                     "description": "With a skilled internal team now managing day-to-day operations, use this newfound leverage to renegotiate your expensive vendor contract to a less costly 'emergency-support-only' tier, delivering direct financial savings.",
                     "owner": "Finance Head / Director"},
                ]
            },
        },
    },
    12: {
        "name": "High Implementation Cost",
        "drivers": [
            "Reduced upfront investment as pay-per-service",
            "Cloud-Based IoT Solutions",
            "Scalability of IoT Solutions",
            "Customized Solutions for Existing Setups",
            "Simulation for Decision-Making",
        ],
        "root_cause_template": (
            "The high upfront cost of IoT implementation is a primary obstacle, often halting projects before they "
            "begin. Our analysis shows this financial barrier is driven by a traditional approach to capital "
            "expenditure and a failure to leverage modern, flexible technologies. To overcome this, the company must "
            "adopt a strategy emphasizing smart planning, utilization of existing assets, and a shift to scalable "
            "pay-per-use cloud models that convert large upfront costs into manageable operating expenses."
        ),
        "strategic_goal": "To de-risk and reduce the cost of IoT implementation through smart planning, a cloud-first approach, and a scalable, pay-per-service financial model.",
        "phases": {
            1: {
                "name": "Plan for Maximum Cost-Effectiveness", "duration": "First 3 Months",
                "actions": [
                    {"title": '"Virtual Factory" Simulation', "driver_ref": "Driver 5",
                     "description": "Before purchasing any hardware, create a digital simulation of your planned IoT project. Model the costs and benefits of connecting different machines to identify the single most cost-effective starter project with the fastest payback period.",
                     "owner": "Director / Finance Head"},
                    {"title": '"No Rip-and-Replace" Audit', "driver_ref": "Driver 4",
                     "description": "Conduct an audit of your existing machinery to identify how a new IoT solution can be customized to connect with current equipment, explicitly avoiding the massive cost of replacing legacy systems.",
                     "owner": "Production Head / Maintenance Head"},
                ]
            },
            2: {
                "name": "Execute a Low-Cost Pilot", "duration": "Next 6 Months",
                "actions": [
                    {"title": 'Select a "Cloud Native" IoT Platform', "driver_ref": "Driver 2",
                     "description": "Choose a scalable, cloud-based IoT platform that requires zero on-premise servers, with a clear pay-per-service pricing model.",
                     "owner": "IT Head"},
                    {"title": '"Pay-As-You-Go" Pilot Project', "driver_ref": "Driver 1",
                     "description": "Based on your simulation, launch a small pilot on just one or two machines using the pay-per-service model of your chosen cloud platform. Track every rupee spent against the value generated.",
                     "owner": "Production Head / IT Head"},
                ]
            },
            3: {
                "name": "Scale Affordably", "duration": "12+ Months",
                "actions": [
                    {"title": '"Scalable Unit" Cost Model', "driver_ref": "Driver 3",
                     "description": "Using data from the successful pilot, calculate the exact cost to add one more 'unit' (e.g., one machine, one production line) to your IoT system — creating a predictable, scalable cost model for future expansion.",
                     "owner": "Finance Head"},
                    {"title": "Greenlight Future Phases Based on Proven ROI", "driver_ref": "All Drivers",
                     "description": "Make it a formal company policy that the next phase of the IoT rollout will only be funded once the previous phase has demonstrated a positive return on investment, ensuring the project pays for its own growth.",
                     "owner": "Director / CEO"},
                ]
            },
        },
    },
    13: {
        "name": "Compliance with Sector-Specific Regulations",
        "drivers": [
            "Confidence of customers in Internet transactions",
            "Robust Cybersecurity Measures",
            "Rapid deployment through Cloud IoT",
            "Change of organizational culture through decentralization",
            "Employee acceptance by motivation and incentives",
        ],
        "root_cause_template": (
            "The challenge of maintaining compliance with sector-specific regulations (e.g., from MPCB, BIS) is "
            "significantly influenced by both external customer perceptions and internal organizational structure. "
            "A lack of demonstrable, secure data practices erodes customer trust, while a centralized, slow-moving "
            "culture prevents the agile adoption of new compliance requirements."
        ),
        "strategic_goal": "To build a secure, agile, and transparent operational framework that ensures continuous regulatory compliance.",
        "phases": {
            1: {
                "name": "Secure the Foundation", "duration": "First 3 Months",
                "actions": [
                    {"title": "Deploy a Cloud-Based Compliance Dashboard", "driver_ref": "Driver 2 & 3",
                     "description": "Use a secure cloud platform to create a simple dashboard tracking key compliance metrics (e.g., emissions data, quality test results), providing a single secure source of truth for audits.",
                     "owner": "IT Head"},
                    {"title": "Appoint Compliance 'Point Persons'", "driver_ref": "Driver 4",
                     "description": "Decentralize responsibility by designating one person in each key department (Production, Warehouse) as the Compliance Point Person, responsible for reporting data for their area.",
                     "owner": "Director"},
                ]
            },
            2: {
                "name": "Build Transparency and Motivate Teams", "duration": "Next 6 Months",
                "actions": [
                    {"title": '"Customer Compliance Portal"', "driver_ref": "Driver 1",
                     "description": "Provide key B2B customers with secure, read-only access to a section of your compliance dashboard relevant to their products, proactively building immense confidence in your operations.",
                     "owner": "Sales Head"},
                    {"title": "Team-Based Compliance Incentive", "driver_ref": "Driver 5",
                     "description": "Launch a quarterly recognition program rewarding the department with the best compliance record (most accurate reporting, zero issues in internal checks) with team recognition or a small bonus.",
                     "owner": "HR Manager / Director"},
                ]
            },
            3: {
                "name": "Embed Compliance into the Culture", "duration": "12+ Months",
                "actions": [
                    {"title": "Automate Data Reporting", "driver_ref": "Driver 2 & 3",
                     "description": "Work towards fully automating the data feed from IoT sensors directly to the cloud compliance dashboard, reducing human error and providing real-time tamper-proof data for auditors and customers.",
                     "owner": "IT Head / Director"},
                    {"title": "Link Compliance to Performance Reviews", "driver_ref": "Driver 4 & 5",
                     "description": "Include compliance-related responsibilities in formal performance reviews for departmental Point Persons and their teams, solidifying the cultural shift.",
                     "owner": "HR Manager"},
                ]
            },
        },
    },
    14: {
        "name": "Lack of Regulations and Standards",
        "drivers": [
            "Top management support and Participation",
            "Robust Cybersecurity Measures",
            "Public advisor system",
            "Integrated Systems Across Departments and Suppliers",
            "Cloud-Based IoT Solutions",
            "Voluntary Third-Party Audits and Certifications",
        ],
        "root_cause_template": (
            "Operating in a rapidly evolving technological field with an unclear legal landscape creates significant "
            "business risk. Our analysis shows that this uncertainty is best countered by proactively adopting "
            "internationally recognized standards and proving adherence through robust systems and audits. This "
            "requires strong top-down commitment to build a secure, integrated, and transparent ecosystem that can "
            "withstand legal scrutiny and earn customer trust."
        ),
        "strategic_goal": "To build a legally defensible and trustworthy digital operation by adopting and validating best-in-class standards for governance and security.",
        "phases": {
            1: {
                "name": "Establish Governance & Expert Guidance", "duration": "First 3 Months",
                "actions": [
                    {"title": 'Form a "Digital Governance Council"', "driver_ref": "Driver 1",
                     "description": "The Director must create and lead a council to formally take ownership of all technology-related legal and standards issues.",
                     "owner": "Director / CEO"},
                    {"title": "Engage a Technology Law Advisor", "driver_ref": "Driver 3",
                     "description": "Onboard a legal expert specializing in technology and data privacy (like India's DPDPA) to act as a public advisor to the new council, providing expert guidance on which standards to adopt.",
                     "owner": "Digital Governance Council"},
                ]
            },
            2: {
                "name": "Implement Secure & Auditable Systems", "duration": "Next 6 Months",
                "actions": [
                    {"title": 'Select a "Certified Cloud" Platform', "driver_ref": "Driver 5",
                     "description": "Migrate key IoT workloads to a major cloud provider (e.g., AWS, Azure) that holds multiple international security and compliance certifications (ISO 27001, SOC 2), inheriting a secure, auditable foundation.",
                     "owner": "IT Head"},
                    {"title": '"Secure Data Traceability" Project', "driver_ref": "Driver 2 & 4",
                     "description": "Use your cloud platform to create an integrated system that securely logs all data access and sharing events between your departments and one key supplier, creating a clear audit trail for both security and compliance.",
                     "owner": "IT Head / Supply Chain Head"},
                ]
            },
            3: {
                "name": "Validate and Build Trust", "duration": "12+ Months",
                "actions": [
                    {"title": "Undergo a Voluntary ISO 27001 Audit", "driver_ref": "Driver 6",
                     "description": "Hire a certified third-party auditing firm to conduct an audit of your cybersecurity practices against the ISO 27001 standard, providing an unbiased assessment of your security posture.",
                     "owner": "Director / IT Head"},
                    {"title": "Publicize Your Certification", "driver_ref": "All Drivers",
                     "description": "Once certified, make it a central part of your marketing and sales conversations. Promoting this credible third-party validation is the most powerful way to build legal and commercial trust with customers and partners.",
                     "owner": "Sales & Marketing Head"},
                ]
            },
        },
    },
    15: {
        "name": "Customers are hesitant to share data",
        "drivers": [
            "Employee acceptance by motivation and incentives",
            "Public advisor system",
            "Continued specialized skills training",
            "Robust Cybersecurity Measures",
            "Customized Solutions for Existing Setups",
        ],
        "root_cause_template": (
            "While customer hesitation appears to be an external issue, our analysis indicates it is significantly "
            "correlated with a set of internal factors. The lack of demonstrated internal expertise, robust security, "
            "and tailored solutions creates a perception of risk for your customers, making them reluctant to share "
            "their sensitive operational data."
        ),
        "strategic_goal": "To build external customer trust by demonstrating internal excellence, security, and expertise.",
        "phases": {
            1: {
                "name": "Building the Internal Foundation", "duration": "First 3 Months",
                "actions": [
                    {"title": '"IoT Champions" Program', "driver_ref": "Driver 1 & 3",
                     "description": "Identify 3-4 key employees and provide them with specialized IoT and data security training. Motivate them with a small incentive or bonus for becoming the company's certified experts, building a core of internal knowledge.",
                     "owner": "HR Manager / Director"},
                    {"title": "Implement Foundational Cybersecurity Measures", "driver_ref": "Driver 4",
                     "description": "Conduct a security audit of your current systems. Implement and document essential measures like multi-factor authentication (MFA) for all data access and encryption for stored data, creating a provable security baseline.",
                     "owner": "IT Head"},
                ]
            },
            2: {
                "name": "Creating Proof and Customizing Solutions", "duration": "Next 6 Months",
                "actions": [
                    {"title": "Showcase Your Certified Experts", "driver_ref": "Driver 3",
                     "description": "When meeting with clients, introduce your newly trained IoT Champions. Having internal certified experts answer technical and security questions directly builds far more trust than relying on an external vendor.",
                     "owner": "Sales Head"},
                    {"title": '"System Harmony" Audit', "driver_ref": "Driver 5",
                     "description": "For a key potential client, offer a free audit to show exactly how your IoT solution can be customized to integrate seamlessly with their existing machinery and software, demonstrating you understand their unique setup.",
                     "owner": "Production Head"},
                ]
            },
            3: {
                "name": "Externalizing Trust & Establishing Authority", "duration": "12+ Months",
                "actions": [
                    {"title": "Form a Customer Advisory Board", "driver_ref": "Driver 2",
                     "description": "Invite 3-5 of your most valued clients to form a Customer Advisory Board. Meet quarterly to discuss their data concerns and get their input on your service roadmap, turning customers into partners.",
                     "owner": "Director / CEO"},
                    {"title": "Publish a Joint Case Study", "driver_ref": "All Drivers",
                     "description": "Work with a customer from your advisory board to publish a case study highlighting how your trained employees, robust security, and customized solution helped them achieve a specific goal. This external validation convinces new, hesitant customers.",
                     "owner": "Marketing Head"},
                ]
            },
        },
    },
}


# ── Low-level API callers ─────────────────────────────────────────────────────

def _messages_to_gemini_contents(messages: List[Dict[str, str]]) -> List[Dict]:
    contents = []
    system_text = None
    for msg in messages:
        role = msg["role"]
        text = msg["content"]
        if role == "system":
            system_text = text
            continue
        gemini_role = "model" if role == "assistant" else "user"
        if system_text and gemini_role == "user":
            text = f"{system_text}\n\n{text}"
            system_text = None
        contents.append({"role": gemini_role, "parts": [{"text": text}]})
    return contents


async def _call_gemini_raw(messages, temperature=AI_TEMPERATURE, max_tokens=AI_MAX_TOKENS):
    url = f"{GEMINI_API_URL}/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    contents = _messages_to_gemini_contents(messages)
    payload = {"contents": contents, "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens}}
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, timeout=AI_TIMEOUT)
        response.raise_for_status()
        return response.json()


async def _call_openrouter_raw(messages, temperature=AI_TEMPERATURE, max_tokens=AI_MAX_TOKENS):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": OPENROUTER_SITE_URL,
        "X-Title": OPENROUTER_SITE_NAME,
    }
    payload = {"model": OPENROUTER_MODEL, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}
    async with httpx.AsyncClient() as client:
        response = await client.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=AI_TIMEOUT)
        response.raise_for_status()
        return response.json()


async def _call_ai(messages, temperature=AI_TEMPERATURE, max_tokens=AI_MAX_TOKENS):
    for attempt in range(RATE_LIMIT_RETRIES):
        try:
            if AI_PROVIDER == "gemini":
                data = await _call_gemini_raw(messages, temperature, max_tokens)
                candidate = data.get("candidates", [{}])[0]
                text = candidate.get("content", {}).get("parts", [{}])[0].get("text", "")
                finish = candidate.get("finishReason", "STOP")
                normalised = "length" if finish in ("MAX_TOKENS", "LENGTH") else "stop"
            else:
                data = await _call_openrouter_raw(messages, temperature, max_tokens)
                choice = data.get("choices", [{}])[0]
                text = choice.get("message", {}).get("content", "")
                finish = choice.get("finish_reason", "stop")
                normalised = "length" if finish == "length" else "stop"
            return text, normalised
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                wait = RATE_LIMIT_BACKOFF[min(attempt, len(RATE_LIMIT_BACKOFF) - 1)]
                logger.warning("Rate limit (429) from %s. Waiting %ds before retry %d/%d...", AI_PROVIDER, wait, attempt + 1, RATE_LIMIT_RETRIES)
                await asyncio.sleep(wait)
                if attempt == RATE_LIMIT_RETRIES - 1:
                    raise
            else:
                raise
    return "", "stop"


def _active_api_key():
    return GEMINI_API_KEY if AI_PROVIDER == "gemini" else OPENROUTER_API_KEY


# ── Score helpers ─────────────────────────────────────────────────────────────

def _interpret_indicator(value: float, lower_is_better: bool = True) -> str:
    if lower_is_better:
        if value <= 1.5: return "Very Low (good)"
        if value <= 3.5: return "Low"
        if value <= 5.5: return "Moderate"
        if value <= 7.5: return "High"
        return "Critically High"
    else:
        if value >= 8.5: return "Strong"
        if value >= 6.0: return "Good"
        if value >= 4.0: return "Moderate"
        if value >= 2.0: return "Low"
        return "Very Low"


def _top_cost_factors_for_barrier(barrier_idx: int, cost_inputs: Optional[Dict]) -> str:
    if not cost_inputs: return ""
    weights = COST_BARRIER_WEIGHTS[barrier_idx]
    cost_vals = list(cost_inputs.values()) if isinstance(cost_inputs, dict) else []
    scored = []
    for j, (label, w) in enumerate(zip(COST_FACTOR_LABELS, weights)):
        if w > 0 and j < len(cost_vals):
            scored.append((label, w * float(cost_vals[j])))
    scored.sort(key=lambda x: x[1], reverse=True)
    top = [label for label, _ in scored[:3] if scored]
    return f"Top cost drivers: {', '.join(top)}." if top else ""


def _top_kpi_factors_for_barrier(barrier_idx: int, kpi_inputs: Optional[Dict]) -> str:
    if not kpi_inputs: return ""
    weights = KPI_BARRIER_WEIGHTS[barrier_idx]
    kpi_vals = list(kpi_inputs.values()) if isinstance(kpi_inputs, dict) else []
    impacted = [label for j, (label, w) in enumerate(zip(KPI_FACTOR_LABELS, weights))
                if w >= 2 and j < len(kpi_vals) and float(kpi_vals[j]) == 1]
    return f"KPIs most impacted: {', '.join(impacted[:4])}." if impacted else ""


# ── Knowledge base context builders ──────────────────────────────────────────

def _build_analysis_knowledge_context(barrier_num: int) -> str:
    """Return drivers + root cause template for a barrier (for analysis prompts)."""
    kb = BARRIER_KNOWLEDGE_BASE.get(barrier_num)
    if not kb:
        return ""
    drivers_str = "\n".join(f"  - {d}" for d in kb["drivers"])
    return (
        f"ISRI Knowledge Base for Barrier {barrier_num}:\n"
        f"  Correlated Drivers:\n{drivers_str}\n"
        f"  Root Cause Framework: {kb['root_cause_template']}\n"
    )


def _build_roadmap_knowledge_context(barrier_num: int) -> str:
    """Return full knowledge base entry formatted for the roadmap prompt."""
    kb = BARRIER_KNOWLEDGE_BASE.get(barrier_num)
    if not kb:
        return ""
    drivers_str = "\n".join(f"  - {d}" for d in kb["drivers"])
    lines = [
        f"ISRI KNOWLEDGE BASE FOR BARRIER {barrier_num}: {kb['name']}",
        f"  Strategic Goal: {kb['strategic_goal']}",
        f"  Correlated Drivers:\n{drivers_str}",
        f"  Root Cause Template: {kb['root_cause_template']}",
    ]
    for phase_num in [1, 2, 3]:
        phase = kb["phases"][phase_num]
        lines.append(f"\n  Phase {phase_num} ({phase['duration']}): {phase['name']}")
        for action in phase["actions"]:
            lines.append(
                f'    - "{action["title"]}" ({action["driver_ref"]}): {action["description"]} [Owner: {action["owner"]}]'
            )
    return "\n".join(lines)


# ── Generation retry wrapper ──────────────────────────────────────────────────

async def _generate_with_retry(prompt, temperature=AI_TEMPERATURE, max_tokens=AI_MAX_TOKENS, label="chunk"):
    messages = [{"role": "user", "content": prompt}]
    accumulated_text = ""
    for attempt in range(1 + MAX_CONTINUATION_RETRIES):
        try:
            chunk_text, finish_reason = await _call_ai(messages, temperature=temperature, max_tokens=max_tokens)
        except Exception as e:
            logger.error("API call failed for %s (attempt %d): %s", label, attempt + 1, e)
            if accumulated_text:
                return accumulated_text
            raise
        logger.info("[%s] attempt=%d  finish_reason=%s  chunk_len=%d chars", label, attempt + 1, finish_reason, len(chunk_text))
        accumulated_text += chunk_text
        if finish_reason != "length":
            break
        logger.info("Response truncated for %s (attempt %d/%d). Requesting continuation...", label, attempt + 1, 1 + MAX_CONTINUATION_RETRIES)
        messages = [
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": accumulated_text},
            {"role": "user", "content": "Your previous response was cut off. Continue EXACTLY where you left off. Do NOT repeat any content already provided. Do NOT add any preamble — just continue the report."},
        ]
    else:
        logger.warning("Response for %s still truncated after %d retries.", label, MAX_CONTINUATION_RETRIES)
    return accumulated_text


def _validate_barriers_present(text, barrier_numbers):
    """Check that each barrier number appears in the text via multiple patterns."""
    missing = []
    for n in barrier_numbers:
        # Match "Barrier 1", "2.1", "Barrier1", section headings with the number
        pattern = rf"(?:[Bb]arrier\s*{n}\b|##\s*2\.{n}\b|\b2\.{n}\b)"
        if not re.search(pattern, text):
            missing.append(n)
    return missing


# ── Comprehensive Barrier Analysis ───────────────────────────────────────────

async def generate_comprehensive_barrier_analysis(
    company_details: Dict,
    barrier_scores: Dict[str, Dict],
    impact_values: Dict[str, Dict],
) -> str:
    if not _active_api_key():
        return f"AI API key for provider '{AI_PROVIDER}' is not configured."

    current_time = datetime.datetime.now().strftime("%B %d, %Y — %I:%M %p IST")
    barrier_groups = [[1,2,3],[4,5,6],[7,8,9],[10,11,12],[13,14,15]]
    parts = []

    part1 = await _generate_analysis_part(company_details, barrier_scores, impact_values, barrier_groups[0], current_time, include_summary=True, include_conclusion=False)
    parts.append(part1)

    for i, group in enumerate(barrier_groups[1:], 1):
        is_last = (i == len(barrier_groups) - 1)
        part = await _generate_analysis_part(company_details, barrier_scores, impact_values, group, current_time, include_summary=False, include_conclusion=is_last)
        parts.append(part)

    return "\n\n---\n\n".join(parts)


def _build_barrier_sections(barrier_numbers, barrier_scores):
    sections = []
    for i in barrier_numbers:
        bk = f"barrier{i}"
        bd = barrier_scores[bk]
        section = f"### Barrier {i}: {bd['name']}\n**Overall Score:** {bd['total']:.2f} / 10  |  **Severity:** {bd['level']}\n**Indicator Breakdown:**\n"
        for ind_name, ind_score in bd['indicators'].items():
            label = ind_name.replace('_', ' ').title()
            section += f"- {label}: {ind_score:.2f}  [{_interpret_indicator(ind_score)}]\n"
        sections.append(section)
    return "\n".join(sections)


async def _generate_analysis_part(
    company_details, barrier_scores, impact_values,
    barrier_numbers, current_time, include_summary=False, include_conclusion=False,
):
    barrier_data_text = _build_barrier_sections(barrier_numbers, barrier_scores)
    barrier_names = ", ".join(f"Barrier {n}" for n in barrier_numbers)
    label = f"barriers {barrier_numbers[0]}-{barrier_numbers[-1]}"
    company_name = company_details.get('company_name', 'N/A')
    industry = company_details.get('industry', 'N/A')
    employees = company_details.get('num_employees', 'N/A')
    revenue = company_details.get('annual_revenue', 'N/A')

    # Build knowledge base context for this group
    kb_context = "\n\n".join(_build_analysis_knowledge_context(n) for n in barrier_numbers)

    # Build sorted barrier list for executive summary
    all_barriers_summary = ""
    if include_summary:
        sorted_barriers = sorted(
            [(k, v) for k, v in barrier_scores.items()],
            key=lambda x: x[1]['total'], reverse=True
        )
        all_barriers_summary = "\n".join(
            f"  - Barrier {k.replace('barrier','')}: {v['name']} — Score {v['total']:.2f}/10 — {v['level']}"
            for k, v in sorted_barriers
        )

    stop_instruction = (
        f"\nCRITICAL RULES:\n"
        f"1. Produce a COMPLETE analysis for ALL barriers listed: {barrier_names}.\n"
        f"2. Do NOT skip any barrier.\n"
        f"3. Do NOT include barriers outside {barrier_numbers[0]}-{barrier_numbers[-1]}.\n"
        f"4. Use the ISRI Knowledge Base context to write specific, framework-aligned root causes and recommendations.\n"
        f"5. Do NOT include generic IoT advice — all content must be ISRI-framework specific.\n"
    )

    if include_summary:
        prompt = f"""Report Generation Date: {current_time}

You are writing an official ISRI (Indian SME Readiness Index) Barrier Analysis Report for {company_name}.

**Company Profile:**
- Company: {company_name}
- Industry: {industry}
- Employees: {employees}
- Annual Revenue: Rs {revenue} Cr

**All Barrier Scores (for Executive Summary):**
{all_barriers_summary}

---

## REPORT FORMAT — Follow this EXACTLY

# Barrier Analysis Report
## IoT Adoption Readiness Assessment

**Prepared for:** {company_name} ({industry})
**Employees:** {employees}  |  **Annual Revenue:** Rs {revenue} Cr
**Report Date:** {current_time}

---

## 1. Executive Summary

Write 200-250 words covering:
- A paragraph about {company_name}, its industry, size, and overall IoT readiness posture
- **Key Findings:** group barriers by severity level using this EXACT format:
  - **Highest Barriers (Critically High / High):**
    - Barrier Name (X.XX/10) – one-line description of the core problem
  - **Moderate Barriers:**
    - Barrier Name (X.XX/10) – one-line description
  - **Lowest Barriers:**
    - Barrier Name (X.XX/10) – one-line description
- Close with an italicised statement: *Overall IoT Readiness: [level] — [company] must prioritize [single call to action].*

---

## 2. Detailed Barrier Analysis & Recommendations

For each barrier below, use EXACTLY this format (you MUST include "Barrier N:" in every heading):

### 2.N Barrier N: [Barrier Name] (Score: X.XX/10 – [SEVERITY])

**Root Causes:**
- **[Cause name]:** [2-sentence explanation referencing the specific indicator scores shown in the data AND drawing from the ISRI knowledge base root cause framework]
- **[Cause name]:** [explanation]

**Impact:**
- **[Impact category]:** [specific business consequence for a {industry} company of {employees} employees and Rs {revenue} Cr revenue]
- **[Impact category]:** [consequence]

**Recommendations:**
- **[Action name from ISRI framework]:** [specific step adapted to {company_name}'s context, referencing the relevant correlated driver]
- **[Action name]:** [step]

---

[repeat for every barrier in the group]

**ISRI Knowledge Base Context (use this to write Root Causes and Recommendations):**
{kb_context}

**Barrier Data:**
{barrier_data_text}
{stop_instruction}"""

    elif include_conclusion:
        prompt = f"""Continue the ISRI Barrier Analysis Report for {company_name} ({industry}, {employees} employees, Rs {revenue} Cr revenue).

## 2. Detailed Barrier Analysis & Recommendations (continued)

For each barrier below, use EXACTLY this format:

### 2.N [Barrier Name] (Score: X.XX/10 – [SEVERITY])

**Root Causes:**
- **[Cause name]:** [explanation referencing indicator scores AND ISRI knowledge base root cause]
- **[Cause name]:** [explanation]

**Impact:**
- **[Impact category]:** [specific business consequence for {company_name}]
- **[Impact category]:** [consequence]

**Recommendations:**
- **[Action name from ISRI framework]:** [specific step adapted to {company_name}'s context]
- **[Action name]:** [step]

---

[repeat for every barrier in the group]

After completing all barriers in the group, add a brief closing paragraph (2-3 sentences) summarising the overall readiness posture of {company_name} based on the barrier scores above. Do NOT include any strategic roadmap, phased plans, or recommendations lists — those are contained in the separate Strategic Roadmap Report.

**ISRI Knowledge Base Context:**
{kb_context}

**Barrier Data:**
{barrier_data_text}
{stop_instruction}"""

    else:
        prompt = f"""Continue the ISRI Barrier Analysis Report for {company_name} ({industry}).

## 2. Detailed Barrier Analysis & Recommendations (continued)

For each barrier below, use EXACTLY this format:

### 2.N [Barrier Name] (Score: X.XX/10 – [SEVERITY])

**Root Causes:**
- **[Cause name]:** [explanation referencing indicator scores AND ISRI knowledge base root cause]
- **[Cause name]:** [explanation]

**Impact:**
- **[Impact category]:** [specific business consequence for {company_name}]
- **[Impact category]:** [consequence]

**Recommendations:**
- **[Action name from ISRI framework]:** [specific step adapted to {company_name}'s context]
- **[Action name]:** [step]

---

[repeat for every barrier in the group]

**ISRI Knowledge Base Context:**
{kb_context}

**Barrier Data:**
{barrier_data_text}
{stop_instruction}"""

    for chunk_attempt in range(1 + MAX_CHUNK_RETRIES):
        try:
            result = await _generate_with_retry(prompt, label=label)
        except httpx.HTTPStatusError as e:
            return f"API HTTP error ({label}): {e.response.status_code}"
        except Exception as e:
            return f"Unexpected error: {e}"

        missing = _validate_barriers_present(result, barrier_numbers)
        if not missing:
            return result

        logger.warning("Missing barriers %s in response for %s (attempt %d/%d).", missing, label, chunk_attempt + 1, 1 + MAX_CHUNK_RETRIES)
        if chunk_attempt < MAX_CHUNK_RETRIES:
            prompt = f"""You MUST write a complete ISRI analysis for EACH of these barriers for {company_name}:

REQUIRED BARRIERS: {barrier_names} (exactly {len(barrier_numbers)} barriers — do not skip any)

For each barrier:
### 2.N [Barrier Name] (Score: X.XX/10 – [Severity])
**Root Causes:**
- **[Cause]:** [explanation]
**Impact:**
- **[Category]:** [consequence]
**Recommendations:**
- **[Action]:** [step]

**Data:**
{barrier_data_text}

ISRI Knowledge Base:
{kb_context}

STOP after Barrier {barrier_numbers[-1]}."""

    return result


# ── Strategic Roadmap ─────────────────────────────────────────────────────────

async def generate_strategic_roadmap(
    company_details: Dict,
    top_barriers: List[tuple],
    barrier_scores: Dict[str, Dict],
    cost_factor_inputs: Optional[Dict] = None,
    kpi_factor_inputs: Optional[Dict] = None,
) -> str:
    if not _active_api_key():
        return f"AI API key for provider '{AI_PROVIDER}' is not configured."

    company_name = company_details.get('company_name', 'N/A')
    industry = company_details.get('industry', 'N/A')
    employees = company_details.get('num_employees', 'N/A')
    revenue = company_details.get('annual_revenue', 'N/A')

    # Build context per barrier
    barrier_sections = []
    for rank, (barrier_key, impact_data) in enumerate(top_barriers, 1):
        barrier_idx = int(barrier_key.replace("barrier", "")) - 1
        barrier_num = barrier_idx + 1
        barrier_data = barrier_scores[barrier_key]

        # Indicator breakdown
        indicator_lines = []
        for ind_name, ind_score in barrier_data["indicators"].items():
            label = ind_name.replace("_", " ").title()
            indicator_lines.append(f"  - {label}: {ind_score:.2f} [{_interpret_indicator(ind_score)}]")

        cost_line = _top_cost_factors_for_barrier(barrier_idx, cost_factor_inputs)
        kpi_line = _top_kpi_factors_for_barrier(barrier_idx, kpi_factor_inputs)

        kb_context = _build_roadmap_knowledge_context(barrier_num)

        section = f"""
=== PRIORITY {rank}: BARRIER {barrier_num} ===
Barrier Name: {barrier_data['name']}
Overall Score: {barrier_data['total']:.2f} / 10
Severity: {barrier_data['level']}
Impact Value: {impact_data['impact_value']:.4f}

Indicator Scores:
{chr(10).join(indicator_lines)}

{cost_line}
{kpi_line}

{kb_context}
"""
        barrier_sections.append(section)

    prompt = f"""You are writing an official ISRI Strategic Roadmap Report for the top 3 critical barriers of {company_name}.

**Company:**
- Name: {company_name}
- Industry: {industry}
- Employees: {employees}
- Annual Revenue: Rs {revenue} Cr

---

## CRITICAL INSTRUCTIONS

1. Produce the roadmap for ALL 3 barriers below — do NOT skip any.
2. Use the ISRI Knowledge Base content for each barrier as the framework — adapt the action descriptions specifically to {company_name}'s industry ({industry}), size ({employees} employees), and revenue (Rs {revenue} Cr).
3. Maintain the EXACT format shown below — including the 2-column phase table.
4. Do NOT write generic IoT advice. Every action must reference the specific ISRI drivers and framework.
5. Adapt ₹ amounts to be realistic for a company with Rs {revenue} Cr revenue.

---

## EXACT REPORT FORMAT (replicate this EXACTLY for each barrier):

---

*Greetings from the Indian SME Readiness Index.*

*Disclaimer: This roadmap has been generated using a proprietary framework developed from a comprehensive industry survey. The correlations between barriers and drivers are statistically derived from the survey responses of Indian SMEs. Please treat this as a strategic guide to be adapted with professional judgment.*

### Detailed Analysis & Action Plan

#### Barrier [N]: [Barrier Name]

- **Barrier Score:** [X.XX] / 10
- **Severity:** [LEVEL]
- **Impact Value:** [value]

**Root Cause Analysis:** [2-3 sentences: use the ISRI root cause template from the knowledge base, adapted to {company_name}'s actual indicator scores and {industry} context. Reference specific indicator scores where relevant.]

**Correlated Drivers:**
- [Driver 1 from knowledge base]
- [Driver 2]
- [Driver N]

| Phase | Actions |
|---|---|
| **Strategic Goal** | [strategic goal from knowledge base, adapted to {company_name} context] |
| **Phase 1 ([duration]): [Phase Name]** | **1. "[Action Title]" ([Driver ref from knowledge base]):** [description adapted to {company_name}]. **Owner:** [role]<br><br>**2. "[Action Title]" ([Driver ref]):** [description adapted to company]. **Owner:** [role] |
| **Phase 2 ([duration]): [Phase Name]** | **1. "[Action Title]" ([Driver ref]):** [description]. **Owner:** [role]<br><br>**2. "[Action Title]" ([Driver ref]):** [description]. **Owner:** [role] |
| **Phase 3 ([duration]): [Phase Name]** | **1. "[Action Title]" ([Driver ref]):** [description]. **Owner:** [role]<br><br>**2. "[Action Title]" ([Driver ref]):** [description]. **Owner:** [role] |

*We are committed to continuous improvement. We welcome your feedback on this roadmap to help us make it even more tailored and effective for your specific business needs.*

---

[Repeat the ENTIRE format above for Barrier 2 and Barrier 3]

---

## BARRIER DATA AND KNOWLEDGE BASE

{chr(10).join(barrier_sections)}

---

REMINDER: Use the ISRI Knowledge Base action titles, driver references, and phase names EXACTLY as provided, but adapt the descriptions to make them specific to {company_name} ({industry}, {employees} employees, Rs {revenue} Cr revenue).
"""

    try:
        return await _generate_with_retry(prompt, temperature=0.55, label="strategic roadmap")
    except httpx.HTTPStatusError as e:
        return f"API HTTP error: {e.response.status_code} — {e.response.text}"
    except httpx.RequestError as e:
        return f"API request error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"
