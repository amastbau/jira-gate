"""CLI interface for JIRA Gate"""

import click
import sys
from jira import JIRA
from jira.exceptions import JIRAError
from .config import Config


def get_jira_client(config_path: str = None) -> JIRA:
    """Create and return authenticated JIRA client

    Args:
        config_path: Optional path to config file

    Returns:
        Authenticated JIRA client instance

    Raises:
        SystemExit: If configuration is invalid or authentication fails
    """
    try:
        config = Config(config_path)
        credentials = config.load()

        # Use appropriate authentication method
        if credentials['auth_method'] == 'pat':
            jira = JIRA(
                server=credentials['server'],
                token_auth=credentials['pat']
            )
        else:  # basic auth
            jira = JIRA(
                server=credentials['server'],
                basic_auth=(credentials['email'], credentials['api_token'])
            )
        return jira
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        click.echo("\nRun 'jira-gate config init' to create a config file.", err=True)
        sys.exit(1)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except JIRAError as e:
        click.echo(f"JIRA Authentication Error: {e.text}", err=True)
        sys.exit(1)


@click.group()
@click.version_option(version="0.1.0")
def main():
    """JIRA Gate - A CLI tool to interact with JIRA API"""
    pass


@main.group()
def config():
    """Manage configuration"""
    pass


@config.command('init')
@click.option('--path', default=None, help='Custom config file path')
@click.option('--force', is_flag=True, help='Overwrite existing config file')
@click.option('--interactive', '-i', is_flag=True, help='Interactive configuration setup')
def config_init(path, force, interactive):
    """Initialize configuration file"""
    try:
        cfg = Config(path)

        if interactive:
            # Interactive mode - prompt for all values
            click.echo("Welcome to JIRA Gate interactive setup!\n")

            server = click.prompt("JIRA server URL (e.g., https://your-domain.atlassian.net)", type=str)

            click.echo("\nChoose authentication method:")
            click.echo("  1. Personal Access Token (PAT) - for JIRA Data Center/Server")
            click.echo("  2. Email + API Token - for JIRA Cloud")

            auth_choice = click.prompt("\nSelect authentication method", type=click.Choice(['1', '2']), default='2')

            if auth_choice == '1':
                click.echo("\nTo generate a Personal Access Token:")
                click.echo("  1. Log in to your JIRA instance")
                click.echo("  2. Go to JIRA Settings > Personal Access Tokens")
                click.echo("  3. Click 'Create token'\n")

                pat = click.prompt("Enter your Personal Access Token", hide_input=True, type=str)

                cfg.create_interactive(
                    server=server,
                    auth_method='pat',
                    pat=pat,
                    force=force
                )
            else:
                click.echo("\nTo generate an API Token:")
                click.echo("  1. Go to https://id.atlassian.com/manage-profile/security/api-tokens")
                click.echo("  2. Click 'Create API token'\n")

                email = click.prompt("Enter your JIRA account email", type=str)
                api_token = click.prompt("Enter your API token", hide_input=True, type=str)

                cfg.create_interactive(
                    server=server,
                    auth_method='basic',
                    email=email,
                    api_token=api_token,
                    force=force
                )

            click.echo("\nSetup complete! Test your connection with: jira-gate test")
        else:
            # Template mode - create template file
            cfg.create_template(force=force)

    except (FileExistsError, ValueError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@config.command('show')
@click.option('--path', default=None, help='Custom config file path')
def config_show(path):
    """Show current configuration (without sensitive data)"""
    try:
        cfg = Config(path)
        credentials = cfg.load()
        click.echo(f"Server: {credentials['server']}")
        click.echo(f"Auth Method: {credentials['auth_method'].upper()}")

        if credentials['auth_method'] == 'pat':
            click.echo(f"PAT: {'*' * len(credentials['pat'])}")
        else:
            click.echo(f"Email: {credentials['email']}")
            click.echo(f"API Token: {'*' * len(credentials['api_token'])}")
    except (FileNotFoundError, ValueError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--config', default=None, help='Custom config file path')
def test(config):
    """Test JIRA connection"""
    jira = get_jira_client(config)
    try:
        user = jira.current_user()
        click.echo(f"Successfully connected to JIRA!")
        click.echo(f"Logged in as: {user}")
    except JIRAError as e:
        click.echo(f"Connection test failed: {e.text}", err=True)
        sys.exit(1)


@main.group()
def issue():
    """Manage JIRA issues"""
    pass


@issue.command('get')
@click.argument('issue_key')
@click.option('--config', default=None, help='Custom config file path')
def issue_get(issue_key, config):
    """Get details of a JIRA issue"""
    jira = get_jira_client(config)
    try:
        issue_obj = jira.issue(issue_key)
        click.echo(f"\nIssue: {issue_obj.key}")
        click.echo(f"Summary: {issue_obj.fields.summary}")
        click.echo(f"Status: {issue_obj.fields.status.name}")
        click.echo(f"Assignee: {issue_obj.fields.assignee.displayName if issue_obj.fields.assignee else 'Unassigned'}")
        click.echo(f"Reporter: {issue_obj.fields.reporter.displayName}")
        click.echo(f"Priority: {issue_obj.fields.priority.name if issue_obj.fields.priority else 'None'}")
        click.echo(f"\nDescription:\n{issue_obj.fields.description or 'No description'}")
    except JIRAError as e:
        click.echo(f"Error: {e.text}", err=True)
        sys.exit(1)


@issue.command('search')
@click.argument('jql')
@click.option('--max-results', default=50, help='Maximum number of results')
@click.option('--config', default=None, help='Custom config file path')
def issue_search(jql, max_results, config):
    """Search issues using JQL"""
    jira = get_jira_client(config)
    try:
        issues = jira.search_issues(jql, maxResults=max_results)
        if not issues:
            click.echo("No issues found.")
            return

        click.echo(f"\nFound {len(issues)} issue(s):\n")
        for issue_obj in issues:
            click.echo(f"{issue_obj.key}: {issue_obj.fields.summary} [{issue_obj.fields.status.name}]")
    except JIRAError as e:
        click.echo(f"Error: {e.text}", err=True)
        sys.exit(1)


@issue.command('create')
@click.option('--project', required=True, help='Project key')
@click.option('--summary', required=True, help='Issue summary')
@click.option('--description', default='', help='Issue description')
@click.option('--issue-type', default='Task', help='Issue type (default: Task)')
@click.option('--config', default=None, help='Custom config file path')
def issue_create(project, summary, description, issue_type, config):
    """Create a new JIRA issue"""
    jira = get_jira_client(config)
    try:
        new_issue = jira.create_issue(
            project=project,
            summary=summary,
            description=description,
            issuetype={'name': issue_type}
        )
        click.echo(f"Issue created successfully: {new_issue.key}")
    except JIRAError as e:
        click.echo(f"Error: {e.text}", err=True)
        sys.exit(1)


@issue.command('update')
@click.argument('issue_key')
@click.option('--summary', help='Update summary')
@click.option('--description', help='Update description')
@click.option('--config', default=None, help='Custom config file path')
def issue_update(issue_key, summary, description, config):
    """Update an existing JIRA issue"""
    jira = get_jira_client(config)
    try:
        issue_obj = jira.issue(issue_key)
        fields = {}
        if summary:
            fields['summary'] = summary
        if description:
            fields['description'] = description

        if fields:
            issue_obj.update(fields=fields)
            click.echo(f"Issue {issue_key} updated successfully.")
        else:
            click.echo("No fields to update.")
    except JIRAError as e:
        click.echo(f"Error: {e.text}", err=True)
        sys.exit(1)


@main.group()
def project():
    """Manage JIRA projects"""
    pass


@project.command('list')
@click.option('--config', default=None, help='Custom config file path')
def project_list(config):
    """List all accessible projects"""
    jira = get_jira_client(config)
    try:
        projects = jira.projects()
        if not projects:
            click.echo("No projects found.")
            return

        click.echo("\nAccessible projects:\n")
        for proj in projects:
            click.echo(f"{proj.key}: {proj.name}")
    except JIRAError as e:
        click.echo(f"Error: {e.text}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
