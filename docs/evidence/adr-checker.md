# Architecture decision checker and index evidence

The Python standard-library checker validates numbered Markdown records before comparing the committed index or printing its canonical replacement. Both paths use the same parsed records and evidence checks. [Checker source](../../scripts/check_adrs.py) · [Decision index](../adr/README.md)

The local verifier checks the bundled library and runs contract and misuse tests using synthetic fixtures. The recorded results distinguish the local checks from hosted runs. [Contract tests](../../tests/test_check_adrs.py) · [PowerShell verifier](../../scripts/verify.ps1) · [Verification record](../RELEASE_EVIDENCE.md)
