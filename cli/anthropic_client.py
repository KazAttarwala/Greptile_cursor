import json
import os
import requests
from typing import List, Dict, Any, Optional
import time

class AnthropicClient:
    """Client for interacting with Anthropic Claude API for changelog generation."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-sonnet-20240229"):
        """
        Initialize the Anthropic client.
        
        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            model: The model to use (default: claude-3-sonnet-20240229)
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key is required. Set ANTHROPIC_API_KEY environment variable or pass api_key parameter.")
        
        self.model = model
        self.api_endpoint = "https://api.anthropic.com/v1/messages"
        self.headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
    
    def _make_request(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Make a request to the Anthropic API."""
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1024,
            "temperature": 0.2
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        try:
            response = requests.post(
                self.api_endpoint, 
                headers=self.headers, 
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get("content", [{}])[0].get("text", "")
            
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to Anthropic API: {str(e)}")
    
    def generate_changelog_entry(self, pr_title: str, pr_description: str, 
                                 pr_diff: Optional[str] = None) -> Dict[str, str]:
        """
        Generate a changelog entry from PR information.
        
        Args:
            pr_title: The title of the PR
            pr_description: The description of the PR
            pr_diff: Optional diff content to provide more context
            
        Returns:
            Dictionary with generated changelog entry and metadata
        """
        # Create a system prompt for better results
        system_prompt = """
        You are an expert at writing clear, concise changelog entries. 
        Focus on what matters to users, not implementation details.
        Always format your response as valid JSON with the fields: summary, details, and type.
        """
        
        # Create a prompt that will generate a good changelog entry
        prompt = f"""
        Generate a concise, user-friendly changelog entry based on this pull request.
        
        PR Title: {pr_title}
        PR Description: {pr_description}
        
        {"Code Changes: " + pr_diff[:1000] + "..." if pr_diff else ""}
        
        Please format your response as JSON with the following fields:
        - summary: A clear, concise summary (max 100 chars)
        - details: Additional details if needed (max 250 chars)
        - type: The type of change (feature, bugfix, improvement, breaking, docs)
        
        Focus on what matters to users, not implementation details.
        """
        
        response = self._make_request(prompt, system_prompt)
        
        # Try to parse JSON from the response
        try:
            # First attempt to find JSON in the response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                result = json.loads(json_str)
                return result
            
            # If no JSON found, create a structured response
            return {
                "summary": response[:100].strip(),
                "details": "",
                "type": "other"
            }
            
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "summary": response[:100].strip(),
                "details": response[100:350].strip() if len(response) > 100 else "",
                "type": "other"
            }
    
    def categorize_changes(self, prs: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Categorize a list of PRs into logical groups.
        
        Args:
            prs: List of PR dictionaries with title, description, etc.
            
        Returns:
            Dictionary with categories as keys and lists of PRs as values
        """
        if not prs:
            return {}
            
        # Create a system prompt for better results
        system_prompt = """
        You are an expert at organizing changelog entries into logical categories.
        Always respond with valid JSON that maps category names to arrays of PR numbers.
        """
            
        # Create a prompt to categorize multiple PRs
        pr_list = "\n".join([
            f"PR #{i+1}: {pr.get('title', 'No title')} - {pr.get('description', 'No description')[:100]}"
            for i, pr in enumerate(prs[:10])  # Limit to 10 PRs to avoid token limits
        ])
        
        prompt = f"""
        Categorize these pull requests into logical groups for a changelog.
        
        {pr_list}
        
        Return your response as JSON with category names as keys and lists of PR numbers as values.
        Example: {{"Features": [1, 3], "Bug Fixes": [2, 4]}}
        
        Use standard changelog categories: Features, Bug Fixes, Performance Improvements, 
        Breaking Changes, Documentation, and Other.
        """
        
        response = self._make_request(prompt, system_prompt)
        
        try:
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                categories = json.loads(json_str)
                
                # Convert PR numbers back to PR objects
                result = {}
                for category, pr_nums in categories.items():
                    result[category] = [prs[num-1] for num in pr_nums if 0 < num <= len(prs)]
                return result
            
            # Fallback to simple categorization
            return {"Other": prs}
            
        except (json.JSONDecodeError, IndexError):
            # Fallback if parsing fails
            return {"Other": prs}
    
    def generate_version_summary(self, version: str, changes: List[Dict[str, Any]]) -> str:
        """
        Generate a high-level summary for a version release.
        
        Args:
            version: Version number
            changes: List of changes in this version
            
        Returns:
            A markdown formatted summary
        """
        if not changes:
            return f"## {version}\n\nNo significant changes in this release."
        
        # Create a system prompt for better results
        system_prompt = """
        You are an expert at writing clear, engaging version summaries for software releases.
        Focus on user benefits and key improvements. Use markdown formatting.
        """
        
        # Create a summary of changes
        changes_summary = "\n".join([
            f"- {change.get('summary', 'Unnamed change')}"
            for change in changes[:5]  # Limit to top 5 changes
        ])
        
        prompt = f"""
        Write a brief, engaging summary for version {version} of our software.
        
        Key changes in this release:
        {changes_summary}
        
        Format your response in markdown, starting with a brief overview paragraph,
        then highlighting 1-2 most important changes. Keep it under 150 words total.
        Focus on user benefits, not technical details.
        """
        
        response = self._make_request(prompt, system_prompt)
        
        # Ensure the response starts with the version header
        if not response.strip().startswith(f"## {version}"):
            response = f"## {version}\n\n{response}"
            
        return response 