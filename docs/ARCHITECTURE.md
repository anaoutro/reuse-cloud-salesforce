# Architecture decisions — ReUse Cloud

## Pure policy engine

RecoveryDecisionEngine has no database operations. Decimal candidates are compared before two-decimal presentation rounding. Eligibility and tie-breaking remain explicit and testable. A separate handler applies outputs to records.

## Server-side integrity

A bulk-safe before-save trigger validates inputs and recalculates outputs on every insert/update. Approval transitions require evaluated, unchanged inputs and a custom permission. Input changes return a record to Draft. Recommendations are not approvals.

## Async evaluation and concurrency

Queueable evaluation locks current records, then transitions Draft rows only. Requests are bounded to 200 IDs. The workbench deliberately uses manual refresh; operational retry and monitoring are future work.

## Access control

Application queries and writes use user mode and with sharing. Derived fields are read-only in the operator permission set and written in trigger context. Record sharing is Private. Manager permission is required for credit above BRL 500 or negative contribution. These decisions still require runtime verification in Salesforce.

## Tradeoffs

Policy constants live in Apex rather than Custom Metadata, keeping v1 easy to inspect. Approved values are not stored in an immutable audit object. Export integration is represented by the contract, not a deployed connector.

See [the input contract](DATA-CONTRACT.md).
