#!/usr/bin/env python3
import argparse
import os
import sys
import webbrowser
import json
from datetime import datetime
from dotenv import load_dotenv
import requests

load_dotenv()

from github_client import GitHubClient
from ollama_client import OllamaClient
from storage import ChangelogStorage
from changelog_generator import ChangelogGenerator

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="AI-powered changelog generator")
    
    # Add global options
    parser.add_argument("--github-token", help="GitHub API token")
    parser.add_argument("--anthropic-key", help="Anthropic API key")

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # auth command for GitHub authentication
    auth_parser = subparsers.add_parser("auth", help="Authenticate with GitHub")
    auth_parser.add_argument("--no-browser", action="store_true", help="Don't open browser for authentication")
    
    # init command
    init_parser = subparsers.add_parser("init", help="Initialize a repository")
    init_parser.add_argument("repo", help="Repository in format 'owner/repo'")
    init_parser.add_argument("--name", help="Display name for the repository")
    
    # discover command to auto-discover repositories
    discover_parser = subparsers.add_parser("discover", help="Discover GitHub repositories you have access to")
    
    # generate command
    generate_parser = subparsers.add_parser("generate", help="Generate changelog from PRs")
    generate_parser.add_argument("--repo", help="Repository ID (from init)")
    generate_parser.add_argument("--days", type=int, default=30, help="Number of days to look back")
    generate_parser.add_argument("--include-diff", action="store_true", help="Include PR diffs for better context")
    generate_parser.add_argument("--pr", type=int, help="Generate changelog for specific PR number")
    
    # add command
    add_parser = subparsers.add_parser("add", help="Add a manual changelog entry")
    add_parser.add_argument("--repo", help="Repository ID (from init)")
    add_parser.add_argument("--summary", required=True, help="Summary of the change")
    add_parser.add_argument("--details", help="Additional details")
    add_parser.add_argument("--type", default="other", choices=["feature", "bugfix", "improvement", "docs", "other"], help="Type of change")
    
    # preview command
    preview_parser = subparsers.add_parser("preview", help="Preview the changelog")
    preview_parser.add_argument("--repo", help="Repository ID (from init)")
    
    # publish command
    publish_parser = subparsers.add_parser("publish", help="Publish the changelog")
    publish_parser.add_argument("--repo", help="Repository ID (from init)")
    publish_parser.add_argument("--version", help="Version number for this release")
    
    # list command
    list_parser = subparsers.add_parser("list", help="List repositories")
    
    return parser.parse_args()

def get_storage():
    """Get the storage instance."""
    # Ensure the data directory exists
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Initialize storage
    db_path = os.path.join(data_dir, 'changelog.db')
    return ChangelogStorage(db_path)

def get_generator(github_token=None, anthropic_api_key=None):
    """Get the changelog generator instance."""
    # Use environment variables if tokens not provided
    if not github_token:
        github_token = os.environ.get("GITHUB_TOKEN")

    if not anthropic_api_key:
        anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not anthropic_api_key:
            print("Warning: ANTHROPIC_API_KEY environment variable not set")
            print("Set this variable or pass --anthropic-key to use Claude")
    
    # Get Anthropic model from environment or use default
    anthropic_model = os.environ.get("ANTHROPIC_MODEL", "claude-3-7-sonnet-20250219")

    return ChangelogGenerator(
        github_token=github_token,
        anthropic_api_key=anthropic_api_key,
        anthropic_model=anthropic_model
    )

def github_auth():
    """Authenticate with GitHub using OAuth."""
    # GitHub OAuth app credentials
    client_id = os.environ.get("GITHUB_CLIENT_ID")
    client_secret = os.environ.get("GITHUB_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("Error: GitHub OAuth credentials not found.")
        print("Please set GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET environment variables.")
        print("You can create an OAuth app at: https://github.com/settings/developers")
        return None
    
    # Generate a random state for security
    import random
    import string
    state = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    
    # Authorization URL
    auth_url = f"https://github.com/login/oauth/authorize?client_id={client_id}&scope=repo&state={state}"
    
    print(f"Opening browser for GitHub authentication...")
    print(f"If the browser doesn't open automatically, visit this URL:")
    print(auth_url)
    
    # Open browser for authentication
    webbrowser.open(auth_url)
    
    # Get the authorization code from user input
    print("\nAfter authentication, GitHub will redirect you to a page.")
    print("Copy the 'code' parameter from the URL and paste it below:")
    code = input("Code: ").strip()
    
    # Exchange code for access token
    token_url = "https://github.com/login/oauth/access_token"
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "state": state
    }
    headers = {"Accept": "application/json"}
    
    try:
        response = requests.post(token_url, data=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if "access_token" in data:
            token = data["access_token"]
            
            # Save token to .env file
            env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
            
            # Read existing .env file if it exists
            env_vars = {}
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    for line in f:
                        if '=' in line and not line.startswith('#'):
                            key, value = line.strip().split('=', 1)
                            env_vars[key] = value
            
            # Update with new token
            env_vars["GITHUB_TOKEN"] = token
            
            # Write back to .env file
            with open(env_path, 'w') as f:
                for key, value in env_vars.items():
                    f.write(f"{key}={value}\n")
            
            print("Successfully authenticated with GitHub!")
            print(f"Token saved to {env_path}")
            
            # Set environment variable for current session
            os.environ["GITHUB_TOKEN"] = token
            
            return token
        else:
            print("Error: Failed to get access token.")
            print(data.get("error_description", "Unknown error"))
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error: {str(e)}")
        return None

def cmd_auth(args):
    """Handle GitHub authentication."""
    token = github_auth()
    if token:
        return 0
    return 1

def cmd_discover(args):
    """Discover GitHub repositories the user has access to."""
    storage = get_storage()
    
    # Get GitHub token
    github_token = args.github_token or os.environ.get("GITHUB_TOKEN")
    
    if not github_token:
        print("Error: GitHub token not found.")
        print("Please authenticate first with 'auth' command or provide a token with --github-token.")
        return 1
    
    # Create GitHub client
    github = GitHubClient(token=github_token)
    
    print("Discovering repositories you have access to...")
    
    try:
        # Get user's repositories
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Get user info
        user_response = requests.get("https://api.github.com/user", headers=headers)
        user_response.raise_for_status()
        user_data = user_response.json()
        username = user_data["login"]
        
        print(f"Authenticated as: {username}")
        
        # Get repositories
        repos_response = requests.get(f"https://api.github.com/user/repos?per_page=100", headers=headers)
        repos_response.raise_for_status()
        repos_data = repos_response.json()
        
        if not repos_data:
            print("No repositories found.")
            return 0
        
        print(f"Found {len(repos_data)} repositories.")
        print("Initializing repositories in the changelog database...")
        
        # Add repositories to storage
        for repo in repos_data:
            if repo["permissions"]["push"]:  # Only add repos with write access
                repo_id = f"{repo['owner']['login']}-{repo['name']}".lower().replace('/', '-')
                storage.add_repository(
                    repo_id=repo_id,
                    name=repo["full_name"],
                    url=repo["html_url"]
                )
                print(f"Added: {repo['full_name']} (ID: {repo_id})")
        
        print("\nRepositories have been added to the changelog database.")
        print("Use 'list' command to see all repositories.")
        
        return 0
        
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to discover repositories: {str(e)}")
        return 1

def cmd_init(args):
    """Initialize a repository."""
    storage = get_storage()
    
    # Extract owner and repo name
    parts = args.repo.split('/')
    if len(parts) != 2:
        print("Error: Repository must be in format 'owner/repo'")
        return 1
    
    owner, repo_name = parts
    
    # Generate a repo ID
    repo_id = f"{owner}-{repo_name}".lower().replace('/', '-')
    
    # Use provided name or generate one
    display_name = args.name or f"{owner}/{repo_name}"
    
    # Add to storage
    storage.add_repository(
        repo_id=repo_id,
        name=display_name,
        url=f"https://github.com/{args.repo}"
    )
    
    print(f"Repository initialized: {display_name}")
    print(f"Repository ID: {repo_id}")
    print("Use this ID in subsequent commands with --repo")
    
    return 0

def cmd_generate(args):
    """Generate changelog from PRs."""
    storage = get_storage()
    
    # Get the repository
    repos = storage.get_repositories()
    repo = next((r for r in repos if r['id'] == args.repo), None)
    
    if not repo:
        print(f"Error: Repository '{args.repo}' not found")
        return 1
    
    # Extract GitHub repo path from URL
    if not repo.get('url'):
        print("Error: Repository URL not found")
        return 1
    
    github_repo = repo['url'].replace('https://github.com/', '')
    
    # Generate changelog
    generator = get_generator()
    
    if args.pr:
        # Generate changelog for specific PR
        print(f"Generating changelog for PR #{args.pr} in {repo['name']}...")
        
        # Create GitHub client
        github_token = args.github_token or os.environ.get("GITHUB_TOKEN")
        github = GitHubClient(token=github_token)
        
        try:
            # Get PR details
            pr_url = f"https://api.github.com/repos/{github_repo}/pulls/{args.pr}"
            headers = {"Authorization": f"token {github_token}"} if github_token else {}
            response = requests.get(pr_url, headers=headers)
            response.raise_for_status()
            pr_data = response.json()
            
            # Create PR object in the format expected by the generator
            pr = {
                "number": pr_data["number"],
                "title": pr_data["title"],
                "description": pr_data["body"] or "",
                "author": pr_data["user"]["login"],
                "merged_at": pr_data["merged_at"],
                "html_url": pr_data["html_url"],
                "labels": [label["name"] for label in pr_data["labels"]]
            }
            
            # Get PR diff if requested
            diff = None
            if args.include_diff:
                diff = github.get_pr_diff(github_repo, args.pr)
            
            # Generate changelog entry
            entry = generator.llm.generate_changelog_entry(
                pr_title=pr["title"],
                pr_description=pr["description"],
                pr_diff=diff
            )
            
            # Add PR metadata to entry
            change = {
                "pr_number": pr["number"],
                "pr_url": pr["html_url"],
                "author": pr["author"],
                "date": pr["merged_at"] or datetime.now().isoformat(),
                "summary": entry.get('summary', ''),
                "details": entry.get('details', ''),
                "type": entry.get('type', 'other'),
                "labels": pr.get('labels', [])
            }
            
            # Add to storage
            date = change["date"].split("T")[0] if "T" in change["date"] else change["date"]
            entry_id = storage.add_changelog_entry(args.repo, date, change)
            
            print(f"Changelog entry generated for PR #{args.pr}")
            print(f"Summary: {change['summary']}")
            print(f"Type: {change['type']}")
            
            return 0
            
        except requests.exceptions.RequestException as e:
            print(f"Error: Failed to fetch PR #{args.pr}: {str(e)}")
            return 1
    else:
        # Generate changelog for time period
        print(f"Generating changelog for {repo['name']} (last {args.days} days)...")

        changelog = generator.generate_for_repo(
            repo=github_repo,
            days=args.days,
            include_diff=args.include_diff
        )

        # Save to storage
        storage.save_changelog(args.repo, changelog)
        
        print(f"Changelog generated and saved for {repo['name']}")
        print(f"Found {len(changelog.get('changes', []))} changes")
        
        return 0

def cmd_add(args):
    """Add a manual changelog entry."""
    storage = get_storage()
    
    # Get the repository
    repos = storage.get_repositories()
    repo = next((r for r in repos if r['id'] == args.repo), None)
    
    if not repo:
        print(f"Error: Repository '{args.repo}' not found")
        return 1
    
    # Create entry
    entry = {
        "pr_number": None,  # Manual entry
        "pr_url": None,
        "author": os.environ.get("USER", "unknown"),
        "summary": args.summary,
        "details": args.details or "",
        "type": args.type,
        "date": datetime.now().isoformat()
    }

    # Add to storage
    today = datetime.now().strftime("%Y-%m-%d")
    storage.add_changelog_entry(args.repo, today, entry)
    
    print(f"Manual entry added to {repo['name']} changelog")
    
    return 0

def cmd_preview(args):
    """Preview the changelog."""
    storage = get_storage()
    
    # Get the repository
    repos = storage.get_repositories()
    repo = next((r for r in repos if r['id'] == args.repo), None)
    
    if not repo:
        print(f"Error: Repository '{args.repo}' not found")
        return 1
    
    # Get the changelog
    changelog = storage.get_changelog(args.repo)
    
    if not changelog:
        print(f"No changelog found for {repo['name']}")
        return 1
    
    # Format as markdown
    generator = get_generator()
    markdown = generator.format_as_markdown(changelog)
    
    # Print the markdown
    print("\n" + "=" * 80)
    print(f"CHANGELOG PREVIEW FOR {repo['name']}")
    print("=" * 80 + "\n")
    print(markdown)
    
    return 0

def cmd_publish(args):
    """Publish the changelog."""
    storage = get_storage()
    
    # Get the repository
    repos = storage.get_repositories()
    repo = next((r for r in repos if r['id'] == args.repo), None)
    
    if not repo:
        print(f"Error: Repository '{args.repo}' not found")
        return 1
    
    # Get the changelog
    changelog = storage.get_changelog(args.repo)
    
    if not changelog:
        print(f"No changelog found for {repo['name']}")
        return 1
    
    # Format as markdown
    generator = get_generator()
    markdown = generator.format_as_markdown(changelog, version=args.version)
    
    # Save to a file
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'web', 'public', 'changelogs')
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"{args.repo}.md"
    if args.version:
        filename = f"{args.repo}-{args.version}.md"
    
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w') as f:
        f.write(markdown)

    print(f"Changelog published to {filepath}")
    print("The web interface will now display the updated changelog")
    
    return 0

def cmd_list(args):
    """List repositories."""
    storage = get_storage()
    
    # Get all repositories
    repos = storage.get_repositories()
    
    if not repos:
        print("No repositories found")
        return 0
    
    print("\nAvailable repositories:")
    print("-" * 80)
    print(f"{'ID':<20} {'Name':<30} {'Last Updated':<20}")
    print("-" * 80)
    
    for repo in repos:
        last_updated = repo.get('last_updated', 'Never')
        if last_updated and last_updated != 'Never':
            try:
                dt = datetime.fromisoformat(last_updated)
                last_updated = dt.strftime("%Y-%m-%d %H:%M")
            except:
                pass

        print(f"{repo['id']:<20} {repo['name']:<30} {last_updated:<20}")
    
    print()
    
    return 0

def main():
    """Main entry point."""
    args = parse_args()
    
    # Check for API keys
    github_token = args.github_token or os.environ.get("GITHUB_TOKEN")
    anthropic_api_key = args.anthropic_key or os.environ.get("ANTHROPIC_API_KEY")
    
    if not github_token and args.command not in ["auth", "list"]:
        print("Warning: No GitHub token provided. Some features may be limited.")
        print("Consider running the 'auth' command to authenticate with GitHub.")
    
    if not anthropic_api_key and args.command not in ["auth", "list", "discover"]:
        print("Error: Anthropic API key is required.")
        print("Set ANTHROPIC_API_KEY environment variable or use --anthropic-key")
        return 1
    
    if args.command == "auth":
        return cmd_auth(args)
    elif args.command == "discover":
        return cmd_discover(args)
    elif args.command == "init":
        return cmd_init(args)
    elif args.command == "generate":
        return cmd_generate(args)
    elif args.command == "add":
        return cmd_add(args)
    elif args.command == "preview":
        return cmd_preview(args)
    elif args.command == "publish":
        return cmd_publish(args)
    elif args.command == "list":
        return cmd_list(args)
    else:
        print("Error: No command specified")
        print("Run with --help for usage information")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 