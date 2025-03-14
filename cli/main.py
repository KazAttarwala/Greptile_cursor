#!/usr/bin/env python3
import argparse
import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

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
    
    # init command
    init_parser = subparsers.add_parser("init", help="Initialize a repository")
    init_parser.add_argument("repo", help="Repository in format 'owner/repo'")
    init_parser.add_argument("--name", help="Display name for the repository")
    
    # generate command
    generate_parser = subparsers.add_parser("generate", help="Generate changelog from PRs")
    generate_parser.add_argument("--repo", help="Repository ID (from init)")
    generate_parser.add_argument("--days", type=int, default=30, help="Number of days to look back")
    generate_parser.add_argument("--include-diff", action="store_true", help="Include PR diffs for better context")
    
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
    anthropic_model = os.environ.get("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")
    
    return ChangelogGenerator(
        github_token=github_token,
        anthropic_api_key=anthropic_api_key,
        anthropic_model=anthropic_model
    )

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
    print(f"Generating changelog for {repo['name']}...")
    
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
    
    if not github_token:
        print("Warning: No GitHub token provided. Some features may be limited.")
    
    if not anthropic_api_key:
        print("Error: Anthropic API key is required.")
        print("Set ANTHROPIC_API_KEY environment variable or use --anthropic-key")
        return 1
    
    if args.command == "init":
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