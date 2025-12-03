# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

JIRA Gate is a Python CLI tool that provides a command-line interface to interact with JIRA APIs. It supports both JIRA Cloud (via Email + API Token) and JIRA Data Center/Server (via Personal Access Token).

## Development Setup

```bash
# Install in development mode
pip install -e .

# Run the CLI
jira-gate --help

# Test connection (requires config file)
jira-gate test
```

## Testing

```bash
# Install test dependencies
pip install pytest

# Run tests
pytest
```

## Architecture

### Authentication Flow

The project uses a dual authentication system to support different JIRA deployment types:

1. **Config Loading** (`config.py:23`): The `Config.load()` method detects which authentication method is configured by checking for the presence of credentials:
   - PAT: Requires `pat` field
   - Basic Auth: Requires both `email` and `api_token` fields
   - Returns a dictionary with `auth_method` key ('pat' or 'basic')

2. **JIRA Client Creation** (`cli.py:10`): The `get_jira_client()` function:
   - Calls `Config.load()` to get credentials
   - Checks the `auth_method` field
   - Instantiates JIRA client with `token_auth` (PAT) or `basic_auth` (Email + API Token)
   - Handles authentication errors and provides user-friendly error messages

3. **Config File Location**: Defaults to `~/.jira-gate.config` (see `config.py:12`), but all commands accept `--config` for custom paths.

### CLI Structure

Built with Click framework using command groups:
- `config` group: Configuration management (init, show)
- `issue` group: Issue operations (get, search, create, update)
- `project` group: Project operations (list)
- Root level: `test` command for connection verification

All commands follow the pattern of calling `get_jira_client()` first, which handles authentication and error handling uniformly.

### Configuration Management

The `Config` class handles all config file operations:
- Template generation with both auth methods documented
- Validation that ensures either PAT or email+api_token is provided (but not both required)
- Path resolution supporting both default and custom config locations

## Important Patterns

### Adding New Commands

When adding new CLI commands:
1. Get JIRA client via `get_jira_client(config)` - this handles all auth and error cases
2. Wrap JIRA API calls in try/except for `JIRAError`
3. Use `click.echo()` for output, with `err=True` for errors
4. Call `sys.exit(1)` on errors after displaying message
5. Add `--config` option to support custom config paths

### Config File Security

Config files contain sensitive credentials and are excluded via `.gitignore`:
- Pattern `*.config` blocks all config files
- Pattern `.jira-gate.config` specifically blocks default location
- Template file `.jira-gate.config.template` is version controlled as documentation
