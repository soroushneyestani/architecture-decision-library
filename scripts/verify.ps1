[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$pythonCommand = Get-Command python -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $pythonCommand) { throw 'Python is required on PATH to check the architecture decision library.' }

$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location -LiteralPath $PSScriptRoot
try {
    & $pythonCommand.Source -X utf8 -B (Join-Path $PSScriptRoot 'check_adrs.py')
    if ($LASTEXITCODE -ne 0) { throw 'Architecture decision library or committed index check failed.' }

    & $pythonCommand.Source -X utf8 -B (Join-Path $projectRoot 'tests/test_check_adrs.py') -v
    if ($LASTEXITCODE -ne 0) { throw 'Architecture decision checker contract tests failed.' }
    Write-Output 'Architecture decision library, index, and contract checks passed.'
} finally {
    Pop-Location
}
