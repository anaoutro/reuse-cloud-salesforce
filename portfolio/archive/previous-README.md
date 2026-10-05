> **Installed and API-verified in Ana's Salesforce Developer Edition.** 15 Apex tests passed. Demo data loaded. UI screenshots/recording pending sign-in. [Verified implementation status](portfolio/IMPLEMENTATION-STATUS.md).

# ReUse Cloud

### Explainable equipment recovery decisions with Salesforce Apex and LWC

A returned device can look valuable and still produce a loss after repair risk, acquisition credit and logistics. ReUse Cloud recommends **resale, repair or recycling**, explains the economics, and controls who may approve the decision.

**Apex · Lightning Web Components · Queueable · Salesforce DX · MIT**

![Interactive browser demonstration of the recovery decision policy](docs/images/decision-lab.png)

*Browser policy demonstration. This image is not a deployed Salesforce screen.*

[Case study](docs/CASE-STUDY.md) · [Setup and demo script](docs/SETUP.md) · [Architecture](docs/ARCHITECTURE.md) · [Validation](VALIDATION.md)

## What to review

| Capability | Implementation |
|---|---|
| Explainable scoring | [Pure Apex Decimal engine](force-app/main/default/classes/RecoveryDecisionEngine.cls) |
| Bulk validation and approval guards | [Before-save handler](force-app/main/default/classes/RecoveryAssetHandler.cls) |
| Async evaluation | [Queueable job](force-app/main/default/classes/RecoveryEvaluationJob.cls) |
| User-mode application access | [Apex controller](force-app/main/default/classes/RecoveryController.cls) |
| Operator interface | [LWC workbench](force-app/main/default/lwc/recoveryWorkbench/recoveryWorkbench.js) |
| Business and permission tests | [Decision tests](force-app/main/default/classes/RecoveryDecisionEngineTest.cls), [approval tests](force-app/main/default/classes/RecoveryApprovalTest.cls) |

## The worked example

For DEMO-001, repair succeeds with assumed probability 90%.

- Resale: 1,000 − 400 credit − 50 logistics = **BRL 550**.
- Repair: 0.9 × 1,400 + 0.1 × 100 salvage − 200 repair − 400 credit − 50 logistics = **BRL 620**.
- Recycle: 100 salvage − 400 credit − 50 logistics = **BRL −350**.

Repair wins. A recommendation is not an approval. Credit above BRL 500 or negative contribution requires manager permission. Changes to decision inputs invalidate the approved state.

## Try the demo

After downloading or cloning, open [docs/demo/index.html](docs/demo/index.html) in a browser. It works offline. Adjust condition, repair cost, credit and failure probability to inspect policy behavior. It cannot approve Salesforce records.

## Run in Salesforce

Requires Salesforce CLI and an authorized Developer/scratch org. Use a demo org with BRL currency. API 62.0 is a compatibility baseline.

~~~powershell
sf org login web --alias reuse-demo
sf project deploy start --source-dir force-app --target-org reuse-demo --test-level RunLocalTests
sf org assign permset --name Recovery_Operator --target-org reuse-demo
sf org assign permset --name Recovery_Manager --target-org reuse-demo
sf apex run --file scripts/seed.apex --target-org reuse-demo
sf apex run test --class-names RecoveryDecisionEngineTest RecoveryApprovalTest --target-org reuse-demo --result-format human --code-coverage --wait 10
~~~

Add Recovery Workbench to an app page using Lightning App Builder. Full permission roles and test-fixture assumptions are in [setup](docs/SETUP.md).

## Architecture

~~~mermaid
flowchart LR
    LWC[Recovery Workbench] --> Controller[Apex controller]
    Controller --> Queue[Queueable evaluation]
    Queue --> Records[Recovery Asset records]
    Records --> Trigger[Validation and approval guard]
    Trigger --> Engine[Decimal decision engine]
~~~

## Verification status

**Implemented:** Apex source, trigger, metadata, permissions, LWC, seed records and two Apex test classes.

**Checked locally:** XML structure, metadata references, documentation links and browser demo behavior. Run `python scripts/check_repository.py` for repository checks.

**Still required:** Salesforce compilation, deployment, Apex test execution and runtime permissions verification. CI checks repository structure; it does not compile Apex or claim code coverage.

## Repository map

~~~text
force-app/main/default/  Apex, trigger, objects, permissions and LWC
config/                 Scratch-org definition
scripts/                Seed Apex and repository checks
docs/                   Case study, architecture, setup, contract and offline demo
.github/                CI and review templates
~~~

[Related Databricks project](docs/RELATED-PROJECT.md) · [Contributing](CONTRIBUTING.md) · [MIT license](LICENSE)

All customers, device models and financial assumptions are synthetic. This is an independent portfolio project.
