# ReUse Cloud — Salesforce Recovery Workbench

**Apex + LWC + Salesforce DX.** A fictional trade-in operation needs consistent recommendations and controlled approvals for returned equipment.

## Implemented behavior
- A bulk-safe before-save trigger validates inputs and recomputes derived financial outputs, including writes made outside the LWC.
- Condition gates, repair failure risk, deterministic tie-breaking, negative-margin review, and policy versioning.
- Queueable evaluation re-reads and locks current Draft assets. Repeated jobs skip evaluated assets. Each request accepts up to 200 IDs.
- Input changes invalidate the prior workflow state and return the asset to Draft. Outputs are server-derived on every write.
- Operators evaluate; approvers approve ordinary cases; managers approve acquisition credit above BRL 500 or negative contribution.
- Queries and application DML use user mode; sharing is private. Trigger-derived output writes intentionally run in trigger context, with no queries/DML inside the loop.
- LWC lists the latest 200 visible assets and displays route comparisons. Direct resale and repair values are hypothetical when condition makes them ineligible.

## Deploy in your Salesforce environment
Requires Salesforce CLI, a suitable Developer/scratch org, and deployment permissions. API 62.0 is an intentional compatibility baseline, not a claim about the latest API.

~~~powershell
sf org login web --alias reuse-demo
sf project deploy start --source-dir force-app --target-org reuse-demo --test-level RunLocalTests
sf org assign permset --name Recovery_Operator --target-org reuse-demo
sf org assign permset --name Recovery_Manager --target-org reuse-demo
sf apex run --file scripts/seed.apex --target-org reuse-demo
sf apex run test --class-names RecoveryDecisionEngineTest RecoveryApprovalTest --target-org reuse-demo --result-format human --code-coverage --wait 10
~~~

For a scratch org, authenticate a Dev Hub, then use config/project-scratch-def.json. Set the org currency to BRL before seeding: the demo assumes BRL throughout and does not implement multi-currency conversion. Use Lightning App Builder to add **Recovery Workbench** to an app page and activate it. Open the Recovery Assets tab to edit inputs. Assign Recovery_Operator plus Recovery_Approver to ordinary approvers; managers receive Recovery_Operator plus Recovery_Manager. Private sharing limits records to their owner and authorized sharing paths.

## Demo script (3 minutes)
1. Seed the three devices. Inspect their route and contribution.
2. Select them and enqueue evaluation; refresh once the job finishes.
3. Approve as a manager. Show that editing repair cost returns an approved asset to Draft.
4. Show the trigger recalculating an attempted manual output change.
5. Revoke manager permission and demonstrate blocked high-credit approval with an appropriately permissioned test user.

## Architecture
~~~mermaid
flowchart LR
  LWC[Recovery Workbench] --> Controller[Controller / user-mode access]
  Controller --> Queue[Queueable / current-row lock]
  Queue --> Assets[Recovery Asset records]
  Assets --> Trigger[Before-save validation and approval guard]
  Trigger --> Engine[Pure Decimal decision engine]
  Engine --> Assets
~~~

## Validation and limits
The included Apex tests cover policy rules, 200-record evaluation, input invalidation, duplicate external IDs, derived field tampering, custom permission approval paths and private sharing. They are authored, but require Salesforce to compile and execute. RecoveryApprovalTest assumes a profile named Standard User in a clean Developer/scratch org; adapt the fixture for other profiles/locales. See the root VALIDATION.md for actual checks. No deployment or coverage percentage is claimed. Async failures can be inspected in Apex Jobs; the LWC currently uses manual refresh. There is no real vendor API, immutable approval audit log, automatic queue retry, or separate approval transaction object. Those are documented next steps rather than implied features.

## Official references
- [Apex CRUD/FLS and user-mode access](https://developer.salesforce.com/docs/platform/secure-coding/guide/secure-coding-access-control-protect-from-crud-fls-vulnerabilities.html)
- [Apex developer guide](https://resources.docs.salesforce.com/latest/latest/en-us/sfdc/pdf/salesforce_apex_developer_guide.pdf)
