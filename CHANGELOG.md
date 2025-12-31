# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2025-12-29

### Added
- **Deletion Subsystem**: Added BithubJanitor for safe bulk deletion and delete_post/topic methods in BithubComms.
- **Dual-Mode Sync**: Implemented sync=True/False flag for deploy_core and communication methods.
- **Audience Flag**: Added target_audience='ai'|'human' to enforce JSON schemas or Markdown formatting.
- **Burn Protocol**: Added burn=True to deploy_core for "Burn After Reply" workflows.
- **Slow Nuke**: Implemented rate-limited bulk deletion to prevent API bans.

### Changed
- **License**: Switched from MIT to **Apache License 2.0**.
- **Architecture**: Refactored into "Hand" (Comms), "Janitor" (Cleanup), and "Brain" (Cores) components.
- **Documentation**: Consolidated documentation into README.md and docs/ folder.

### Fixed
- **Test Suite**: Refactored all tests to use mocks, ensuring zero network traffic during verification.
- **Rate Limiting**: Added poll_interval to wait loops to respect API limits.

## [1.0.0] - 2025-12-30
### Added
- **Pull Cores**: New  functionality in  to fetch Core Categories (Hegel, BITcore, etc.) recursively.
- **CLI Tool**: Updated  to execute the core sync process.
- **Security**: Implemented permission-aware syncing (skips inaccessible categories).

### Fixed
- **Integration**: Resolved syntax errors in  and environment loading in .
- **Configuration**: Added missing  and  to .

### Changed
- **Architecture**: Moved core sync logic from scripts to the  library for better reusability.
