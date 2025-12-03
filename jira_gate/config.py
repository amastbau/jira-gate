"""Configuration handler for JIRA Gate"""

import os
import configparser
from pathlib import Path
from typing import Dict, Optional


class Config:
    """Handle configuration file operations"""

    DEFAULT_CONFIG_PATH = Path.home() / ".jira-gate.config"

    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration handler

        Args:
            config_path: Path to config file. If None, uses default location
        """
        self.config_path = Path(config_path) if config_path else self.DEFAULT_CONFIG_PATH
        self.config = configparser.ConfigParser()

    def load(self) -> Dict[str, str]:
        """Load configuration from file

        Returns:
            Dictionary with configuration values

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If required fields are missing
        """
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Config file not found at {self.config_path}. "
                f"Please create one using the template."
            )

        self.config.read(self.config_path)

        if 'jira' not in self.config:
            raise ValueError("Config file missing [jira] section")

        jira_config = self.config['jira']

        # Check if server is provided (always required)
        if 'server' not in jira_config or not jira_config['server'].strip():
            raise ValueError("Missing required field: server")

        # Support two authentication methods:
        # 1. Personal Access Token (PAT) - recommended for JIRA Data Center/Server
        # 2. Email + API Token - common for JIRA Cloud

        has_pat = 'pat' in jira_config and jira_config['pat'].strip()
        has_basic_auth = ('email' in jira_config and jira_config['email'].strip() and
                         'api_token' in jira_config and jira_config['api_token'].strip())

        if not has_pat and not has_basic_auth:
            raise ValueError(
                "Authentication credentials missing. Provide either:\n"
                "  - 'pat' (Personal Access Token), OR\n"
                "  - Both 'email' and 'api_token'"
            )

        result = {'server': jira_config['server']}

        if has_pat:
            result['auth_method'] = 'pat'
            result['pat'] = jira_config['pat']
        else:
            result['auth_method'] = 'basic'
            result['email'] = jira_config['email']
            result['api_token'] = jira_config['api_token']

        return result

    def create_template(self, force: bool = False) -> None:
        """Create a template configuration file

        Args:
            force: If True, overwrite existing file

        Raises:
            FileExistsError: If file exists and force is False
        """
        if self.config_path.exists() and not force:
            raise FileExistsError(
                f"Config file already exists at {self.config_path}. "
                f"Use --force to overwrite."
            )

        template_content = """[jira]
# Your JIRA server URL (e.g., https://your-domain.atlassian.net)
server =

# Authentication Method - Choose ONE of the following:

# Option 1: Personal Access Token (PAT) - Recommended for JIRA Data Center/Server
# Generate at: JIRA Settings > Personal Access Tokens
# Uncomment and fill in if using PAT:
# pat =

# Option 2: Email + API Token - Common for JIRA Cloud
# Generate API token at: https://id.atlassian.com/manage-profile/security/api-tokens
# Uncomment and fill in if using Email + API Token:
# email =
# api_token =
"""

        self.config_path.write_text(template_content)
        print(f"Config template created at: {self.config_path}")
        print("Please edit the file and add your JIRA credentials.")
