# Changelog

All core functionality for the Bithub plugin is documented here.


## [1.1.0] - 2026-01-01

### Resilience & Un-Fitting
- **Synaptic Storage**: Centralized all registries in `resources/` directory.
- **Dynamic Path Resolution**: Eliminated absolute paths; implemented relative resolution for portability.
- **Dual-Layer Testing**: Implemented scoped unit tests and swarm integration suites (52+ tests restored).
- **Neural Processing Standard**: Enforced **Guard → Do → Verify** flow across all core modules.
- **Branding Integrity**: Completed global rebranding for `elizaos.b8` and `a0.b8` nodes.

## [1.0.0] - 2025-12-31

### Core Functionality
- **Multi-Turn Logic**: Implemented `reply` command and `reply_to_post` methods for complex agentic dialogues.
- **Deletion Subsystem**: BithubJanitor for safe bulk deletion and management of posts/topics.
- **Dual-Mode Sync**: Support for `sync=True/False` flags in deployment and communication methods.
- **Audience Control**: `target_audience` parameter to enforce JSON schemas (AI) or Markdown (Human).
- **Burn Protocol**: `burn=True` support for ephemeral 'Burn After Reply' workflows.
- **Synapse Architecture**: Refactored into 'Hand' (Comms), 'Janitor' (Cleanup), and 'Brain' (Cores) components.
- **Core Sync**: Recursive fetching and synchronization of Core Categories and Categories.
- **CLI Interface**: Unified entry point for agent interaction, core deployment, and registry management.
- **Security**: Permission-aware syncing and environment-based authentication.
- **Reliability**: Rate-limiting with jitter, exponential backoff, and comprehensive test suite with 100% mock coverage.
