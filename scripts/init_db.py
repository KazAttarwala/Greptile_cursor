#!/usr/bin/env python3
import os
import sys
import json
from datetime import datetime, timedelta

# Add the CLI directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'cli'))
from storage import ChangelogStorage

def init_sample_data():
    """Initialize the database with sample data."""
    # Ensure the data directory exists
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Initialize storage
    db_path = os.path.join(data_dir, 'changelog.db')
    storage = ChangelogStorage(db_path)
    
    # Add sample repositories
    repos = [
        {
            "id": "frontend-app",
            "name": "Frontend Application",
            "url": "https://github.com/example/frontend"
        },
        {
            "id": "backend-api",
            "name": "Backend API Service",
            "url": "https://github.com/example/backend"
        },
        {
            "id": "mobile-app",
            "name": "Mobile Application",
            "url": "https://github.com/example/mobile"
        }
    ]
    
    for repo in repos:
        storage.add_repository(repo["id"], repo["name"], repo["url"])
        print(f"Added repository: {repo['name']}")
    
    # Add sample changelog data
    today = datetime.now()
    
    # Frontend app changelog
    frontend_changes = {
        "repo": "frontend-app",
        "generated_at": today.isoformat(),
        "changes": {
            today.strftime("%Y-%m-%d"): [
                {
                    "pr_number": 123,
                    "pr_url": "https://github.com/example/frontend/pull/123",
                    "author": "developer1",
                    "summary": "Added user authentication system",
                    "details": "Implemented login, registration, and password reset functionality",
                    "type": "feature"
                },
                {
                    "pr_number": 124,
                    "pr_url": "https://github.com/example/frontend/pull/124",
                    "author": "developer2",
                    "summary": "Fixed responsive layout issues on mobile devices",
                    "details": "Resolved navbar and sidebar display problems on small screens",
                    "type": "bugfix"
                }
            ],
            (today - timedelta(days=5)).strftime("%Y-%m-%d"): [
                {
                    "pr_number": 120,
                    "pr_url": "https://github.com/example/frontend/pull/120",
                    "author": "developer3",
                    "summary": "Improved performance of data loading",
                    "details": "Optimized API calls and implemented caching",
                    "type": "improvement"
                }
            ],
            (today - timedelta(days=10)).strftime("%Y-%m-%d"): [
                {
                    "pr_number": 115,
                    "pr_url": "https://github.com/example/frontend/pull/115",
                    "author": "developer1",
                    "summary": "Updated documentation for component usage",
                    "details": "Added examples and improved clarity of component documentation",
                    "type": "docs"
                }
            ]
        },
        "categories": {
            "Features": [123],
            "Bug Fixes": [124],
            "Improvements": [120],
            "Documentation": [115]
        }
    }
    
    # Backend API changelog
    backend_changes = {
        "repo": "backend-api",
        "generated_at": today.isoformat(),
        "changes": {
            today.strftime("%Y-%m-%d"): [
                {
                    "pr_number": 87,
                    "pr_url": "https://github.com/example/backend/pull/87",
                    "author": "developer4",
                    "summary": "Implemented rate limiting for API endpoints",
                    "details": "Added configurable rate limiting to prevent abuse",
                    "type": "feature"
                }
            ],
            (today - timedelta(days=3)).strftime("%Y-%m-%d"): [
                {
                    "pr_number": 85,
                    "pr_url": "https://github.com/example/backend/pull/85",
                    "author": "developer2",
                    "summary": "Fixed memory leak in connection pool",
                    "details": "Resolved issue with database connections not being properly closed",
                    "type": "bugfix"
                },
                {
                    "pr_number": 84,
                    "pr_url": "https://github.com/example/backend/pull/84",
                    "author": "developer5",
                    "summary": "Added new endpoints for user management",
                    "details": "Created API endpoints for user creation, deletion, and profile updates",
                    "type": "feature"
                }
            ]
        },
        "categories": {
            "Features": [87, 84],
            "Bug Fixes": [85]
        }
    }
    
    # Save the changelogs
    storage.save_changelog("frontend-app", frontend_changes)
    storage.save_changelog("backend-api", backend_changes)
    
    print("Added sample changelog data")
    print(f"Database initialized at: {db_path}")

if __name__ == "__main__":
    init_sample_data() 