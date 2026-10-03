# Validation — ReUse Cloud

Date: 2026-10-03.

## Executed locally

- Salesforce XML is well formed. Apex class metadata and field references were checked.
- All repository-relative documentation and browser asset links resolve.
- The included browser policy demo was checked at desktop and mobile sizes. It is a simulation, not a screenshot of Salesforce.

## Authored platform tests

RecoveryDecisionEngineTest covers policy boundaries, repair risk, bulk evaluation, duplicate identity, derived output tampering and input invalidation. RecoveryApprovalTest covers operator/approver/manager permissions, approval invalidation and private record sharing.

## Pending platform verification

No Salesforce org or CLI was connected. Apex has not been compiled or executed in Salesforce; no coverage percentage or successful metadata deployment is claimed. The GitHub Actions workflow checks structure and documentation, not Apex runtime behavior.

See [setup](docs/SETUP.md) and [architecture decisions](docs/ARCHITECTURE.md).

## GitHub preparation checks

The repository validator completed without errors: 36 XML files, two JSON files, one Python helper and 33 local links checked. The standalone demo passed desktop/mobile case selection, source-link resolution and overflow checks without browser runtime errors. GitHub Actions is prepared but has not run on GitHub yet.
