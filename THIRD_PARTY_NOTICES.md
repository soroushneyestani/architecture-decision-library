# Third-party references and tools

Architecture Decision Library includes its original Markdown format, examples and Python validation code. MADR is a design reference for capturing context, options and confirmation. The project uses its own template and checker. [MADR](https://adr.github.io/madr/) · [MADR upstream license information](https://adr.github.io/madr/#license)

Evidence notes link to independently distributed implementation revisions and CI runs. The linked products and their dependencies retain their own terms. This distribution includes evidence and links rather than copies of those implementations.

The checker and tests use the Python standard library without installed packages. Python, Git and PowerShell are separately installed tools. GitHub Actions fetches the pinned checkout, Python setup and Go setup actions, and the Linux CI job runs pinned Gitleaks. None of those tool distributions is bundled in the source ZIP. [Python license](https://docs.python.org/3/license.html) · [PowerShell license](https://github.com/PowerShell/PowerShell/blob/master/LICENSE.txt) · [Git license](https://github.com/git/git/blob/master/COPYING) · [checkout](https://github.com/actions/checkout) · [setup-python](https://github.com/actions/setup-python) · [setup-go](https://github.com/actions/setup-go) · [Gitleaks license](https://github.com/gitleaks/gitleaks/blob/master/LICENSE)
