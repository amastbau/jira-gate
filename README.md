# JIRA Gate

A Python CLI tool to interact with the JIRA API.

## Features

- Simple configuration using a config file
- Interactive setup wizard for easy configuration
- Secure credential storage
- Multiple authentication methods (PAT or Email + API Token)
- Full JIRA API integration
- Easy-to-use command-line interface

## Installation

### From PyPI (Recommended)

```bash
# Install in a Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install git+https://github.com/amastbau/jira-gate.git
```

### From Source

```bash
# Clone the repository
git clone https://github.com/amastbau/jira-gate.git
cd jira-gate

# Install in development mode
pip install -e .
```

## Quick Start

After installation, run the interactive setup:

```bash
jira-gate config init --interactive
```

This will guide you through configuring your JIRA connection. Then test it:

```bash
jira-gate test
```

## Configuration

### Option 1: Interactive Setup (Recommended)

Run the interactive configuration wizard:

```bash
jira-gate config init --interactive
```

or use the short form:

```bash
jira-gate config init -i
```

The wizard will prompt you for:
- JIRA server URL
- Authentication method (PAT or Email + API Token)
- Credentials based on your chosen method

### Option 2: Template Configuration

Create a template configuration file to edit manually:

```bash
jira-gate config init
```

This will create a template config file at `~/.jira-gate.config`.

Then open the config file and add your JIRA credentials. Choose ONE of the following authentication methods:

#### Option A: Personal Access Token (PAT) - Recommended for JIRA Data Center/Server

Personal Access Tokens are the preferred authentication method for self-hosted JIRA instances (JIRA Data Center/Server) and some enterprise JIRA deployments.

**Configuration:**

```ini
[jira]
server = https://your-jira-server.com
pat = your-personal-access-token-here
```

**How to Generate a Personal Access Token:**

1. **Log in to your JIRA instance**
   - Navigate to your JIRA server (e.g., `https://issues.redhat.com` or your company's JIRA URL)

2. **Access Personal Access Token settings**
   - Click on your profile icon in the top-right corner
   - Select "Profile" or "Account Settings"
   - Look for "Personal Access Tokens" in the left sidebar or security settings
   - Or directly navigate to: `https://your-jira-server.com/secure/ViewProfile.jspa` and click "Personal Access Tokens"

3. **Create a new token**
   - Click "Create token" or "Generate new token"
   - Enter a descriptive name (e.g., "jira-gate CLI")
   - Set an expiration date (recommended for security)
   - Click "Create" or "Generate"

4. **Copy the token immediately**
   - **Important**: Copy the token immediately as it will only be shown once
   - Store it securely - you won't be able to view it again
   - If you lose it, you'll need to generate a new token

5. **Add to your config file**
   - Paste the token in your `~/.jira-gate.config` file
   - Or use interactive setup: `jira-gate config init -i`

**Example for Red Hat JIRA:**

```ini
[jira]
server = https://issues.redhat.com
pat = your-personal-access-token-here
```

**Token Permissions:**
- Ensure the token has sufficient permissions for the operations you need
- Typically requires: read/write access to issues, projects, and comments
- Check with your JIRA administrator if you encounter permission errors

**Security Best Practices:**
- Never share your PAT or commit it to version control
- Use token expiration dates and rotate tokens regularly
- Revoke tokens that are no longer needed
- Store the config file with restricted permissions: `chmod 600 ~/.jira-gate.config`

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
# Interactive setup (recommended for first-time setup)
jira-gate config init --interactive
jira-gate config init -i

# Create template config file for manual editing
jira-gate config init

# Initialize with custom path
jira-gate config init --path /path/to/custom/config

# Interactive setup with custom path
jira-gate config init --interactive --path /path/to/custom/config

# Overwrite existing config (works with both template and interactive modes)
jira-gate config init --force
jira-gate config init -i --force

# Show current configuration (credentials are masked)
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

# Create a subtask under a parent issue
jira-gate issue create-subtask --parent PROJ-123 --summary "Implement unit tests"
jira-gate issue create-subtask --parent PROJ-123 --summary "Code review" --description "Review changes"
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
