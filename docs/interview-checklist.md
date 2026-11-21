# Interview checklist

Before the interview, copy `inputs.example.yaml` to `inputs.yaml` and share the relevant questions with the people listed below.
During the interview, date the answers and leave any unanswered field empty so the report can identify what is missing and how to follow it up.
Build the report with `befund report SCAN_JSON --inputs inputs.yaml`.

## The organisation and the basics

- Which organisation name does the project lead want on the report (`organisation_name`)?
- Which three-letter currency code does finance use for the comparison (`currency`)?
- Which report language does the project lead need, English (`en`) or German (`de`) (`language`)?
- Which target profile has the IT lead chosen, `opendesk`, `nextcloud` or `generic` (`target_profile`)?
- On what date were the answers given (`as_of`)?
- Are the amounts invented for a demonstration (`amounts_are_invented`)?

## What Microsoft and other IT cost today

Record both annual amounts under `current_costs` and put every amount in quotes, using `"0"` for a confirmed zero.

- How much does finance pay for Microsoft licences each year (`current_costs.microsoft_licences_per_year`)?
- How much does finance spend each year on other IT that would continue in all three scenarios (`current_costs.other_it_per_year`)?

## Partial exit

Put both scenarios under `target_costs` and use `target_costs.partial_exit` for the partial exit.

- How many people would work on the new platform in the IT lead's partial exit plan (`target_costs.partial_exit.users`)?
- What annual cost does finance expect for Microsoft licences kept after parallel running (`target_costs.partial_exit.retained_microsoft_licences_per_year`)?
- What hosting charge per person per month has the provider given finance (`target_costs.partial_exit.hosting_per_user_per_month`)?
- What annual staff or service cost does the IT lead expect for operating the new platform (`target_costs.partial_exit.operations_per_year`)?
- What other recurring annual costs of the partial exit has finance identified (`target_costs.partial_exit.other_recurring_per_year`)?
- What one-time cost does the IT lead expect for carrying out the partial move (`target_costs.partial_exit.one_time_migration`)?
- How much does the IT lead expect to spend adapting applications for the partial move (`target_costs.partial_exit.application_adaptation`)?
- How much does finance expect to spend on external advice for the partial move (`target_costs.partial_exit.external_advice`)?
- How many training days per person do department heads expect (`target_costs.partial_exit.training_days_per_person`)?
- How much does finance expect a training day for one person to cost (`target_costs.partial_exit.training_day_rate`)?
- How many staff do department heads expect to attend training (`target_costs.partial_exit.training_staff`)?
- What total cost have finance and the departments assigned to work time lost during the partial move (`target_costs.partial_exit.productivity_loss`)?
- For how many months does finance expect to pay for both systems (`target_costs.partial_exit.parallel_running_months`)?

## Full exit

Use `target_costs.full_exit` for the full exit.

- How many people would work on the new platform in the IT lead's full exit plan (`target_costs.full_exit.users`)?
- What annual cost does finance expect for any Microsoft licences kept after parallel running (`target_costs.full_exit.retained_microsoft_licences_per_year`)?
- What hosting charge per person per month has the provider given finance (`target_costs.full_exit.hosting_per_user_per_month`)?
- What annual staff or service cost does the IT lead expect for operating the new platform (`target_costs.full_exit.operations_per_year`)?
- What other recurring annual costs of the full exit has finance identified (`target_costs.full_exit.other_recurring_per_year`)?
- What one-time cost does the IT lead expect for carrying out the full move (`target_costs.full_exit.one_time_migration`)?
- How much does the IT lead expect to spend adapting applications for the full move (`target_costs.full_exit.application_adaptation`)?
- How much does finance expect to spend on external advice for the full move (`target_costs.full_exit.external_advice`)?
- How many training days per person do department heads expect (`target_costs.full_exit.training_days_per_person`)?
- How much does finance expect a training day for one person to cost (`target_costs.full_exit.training_day_rate`)?
- How many staff do department heads expect to attend training (`target_costs.full_exit.training_staff`)?
- What total cost have finance and the departments assigned to work time lost during the full move (`target_costs.full_exit.productivity_loss`)?
- For how many months does finance expect to pay for both systems (`target_costs.full_exit.parallel_running_months`)?

## Software that runs only on Windows

Remove `null` and add one entry per application, or enter `[]` when the IT lead confirms there are none.

- Which applications can run only on Windows (`windows_only_software`)?
- Which name does the IT lead use for the application (`windows_only_software.name`)?
- How many people use it, according to the department heads (`windows_only_software.users`)?
- Does the software vendor offer a web version (`windows_only_software.vendor_has_web_version`)?

## Questions by workload

Enter whole numbers under `provided_counts` and use `true` or `false` under `confirmations`.

### Licences

- Has procurement reviewed the Microsoft licence contract terms (`licences.contract_terms_known`)?

### Directory

- Has the IT lead reviewed the current account list (`directory.account_list_reviewed`)?

### Mail

- Do other systems, such as scanners or business applications, send email through Microsoft (`mail.other_systems_send_mail`)?

### OneDrive

- Does your organisation share OneDrive files with people outside the organisation (`onedrive.external_sharing_in_use`)?

### SharePoint

- Does your organisation use any custom SharePoint solutions (`sharepoint.custom_solutions_in_use`)?

### Teams

- Do department heads or records managers require the Teams chat history to be kept (`teams.chat_history_must_be_kept`)?

### Office files

- How many files with extensions that allow macros has the IT lead counted (`.xlsm`, `.xltm`, `.xlam`, `.docm`, `.dotm`, `.pptm`, `.potm`) (`office_files.kind.macro`)?
- How many Access database files for records, forms or queries has the IT lead counted (`.accdb`, `.mdb`) (`office_files.kind.access`)?
- How many Publisher files used for page layout has the IT lead counted (`.pub`) (`office_files.kind.publisher`)?
- How many Visio drawing files used for diagrams has the IT lead counted (`.vsdx`) (`office_files.kind.visio`)?
- How many OneNote files used for notes has the IT lead counted (`.one`) (`office_files.kind.onenote`)?

### Device management

- How many devices are in scope according to the IT lead's inventory (`device_management.device_count`)?
- How many of those devices run Windows according to the IT lead (`device_management.windows_device_count`)?
- Does your organisation manage any devices through Microsoft (`device_management.in_use`)?

### Power Platform

- Does your organisation use Power Platform services such as Power Apps, Power Automate or Power BI (`power_platform.in_use`)?

### Telephony

- Does some or all of your organisation's telephony run through Microsoft (`telephony.in_use`)?
- Is a replacement available for the Microsoft telephony your organisation uses (`telephony.replacement_available`)?

### Identity and access

- How many applications use Microsoft single sign-on according to the IT lead (`identity_access.sso_application_count`)?
- Does your organisation use Microsoft Conditional Access (`identity_access.conditional_access_in_use`)?

### Security and compliance

- Are any Microsoft protection or retention features in use, according to the security or records leads (`security_compliance.protection_or_retention_in_use`)?

### Smaller Microsoft applications

- Do departments use smaller Microsoft applications such as Forms, Planner or Bookings (`small_apps.in_use`)?

### Application integrations

- How many business applications does the IT lead count as connected to Microsoft 365 (`integrations.application_count`)?
