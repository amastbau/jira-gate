# JIRA Gate

A Python CLI tool to interact with the JIRA API.

## Features

- Simple configuration using a config file
- Secure credential storage
- Multiple authentication methods (PAT or Email + API Token)
- Full JIRA API integration
- Easy-to-use command-line interface

## Installation

### From Source

```bash
# Clone the repository
git clone <repository-url>
cd jira-gate

# Install in development mode
pip install -e .
```

### Using pip

```bash
pip install -r requirements.txt
pip install -e .
```

## Configuration

### 1. Initialize Configuration

Run the following command to create a configuration file:

```bash
jira-gate config init
```

This will create a config file at `~/.jira-gate.config`.

### 2. Edit Configuration

Open the config file and add your JIRA credentials. Choose ONE of the following authentication methods:

#### Option A: Personal Access Token (PAT) - Recommended for JIRA Data Center/Server

```ini
[jira]
server = https://your-jira-server.com
pat = your-personal-access-token-here
```

To generate a Personal Access Token:
1. Log in to your JIRA instance
2. Go to JIRA Settings > Personal Access Tokens
3. Click "Create token"
4. Copy the token and paste it in the config file

#### Option B: Email + API Token - Common for JIRA Cloud

```ini
[jira]
server = https://your-domain.atlassian.net
email = your-email@example.com
api_token = your-api-token-here
```

To generate a JIRA API token:
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Copy the token and paste it in the config file

### 3. Test Connection

Verify your configuration:

```bash
jira-gate test
```

## Usage

### Configuration Commands

```bash
# Initialize config file
jira-gate config init

# Initialize with custom path
jira-gate config init --path /path/to/custom/config

# Overwrite existing config
jira-gate config init --force

# Show current configuration (API token is masked)
jira-gate config show
```

### Issue Commands

```bash
# Get issue details
jira-gate issue get PROJ-123

# Search issues using JQL
jira-gate issue search "project = PROJ AND status = Open"
jira-gate issue search "assignee = currentUser()" --max-results 10

# Create a new issue
jira-gate issue create --project PROJ --summary "Bug fix" --description "Description here"
jira-gate issue create --project PROJ --summary "New feature" --issue-type Story

# Update an issue
jira-gate issue update PROJ-123 --summary "Updated summary"
jira-gate issue update PROJ-123 --description "Updated description"
```

### Project Commands

```bash
# List all accessible projects
jira-gate project list
```

### Using Custom Config Path

All commands support a custom config file path:

```bash
jira-gate --config /path/to/config test
jira-gate issue get PROJ-123 --config /path/to/config
```

## Development

### Project Structure

```
jira-gate/
├── jira_gate/
│   ├── __init__.py
│   ├── cli.py          # Main CLI interface
│   └── config.py       # Configuration handler
├── tests/              # Test files
├── pyproject.toml      # Project metadata
├── requirements.txt    # Dependencies
└── README.md
```

### Running Tests

```bash
# Install development dependencies
pip install pytest

# Run tests
pytest
```

## Security Notes

- The config file contains sensitive information (PAT or API token)
- Never commit the `.config` file to version control
- The `.gitignore` file is configured to exclude config files
- Use file permissions to protect your config file:
  ```bash
  chmod 600 ~/.jira-gate.config
  ```

## Common JQL Examples

```bash
# My open issues
jira-gate issue search "assignee = currentUser() AND status != Done"

# Recent issues
jira-gate issue search "created >= -7d"

# High priority bugs
jira-gate issue search "type = Bug AND priority = High"

# Issues in sprint
jira-gate issue search "sprint in openSprints()"
```

## Troubleshooting

### Authentication Errors

If you get authentication errors:
1. Verify your server URL is correct (no trailing slash)
2. For PAT authentication:
   - Ensure your Personal Access Token is valid and not expired
   - Check that the token has the necessary permissions
3. For Email + API Token authentication:
   - Check that your email is correct
   - Ensure your API token is valid and not expired
4. Run `jira-gate config show` to verify configuration and auth method

### Connection Issues

If you cannot connect to JIRA:
1. Check your internet connection
2. Verify the JIRA server is accessible
3. Check if your organization uses a proxy

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
