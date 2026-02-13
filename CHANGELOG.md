# Changelog

All notable changes to this project will be documented in this file.

## [3.0.0] — 2026-02-13

### Added
- Weather module with offline seasonal weather profiles (v2, after v1 was reverted).
- `seasons weather <name>` CLI command.
- `seasons compare <a> <b>` side-by-side season comparison command.
- Change Impact Analyzer (`tools/change_impact.py`) with pre-commit hook and GitHub Action.
- Registry `remove()` function for safe deregistration.

### Changed
- CLI output now uses Unicode box-drawing characters for season cards and summary table.
- `_format_season` accepts `verbose` kwarg for controlling detail level.

### Fixed
- Registry `register()` now validates: name must not be empty, months must not be empty.
- `compare` command rejects self-comparison.
- Activity strings truncated to prevent box-drawing overflow.

### Security
- Registry input validation prevents corrupted data from crashing downstream formatters.

### Incidents During This Release
- **Reverted feature/weather-api**: Original weather integration hit live API with timeout=0. Merged without CI passing. Reverted, then rewritten as offline v2.
- **hotfix/2.0.2 during release**: Production registry crash required emergency hotfix while release/3.0.0 was in QA. Cherry-picked into release branch.
- **Accidental commit to main**: Experimental module pushed directly to main, immediately reverted.
- **QA found 2 bugs during RC1**: Self-comparison and box-drawing overflow, fixed in RC2.

## [2.0.2] — 2026-02-13

### Fixed
- Registry `register()` validates name and months (emergency hotfix).
- Added `remove()` to registry API.

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
