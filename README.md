# Ladcemas

**Ladcemas is a planned installer and orchestration interface for self-hosted applications and services.**

Ladcemas aims to make it easier to choose, deploy, configure, update, and maintain a collection of independently useful software without asking users to learn the installation details of every component. It is intended to provide a human-friendly entry point to the installation and lifecycle workflows used by [Aggregare](https://github.com/azwarners/Aggregare).

## Purpose

Aggregare defines the composition of applications, configuration conventions, and infrastructure integrations. Ladcemas is intended to make those capabilities approachable through an installer and management interface.

The design goals are to:

- Guide users through selecting an installation profile and the applications they want.
- Explain required dependencies and configuration choices before making changes.
- Reuse established tools and application installers rather than reinventing their functionality.
- Support repeatable installation, reconfiguration, and maintenance.
- Keep the underlying services useful independently of Ladcemas.
- Provide clear status and errors, with explicit operator control over consequential actions.

A terminal-based interface (TUI) is one intended form of interaction; a graphical interface may be considered as the project develops. These interfaces are **plans, not implemented features**.

## Project status

**Concept / placeholder repository.** Ladcemas does not yet contain a working installer, CLI, TUI, GUI, or release. No installation procedure or executable quick start is available.

For an implemented starting point today, see [Aggregare's installation guide](https://github.com/azwarners/Aggregare#install-aggregare-on-ubuntu-server). Aggregare currently uses an Ubuntu Server installation path built around Ansible. Ladcemas should complement that work rather than duplicate it.

## Quick start

There is nothing to install or run from this repository yet. To inspect the project description locally:

```sh
git clone https://github.com/azwarners/Ladcemas.git
cd Ladcemas
cat README.md
```

## Planned relationship to the stack

```text
Operator
   |
   v
Ladcemas (planned installer / management interface)
   |
   v
Aggregare (application catalog and composition)
   |
   v
Existing deployment tools and independently useful applications
```

The final interface, packaging, lifecycle operations, and integration contracts remain to be defined. This README deliberately distinguishes goals from shipping capabilities.
