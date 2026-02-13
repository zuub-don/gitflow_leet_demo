# Changelog

All notable changes to this project will be documented in this file.

## [2.0.0] — 2026-02-13

### Added
- Autumn season module with month, temperature, and activity data.
- Winter season module with month, temperature, and activity data.
- `seasons summary` command for compact tabular output.

### Changed
- CLI `seasons all` now prints a blank line between seasons for readability.

## [1.0.1] — 2026-02-13

### Fixed
- Registry `get()` and `register()` now strip leading/trailing whitespace.

## [1.0.0] — 2026-02-13

### Added
- Spring season module with month, temperature, and activity data.
- Summer season module with month, temperature, and activity data.
- Central season registry with register/get/all_seasons API.
- CLI with `seasons all` and `seasons info <name>` commands.
- Full test suite for registry, CLI, spring, and summer modules.
