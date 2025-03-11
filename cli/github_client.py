import os
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

class GitHubClient:
    """Client for interacting with GitHub API to fetch PR information."""
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize the GitHub client.
        
        Args:
            token: GitHub personal access token (optional)
        """
        self.token = token or os.environ.get("GITHUB_TOKEN")
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"
    
    def get_recent_prs(self, repo: str, days: int = 30, state: str = "closed") -> List[Dict[str, Any]]:
        """
        Get recent PRs from a repository.
        
        Args:
            repo: Repository in format "owner/repo"
            days: Number of days to look back
            state: PR state (open, closed, all)
            
        Returns:
            List of PR dictionaries
        """
        url = f"{self.base_url}/repos/{repo}/pulls"
        
        # Calculate date for filtering
        since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        params = {
            "state": state,
            "sort": "updated",
            "direction": "desc",
            "per_page": 100
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            prs = response.json()
            
            # Filter PRs by date and merge status
            filtered_prs = []
            for pr in prs:
                # Only include merged PRs if state is closed
                if state == "closed" and not pr.get("merged_at"):
                    continue
                    
                # Check if PR was updated within the time period
                updated_at = pr.get("updated_at")
                if updated_at and updated_at >= since_date:
                    # Extract relevant information
                    filtered_prs.append({
                        "number": pr.get("number"),
                        "title": pr.get("title"),
                        "description": pr.get("body") or "",
                        "author": pr.get("user", {}).get("login"),
                        "merged_at": pr.get("merged_at"),
                        "html_url": pr.get("html_url"),
                        "labels": [label.get("name") for label in pr.get("labels", [])]
                    })
            
            return filtered_prs
            
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to fetch PRs from GitHub: {str(e)}")
    
    def get_pr_diff(self, repo: str, pr_number: int) -> str:
        """
        Get the diff for a specific PR.

        Args:
            repo: Repository in format "owner/repo"
            pr_number: PR number
            
        Returns:
            Diff content as string
        """
        url = f"{self.base_url}/repos/{repo}/pulls/{pr_number}"
        
        try:
            # Request diff format
            headers = self.headers.copy()
            headers["Accept"] = "application/vnd.github.v3.diff"
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            return response.text
            
        except requests.exceptions.RequestException as e:
            # Return empty string on error, as diff is optional
            return "" 