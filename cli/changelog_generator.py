from typing import List, Dict, Any, Optional
import json
from datetime import datetime

from github_client import GitHubClient
from anthropic_client import AnthropicClient

class ChangelogGenerator:
    """Main class for generating changelogs from GitHub PRs using LLM."""
    
    def __init__(self, github_token: Optional[str] = None, 
                 anthropic_api_key: Optional[str] = None,
                 anthropic_model: str = "claude-3-sonnet-20240229"):
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
        categories = changelog_data.get("categories", {})
        
        # Start with header
        if version:
            markdown = f"# {version}\n\n"
        else:
            markdown = f"# Changelog for {repo}\n\n"
            
        markdown += f"Generated on {datetime.now().strftime('%Y-%m-%d')}\n\n"
        
        # If we have categories, use them to organize the output
        if categories:
            for category, pr_numbers in categories.items():
                markdown += f"## {category}\n\n"
                
                # Find changes for this category
                category_changes = [c for c in changes if c["pr_number"] in pr_numbers]
                
                # Sort by date
                category_changes.sort(key=lambda x: x.get("date", ""), reverse=True)
                
                for change in category_changes:
                    markdown += f"- {change.get('summary')}"
                    
                    # Add PR reference
                    markdown += f" ([#{change.get('pr_number')}]({change.get('pr_url')}))"
                    
                    # Add details if available
                    if change.get("details"):
                        markdown += f"\n  {change.get('details')}"
                        
                    markdown += "\n"
                
                markdown += "\n"
        else:
            # No categories, just list changes by date
            sorted_changes = sorted(changes, key=lambda x: x.get("date", ""), reverse=True)
            
            for change in sorted_changes:
                markdown += f"- {change.get('summary')}"
                markdown += f" ([#{change.get('pr_number')}]({change.get('pr_url')}))"
                
                if change.get("details"):
                    markdown += f"\n  {change.get('details')}"
                    
                markdown += "\n"
        
        return markdown

# Example usage
if __name__ == "__main__":
    generator = ChangelogGenerator()
    changelog = generator.generate_for_repo("owner/repo", days=30)
    markdown = generator.format_as_markdown(changelog)
    print(markdown) 