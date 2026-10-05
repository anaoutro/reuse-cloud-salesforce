param([string]$OrgAlias = "ana-portfolio")
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)
function Invoke-Sf { & sf @args; if ($LASTEXITCODE -ne 0) { throw "Salesforce command failed; installation stopped." } }
if (-not (Get-Command sf -ErrorAction SilentlyContinue)) { throw "Install the official Salesforce CLI first." }
Invoke-Sf org login web --instance-url https://orgfarm-6348f8859a-dev-ed.develop.my.salesforce.com --alias $OrgAlias
Invoke-Sf project deploy start --source-dir force-app --target-org $OrgAlias --test-level RunLocalTests --wait 20
Invoke-Sf org assign permset --name Recovery_Operator --target-org $OrgAlias
Invoke-Sf org assign permset --name Recovery_Manager --target-org $OrgAlias
# Confirm the org uses BRL before executing the fictional seed:
$seed = Read-Host "Type SEED to add the fictional demonstration records"
if ($seed -eq "SEED") { Invoke-Sf apex run --file scripts/seed.apex --target-org $OrgAlias }
Invoke-Sf org open --target-org $OrgAlias
