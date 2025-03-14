import json
import sqlite3
import os
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

class ChangelogStorage:
    """Storage layer for changelog data using SQLite."""
    
    def __init__(self, db_path: str = "changelog.db"):
        """
        Initialize the storage with a SQLite database.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self._initialize_db()
    
    def _initialize_db(self) -> None:
        """Create the database tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create repositories table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS repositories (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            url TEXT,
            last_updated TEXT
        )
        ''')
        
        # Create changelogs table (key-value store)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS changelogs (
            repo_id TEXT,
            data TEXT,  -- JSON blob
            PRIMARY KEY (repo_id),
            FOREIGN KEY (repo_id) REFERENCES repositories(id)
        )
        ''')
        
        # Create users table for GitHub authentication
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            github_id TEXT UNIQUE NOT NULL,
            username TEXT NOT NULL,
            email TEXT,
            avatar_url TEXT,
            access_token TEXT,
            created_at TEXT,
            last_login TEXT
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_repository(self, repo_id: str, name: str, url: Optional[str] = None) -> None:
        """
        Add or update a repository.
        
        Args:
            repo_id: Unique identifier for the repository
            name: Display name for the repository
            url: GitHub URL for the repository
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT OR REPLACE INTO repositories (id, name, url, last_updated) VALUES (?, ?, ?, ?)",
            (repo_id, name, url, datetime.now().isoformat())
        )
        
        conn.commit()
        conn.close()
    
    def get_repositories(self) -> List[Dict[str, Any]]:
        """
        Get all repositories.
        
        Returns:
            List of repository dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM repositories ORDER BY name")
        repos = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return repos
    
    def save_changelog(self, repo_id: str, changelog_data: Dict[str, Any]) -> None:
        """
        Save changelog data for a repository.
        
        Args:
            repo_id: Repository identifier
            changelog_data: Changelog data dictionary
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Update the repository's last_updated timestamp
        cursor.execute(
            "UPDATE repositories SET last_updated = ? WHERE id = ?",
            (datetime.now().isoformat(), repo_id)
        )
        
        # Save the changelog data
        cursor.execute(
            "INSERT OR REPLACE INTO changelogs (repo_id, data) VALUES (?, ?)",
            (repo_id, json.dumps(changelog_data))
        )
        
        conn.commit()
        conn.close()
    
    def get_changelog(self, repo_id: str) -> Optional[Dict[str, Any]]:
        """
        Get changelog data for a repository.
        
        Args:
            repo_id: Repository identifier
            
        Returns:
            Changelog data dictionary or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT data FROM changelogs WHERE repo_id = ?", (repo_id,))
        row = cursor.fetchone()

        conn.close()

        if row:
            return json.loads(row[0])
        return None
    
    def add_changelog_entry(self, repo_id: str, date: str, entry: Dict[str, Any]) -> None:
        """
        Add a new entry to a repository's changelog.
        
        Args:
            repo_id: Repository identifier
            date: Date string (YYYY-MM-DD)
            entry: Changelog entry dictionary
        """
        changelog = self.get_changelog(repo_id) or {
            "repo": repo_id,
            "generated_at": datetime.now().isoformat(),
            "changes": []
        }
        
        # Add the entry with the date included in the entry
        entry["date"] = date
        changelog["changes"].append(entry)

        # Save the updated changelog
        self.save_changelog(repo_id, changelog)

    def delete_repository(self, repo_id: str) -> None:
        """
        Delete a repository and its changelog.
        
        Args:
            repo_id: Repository identifier
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Delete the changelog first (foreign key constraint)
        cursor.execute("DELETE FROM changelogs WHERE repo_id = ?", (repo_id,))
        
        # Delete the repository
        cursor.execute("DELETE FROM repositories WHERE id = ?", (repo_id,))
        
        conn.commit()
        conn.close()

    def get_user_by_github_id(self, github_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a user by their GitHub ID.
        
        Args:
            github_id: GitHub user ID
            
        Returns:
            User dictionary or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE github_id = ?", (github_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def create_or_update_user(self, github_id: str, username: str, email: Optional[str] = None,
                             avatar_url: Optional[str] = None, access_token: Optional[str] = None) -> int:
        """
        Create a new user or update an existing one.
        
        Args:
            github_id: GitHub user ID
            username: GitHub username
            email: User email
            avatar_url: URL to user's avatar
            access_token: GitHub OAuth access token
            
        Returns:
            User ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE github_id = ?", (github_id,))
        row = cursor.fetchone()
        
        now = datetime.now().isoformat()
        
        if row:
            # Update existing user
            cursor.execute(
                """
                UPDATE users 
                SET username = ?, email = ?, avatar_url = ?, 
                    access_token = ?, last_login = ?
                WHERE github_id = ?
                """,
                (username, email, avatar_url, access_token, now, github_id)
            )
            user_id = row[0]
        else:
            # Create new user
            cursor.execute(
                """
                INSERT INTO users 
                (github_id, username, email, avatar_url, access_token, created_at, last_login)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (github_id, username, email, avatar_url, access_token, now, now)
            )
            user_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return user_id 

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a user by their ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User dictionary or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return dict(row)
        return None 