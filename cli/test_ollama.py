#!/usr/bin/env python3
import sys
from ollama_client import OllamaClient

def test_changelog_generation():
    """Test the changelog generation functionality."""
    client = OllamaClient()
    
    # Test with a sample PR
    pr_title = "Add user authentication system"
    pr_description = """
    This PR implements a complete user authentication system with:
    - Login/logout functionality
    - Password reset
    - Email verification
    - OAuth integration with Google and GitHub
    
    Fixes issues #123 and #124
    """
    
    print("Generating changelog entry...")
    entry = client.generate_changelog_entry(pr_title, pr_description)
    
    print("\nGenerated Entry:")
    print(f"Summary: {entry.get('summary')}")
    print(f"Details: {entry.get('details')}")
    print(f"Type: {entry.get('type')}")
    
    # Test categorization
    prs = [
        {"title": "Add user authentication", "description": "Implements login/logout"},
        {"title": "Fix navbar display on mobile", "description": "Resolves responsive design issues"},
        {"title": "Update documentation", "description": "Improve installation instructions"},
        {"title": "Optimize database queries", "description": "Reduces load time by 30%"}
    ]
    
    print("\nCategorizing PRs...")
    categories = client.categorize_changes(prs)
    
    print("\nCategories:")
    for category, items in categories.items():
        print(f"\n{category}:")
        for item in items:
            print(f"- {item.get('title')}")
    
    # Test version summary
    changes = [
        {"summary": "Added user authentication system"},
        {"summary": "Fixed responsive design issues on mobile"},
        {"summary": "Improved documentation"},
        {"summary": "Optimized database performance"}
    ]
    
    print("\nGenerating version summary...")
    summary = client.generate_version_summary("v1.2.0", changes)
    
    print("\nVersion Summary:")
    print(summary)

if __name__ == "__main__":
    try:
        test_changelog_generation()
        print("\nAll tests completed successfully!")
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1) 