## Detailed Formulas

### Barrier 1 – Skills & Training Deficiency

| # | Title / Description                                      | Variable Name                        | Formula / Scaling Logic                                      |
|---|------------------------------------------------------------------|--------------------------------------|--------------------------------------------------------------|
| i   | Number of training programs offered per year (≥5 = good)        | `num_training_programs`              | (1 − input/5) × 0.2 × 10                                     |
| ii  | % of employees trained in digital technologies                  | `pct_employees_trained`              | (1 − input) × 0.5 × 10                                       |
| iii | Budget for training (% of total payroll)                        | `pct_budget_training_of_payroll`     | (1 − input/2.5) × 0.3 × 10                                   |

### Barrier 2 – Employee Resistance & Turnover

| # | Title / Description                                      | Variable Name                        | Formula                                                      |
|---|------------------------------------------------------------------|--------------------------------------|--------------------------------------------------------------|
| i   | Employee turnover rate after IoT initiatives (20% = alarming)   | `employee_turnover_rate_pct`         | input/20 × 0.4 × 10                                          |
| ii  | % employees expressing resistance in surveys                    | `pct_employees_resisting`            | (1 − input) × 0.35 × 10                                      |
| iii | Number of feedback sessions/meetings per year (12 = good)       | `num_feedback_sessions`              | (1 − input/12) × 0.25 × 10                                   |

### Barrier 3 – Digital Comfort & Adoption

| # | Title                                                            | Variable Name                              | Formula                                                      |
|---|--------------------------------------------------------------------------|--------------------------------------------|--------------------------------------------------------------|
| i   | Number of digital skills workshops attended (5 = healthy)               | `num_digital_skills_workshops`             | (1 − input/5) × 0.2 × 10                                     |
| ii  | % employees comfortable using digital tools                             | `pct_comfortable_digital_tools`            | (1 − input) × 0.4 × 10                                       |
| iii | Adoption rate of new digital tools/platforms (%)                        | `adoption_rate_new_digital_tools_pct`      | (1 − input/100) × 0.4 × 10                                   |

### Barrier 4 – Training Effectiveness & Investment

| # | Title                                                            | Variable Name                              | Formula                                                      |
|---|--------------------------------------------------------------------------|--------------------------------------------|--------------------------------------------------------------|
| i   | Training expenditure (% of total operational costs)                     | `pct_training_expenditure_of_op_costs`     | (1 − input/5) × 0.4 × 10                                     |
| ii  | Avg training hours per employee per year (40 h = norm)                  | `avg_training_hours_per_employee`          | input/40 × 0.3 × 10                                          |
| iii | ROI on training programs (% productivity improvement)                   | `roi_training_programs_pct`                | (1 − input/100) × 0.3 × 10                                   |

### Barrier 5 – Knowledge Management & Sharing

| # | Title                                                            | Variable Name                              | Formula                                                      |
|---|--------------------------------------------------------------------------|--------------------------------------------|--------------------------------------------------------------|
| i   | Number of internal knowledge-sharing sessions (24/yr good)              | `num_knowledge_sharing_sessions`           | (1 − input/24) × 0.3 × 10                                    |
| ii  | % employees with access to centralized KMS                              | `pct_employees_access_kms`                 | (1 − input/100) × 0.4 × 10                                   |
| iii | Frequency of KMS updates (Weekly=0.25, Monthly=0.5, Quarterly=0.75)     | `freq_updates_kms`                         | input × 0.3 × 10                                             |

### Barrier 6 – Regulatory & Compliance Risks

| # | Title                                                            | Variable Name                              | Formula                                                      |
|---|--------------------------------------------------------------------------|--------------------------------------------|--------------------------------------------------------------|
| i   | Number of non-compliance incidents/penalties (5/yr = crisis)            | `num_non_compliance_incidents`             | input/5 × 0.4 × 10                                           |
| ii  | % IoT projects delayed due to regulatory challenges                     | `pct_projects_delayed_regulatory`          | input/100 × 0.4 × 10                                         |
| iii | Time to achieve compliance with new IoT regulations (days)              | `time_to_achieve_compliance_days`          | input/180 × 0.2 × 10                                         |

### Barrier 7 – Lack of Standards & Interoperability

| # | Title                                                            | Variable Name                              | Formula                                                      |
|---|--------------------------------------------------------------------------|--------------------------------------------|--------------------------------------------------------------|
| i   | Number of industry standards adopted (10 = healthy)                     | `num_industry_standards_adopted`           | (1 − input/10) × 0.35 × 10                                   |
| ii  | % IoT devices conforming to reference architectures                     | `pct_iot_devices_conforming`               | (1 − input/50) × 0.4 × 10                                    |
| iii | % IoT projects delayed due to lack of standardized solutions            | `pct_projects_delayed_standardized_solutions` | input/100 × 0.25 × 10                                     |

### Barrier 8 – Infrastructure & Connectivity Issues

| # | Title                                                            | Variable Name                              | Formula                                                      |
|---|--------------------------------------------------------------------------|--------------------------------------------|--------------------------------------------------------------|
| i   | % work locations with stable internet (inverted)                        | `pct_internet_coverage`                    | (1 − input/100) × 0.3 × 10                                   |
| ii  | Average internet speed (Mbps) – 50 Mbps good                            | `avg_internet_speed_mbps`                  | (1 − input/50) × 0.2 × 10                                    |
| iii | Frequency of IT outages impacting IoT (8/month = crisis)                | `freq_it_infrastructure_outages_per_month` | input/8 × 0.5 × 10                                           |

### Barrier 9 – Funding & Financial Constraints

| # | Title                                                            | Variable Name                              | Formula                                                      |
|---|--------------------------------------------------------------------------|--------------------------------------------|--------------------------------------------------------------|
| i   | Loan application success/approval rate                                  | `pct_loan_approved`                        | (1 − input/5) × 0.4 × 10                                     |
| ii  | % projects delayed/canceled due to lack of funding                      | `pct_projects_delayed_lack_funding`        | input/100 × 0.4 × 10                                         |
| iii | Ratio of external funding to total project costs (%)                    | `ratio_external_funding_total_project_costs_pct` | (1 − input/100) × 0.2 × 10                         |

### Barrier 10 – Limited Business Impact / ROI

| # | Title                                                            | Variable Name                              | Formula                                                      |
|---|--------------------------------------------------------------------------|--------------------------------------------|--------------------------------------------------------------|
| i   | YoY revenue growth from IoT initiatives (20% good)                      | `yoy_revenue_growth_iot_pct`               | (1 − input/20) × 0.4 × 10                                    |
| ii  | Profit margin improvement after IoT (5% strong)                         | `profit_margin_improvement_iot_pct`        | (1 − input/5) × 0.4 × 10                                     |
| iii | Number of new revenue streams from IoT (3 = successful)                 | `num_new_revenue_streams_iot`              | (1 − input/3) × 0.2 × 10                                     |

### Barrier 11 – Vendor Dependency & Lock-in

| # | Title                                                            | Variable Name                              | Formula                                                      |
|---|--------------------------------------------------------------------------|--------------------------------------------|--------------------------------------------------------------|
| i   | % critical operations reliant on third-party vendors                    | `pct_critical_operations_reliant_vendor`   | input/100 × 0.4 × 10                                         |
| ii  | Number of vendor-related delays/disruptions per year                    | `num_vendor_delays_disruptions_per_year`   | (1 − (1 − input/5)) × 0.4 × 10                               |
| iii | Cost of vendor contracts (% of total op. expenses)                      | `cost_vendor_contracts_pct_op_expenses`    | input/100 × 0.2 × 10                                         |

### Barrier 12 – High Implementation & Maintenance Costs

| # | Title                                                            | Variable Name                              | Formula                                                      |
|---|--------------------------------------------------------------------------|--------------------------------------------|--------------------------------------------------------------|
| i   | % of total IT budget allocated to IoT                                   | `pct_it_budget_allocated_iot`              | input/100 × 0.4 × 10                                         |
| ii  | Annual O&M costs (% of total op. costs) – 5% crisis level               | `annual_maintenance_costs_pct_op_costs`    | (1 − (1 − input/5)) × 0.3 × 10                               |
| iii | Integration costs (% of total project cost)                             | `integration_costs_pct_total_project_cost` | input/100 × 0.3 × 10                                         |

### Barrier 13 – Regulatory Compliance Management

| # | Title                                                            | Variable Name                              | Formula                                                      |
|---|--------------------------------------------------------------------------|--------------------------------------------|--------------------------------------------------------------|
| i   | Number of regulatory violations/penalties (4/yr = crisis)               | `num_regulatory_violations_penalties`      | input/4 × 0.5 × 10                                           |
| ii  | % compliance audits passed without issues (inverted)                    | `pct_compliance_audits_passed_without_issues` | (1 − input/100) × 0.3 × 10                            |
| iii | Frequency of internal policy updates (Quarterly=0.5, Bi-annual=0.75, Annual=1.0) | `freq_updates_internal_policies`     | input × 0.5 × 10                                             |

### Barrier 14 – Standards & Framework Adoption

| # | Title                                                            | Variable Name                              | Formula                                                      |
|---|--------------------------------------------------------------------------|--------------------------------------------|--------------------------------------------------------------|
| ii  | % standards-compliant IoT devices (inverted)                            | `pct_standards_compliant_iot_devices`      | (1 − input/100) × 0.4 × 10                                   |
| iii | Number of industry-specific guidelines/frameworks implemented (10 good)| `num_industry_specific_guidelines_implemented` | (1 − input/10) × 0.6 × 10                            |

### Barrier 15 – Customer Data Privacy Concerns

| # | Title                                                            | Variable Name                              | Formula                                                      |
|---|--------------------------------------------------------------------------|--------------------------------------------|--------------------------------------------------------------|
| i   | % customers refusing to share data (survey-based)                       | `pct_customers_refuse_data`                | input/100 × 0.4 × 10                                         |
| ii  | Number of customer complaints/concerns on data sharing (25/yr = crisis) | `num_customer_complaints_data_sharing`     | input/25 × 0.35 × 10                                         |
| iii | % customer contracts with explicit data-sharing agreements (inverted)   | `pct_customer_contracts_explicit_data_sharing` | (1 − input/100) × 0.25 × 10                          |

---

Last updated: based on source document dated ~2025–2026  
Use for calculating **barrier risk scores** in IoT/digital adoption readiness assessments.