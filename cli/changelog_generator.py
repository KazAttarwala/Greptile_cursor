from typing import List, Dict, Any, Optional
import json
from datetime import datetime

from github_client import GitHubClient
from anthropic_client import AnthropicClient

class ChangelogGenerator:
    """Main class for generating changelogs from GitHub PRs using LLM."""
    
    def __init__(self, github_token: Optional[str] = None, 
                 anthropic_api_key: Optional[str] = None,
                 anthropic_model: str = "claude-3-7-sonnet-20250219"):
        """
        Initialize the changelog generator.
        
        Args:
            github_token: GitHub personal access token
            anthropic_api_key: Anthropic API key
            anthropic_model: Anthropic model to use
        """
        self.github = GitHubClient(token=github_token)
        self.llm = AnthropicClient(api_key=anthropic_api_key, model=anthropic_model)
    
    def generate_for_repo(self, repo: str, days: int = 30,
                          include_diff: bool = False) -> Dict[str, Any]:
        """
        Generate a changelog for a repository.
        
        Args:
            repo: Repository in format "owner/repo"
            days: Number of days to look back
            include_diff: Whether to include PR diffs for better context
            
        Returns:
            Dictionary with changelog data
        """
        # Get recent PRs
        print(f"Fetching recent PRs for {repo}...")
        prs = self.github.get_recent_prs(repo, days=days)
        
        if not prs:
            print("No recent PRs found.")
            return {
                "repo": repo,
                "generated_at": datetime.now().isoformat(),
                "changes": [],
                "categories": {}
            }
        
        print(f"Found {len(prs)} PRs. Processing...")
        
        # Process each PR to generate changelog entries
        changes = []
        for i, pr in enumerate(prs):
            print(f"Processing PR #{pr['number']} ({i+1}/{len(prs)}): {pr['title']}")
            
            # Optionally get diff for better context
            diff = None
            if include_diff:
                diff = self.github.get_pr_diff(repo, pr['number'])
            
            # Generate changelog entry
            entry = self.llm.generate_changelog_entry(
                pr_title=pr['title'],
                pr_description=pr['description'],
                pr_diff=diff
            )
            
            # Add PR metadata to entry
            changes.append({
                "pr_number": pr['number'],
                "pr_url": pr['html_url'],
                "author": pr['author'],
                "date": pr['merged_at'] or datetime.now().isoformat(),
                "summary": entry.get('summary', ''),
                "details": entry.get('details', ''),
                "type": entry.get('type', 'other'),
                "labels": pr.get('labels', [])
            })
        
        # Categorize changes
        print("Categorizing changes...")
        categories = self.llm.categorize_changes(changes)
        
        # Generate version summary if needed
        # (This would typically be done when publishing a specific version)
        
        return {
            "repo": repo,
            "generated_at": datetime.now().isoformat(),
            "changes": changes,
            "categories": {k: [c["pr_number"] for c in v] for k, v in categories.items()}
        }
    
    def format_as_markdown(self, changelog_data: Dict[str, Any], 
                           version: Optional[str] = None) -> str:
        """
        Format changelog data as markdown.
        
        Args:
            changelog_data: Changelog data dictionary
            version: Optional version number
            
        Returns:
            Markdown formatted changelog
        """
        repo = changelog_data.get("repo", "")
        changes = changelog_data.get("changes", [])

        # Start with header
        if version:
            markdown = f"# {version}\n\n"
        else:
            markdown = f"# Changelog for {repo}\n\n"
            
        markdown += f"Generated on {datetime.now().strftime('%Y-%m-%d')}\n\n"
        
        # Group changes by date
        changes_by_date = {}
        for change in changes:
            date = change.get("date", "").split("T")[0]  # Extract date part from ISO format
            if date not in changes_by_date:
                changes_by_date[date] = []
            changes_by_date[date].append(change)
        
        # Sort dates in reverse chronological order
        sorted_dates = sorted(changes_by_date.keys(), reverse=True)
        
        # Format changes by date
        for date in sorted_dates:
            date_changes = changes_by_date[date]
            
            # Add date header
            try:
                formatted_date = datetime.fromisoformat(date).strftime("%B %d, %Y")
            except:
                formatted_date = date
                
            markdown += f"## {formatted_date}\n\n"
            
            # Group by type if we have types
            changes_by_type = {}
            for change in date_changes:
                change_type = change.get("type", "other")
                if change_type not in changes_by_type:
                    changes_by_type[change_type] = []
                changes_by_type[change_type].append(change)
            
            # Format each type
            for change_type, type_changes in changes_by_type.items():
                # Format the type header
                type_header = change_type.capitalize()
                if change_type == "bugfix":
                    type_header = "Bug Fixes"
                elif change_type == "feature":
                    type_header = "New Features"
                elif change_type == "improvement":
                    type_header = "Improvements"
                    
                markdown += f"### {type_header}\n\n"
                
                # Add each change
                for change in type_changes:
                    markdown += f"- {change.get('summary')}"
                    
                    # Add PR reference if available
                    if change.get("pr_number"):
                        markdown += f" ([#{change.get('pr_number')}]({change.get('pr_url')}))"
                    
                    # Add details if available
                    if change.get("details"):
                        markdown += f"\n  {change.get('details')}"
                        
                    markdown += "\n"
                
                markdown += "\n"
        
        return markdown

# Example usage
if __name__ == "__main__":
    generator = ChangelogGenerator()
    changelog = generator.generate_for_repo("owner/repo", days=30)
    markdown = generator.format_as_markdown(changelog)
    print(markdown)