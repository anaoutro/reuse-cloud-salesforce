# ReUse Cloud — Case Study

**Headline:** Turning equipment returns into explainable recovery decisions.

**Context.** A fictional electronics trade-in company needs to decide whether to resell, repair or recycle returned devices. Inconsistent assessments can produce attractive offers with negative expected contribution.

**My approach.** I designed a Salesforce workflow with a pure Apex decision engine, bulk-safe trigger logic, Queueable evaluation and an LWC workbench. Financial rules account for repair failure and condition eligibility. Server-side approval guards require unchanged evaluated inputs and the appropriate custom permission.

**Technical decisions.** I used Decimal arithmetic and explicit tie-breaking to make decisions reproducible. A before-save trigger recalculates derived outputs even when records are edited outside the UI. Input changes return the workflow to Draft. Application queries and DML enforce user-mode access, with private record sharing.

**Demonstration.** A healthy device produces BRL 620 in expected repair contribution; a risky device has negative contribution and needs manager review; a severely damaged device is eligible only for recycling. These are synthetic examples, not customer results.

**Evidence.** Source metadata, Apex tests, three seed devices, a rule walkthrough, and an interactive policy demonstration. Platform compilation, coverage and deployment must be verified in a Salesforce org.

**Next iteration.** Add immutable approval snapshots, operational job monitoring and observed repair outcomes. Current permissions and workflow are a portfolio implementation, not a production rollout.


## Review the implementation

See the [repository README](../README.md), [setup guide](SETUP.md), [data contract](DATA-CONTRACT.md) and [validation report](../VALIDATION.md).
