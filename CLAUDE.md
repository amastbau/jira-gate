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

# Interactive setup (recommended for first-time users)
jira-gate config init --interactive

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

The `Config` class handles all config file operations with two creation modes:

1. **Interactive Setup** (`config.py:114`): The `create_interactive()` method:
   - Takes server URL and auth method as parameters
   - Accepts credentials (PAT or email+api_token) based on chosen method
   - Creates a ready-to-use config file with actual credentials
   - Used by `jira-gate config init --interactive`

2. **Template Mode** (`config.py:77`): The `create_template()` method:
   - Generates a config file with commented examples
   - User must manually edit and add credentials
   - Used by `jira-gate config init` (without --interactive)

Both modes:
- Validate that either PAT or email+api_token is provided (but not both required)
- Support both default (`~/.jira-gate.config`) and custom config paths
- Respect the `--force` flag to overwrite existing files

## Important Patterns

### Adding New Commands

When adding new CLI commands:
1. Get JIRA client via `get_jira_client(config)` - this handles all auth and error cases
2. Wrap JIRA API calls in try/except for `JIRAError`
3. Use `click.echo()` for output, with `err=True` for errors
4. Call `sys.exit(1)` on errors after displaying message
5. Add `--config` option to support custom config paths

### Interactive CLI Prompts

The interactive setup (`cli.py:63`) uses Click's prompt features:
- `click.prompt()` for text input with type validation
- `type=click.Choice()` for multiple-choice selections
- `hide_input=True` for sensitive credentials (tokens, passwords)
- Contextual help messages shown before prompts to guide users

### Config File Security

Config files contain sensitive credentials and are excluded via `.gitignore`:
- Pattern `*.config` blocks all config files
- Pattern `.jira-gate.config` specifically blocks default location
- Template file `.jira-gate.config.template` is version controlled as documentation
- Interactive setup uses `hide_input=True` to prevent credential exposure in terminal
