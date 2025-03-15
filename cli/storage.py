import json
import sqlite3
import os
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import uuid

class ChangelogStorage:
    """Storage for changelog data using SQLite."""
    
    def __init__(self, db_path: str = "changelog.db"):
        """
        Initialize the storage.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self._initialize_db()
    
    def _initialize_db(self) -> None:
        """Initialize the database schema if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create repositories table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS repositories (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            url TEXT,
            current_version TEXT,
            last_updated TEXT
        )
        ''')
        
        # Create changelog entries table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS changelog_entries (
            id TEXT PRIMARY KEY,
            repo_id TEXT NOT NULL,
            pr_number INTEGER,
            pr_url TEXT,
            author TEXT,
            date TEXT NOT NULL,
            summary TEXT NOT NULL,
            details TEXT,
            type TEXT,
            labels TEXT,
            FOREIGN KEY (repo_id) REFERENCES repositories (id)
        )
        ''')
        
        # Create versions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS versions (
            id TEXT PRIMARY KEY,
            repo_id TEXT NOT NULL,
            version TEXT NOT NULL,
            release_date TEXT,
            description TEXT,
            is_breaking BOOLEAN DEFAULT 0,
            FOREIGN KEY (repo_id) REFERENCES repositories (id)
        )
        ''')
        
        # Create version_entries table (for mapping entries to versions)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS version_entries (
            version_id TEXT NOT NULL,
            entry_id TEXT NOT NULL,
            PRIMARY KEY (version_id, entry_id),
            FOREIGN KEY (version_id) REFERENCES versions (id),
            FOREIGN KEY (entry_id) REFERENCES changelog_entries (id)
        )
        ''')
        
        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            github_id TEXT UNIQUE,
            username TEXT NOT NULL,
            email TEXT,
            avatar_url TEXT,
            access_token TEXT,
            created_at TEXT NOT NULL,
            last_login TEXT
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_repository(self, repo_id: str, name: str, url: Optional[str] = None, current_version: Optional[str] = None) -> None:
        """
        Add or update a repository.
        
        Args:
            repo_id: Repository ID
            name: Repository name
            url: Repository URL
            current_version: Current version
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if repository already exists
        cursor.execute("SELECT id FROM repositories WHERE id = ?", (repo_id,))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing repository
            cursor.execute(
                "UPDATE repositories SET name = ?, url = ?, current_version = ?, last_updated = ? WHERE id = ?",
                (name, url, current_version, datetime.now().isoformat(), repo_id)
            )
        else:
            # Insert new repository
            cursor.execute(
                "INSERT INTO repositories (id, name, url, current_version, last_updated) VALUES (?, ?, ?, ?, ?)",
                (repo_id, name, url, current_version, datetime.now().isoformat())
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
        
        cursor.execute("SELECT * FROM repositories ORDER BY last_updated DESC")
        rows = cursor.fetchall()
        
        repositories = []
        for row in rows:
            repositories.append(dict(row))
        
        conn.close()
        return repositories
    
    def save_changelog(self, repo_id: str, changelog_data: Dict[str, Any]) -> None:
        """
        Save a complete changelog for a repository.
        
        Args:
            repo_id: Repository ID
            changelog_data: Changelog data dictionary
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Update repository last_updated timestamp
        cursor.execute(
            "UPDATE repositories SET last_updated = ? WHERE id = ?",
            (datetime.now().isoformat(), repo_id)
        )
        
        # Delete existing entries for this repository
        cursor.execute("DELETE FROM changelog_entries WHERE repo_id = ?", (repo_id,))
        
        # Insert new entries
        changes = changelog_data.get("changes", [])
        for change in changes:
            # Generate a unique ID for the entry
            entry_id = str(uuid.uuid4())
            
            # Convert labels to JSON string if present
            labels_json = json.dumps(change.get("labels", [])) if change.get("labels") else None
            
            cursor.execute(
                """
                INSERT INTO changelog_entries 
                (id, repo_id, pr_number, pr_url, author, date, summary, details, type, labels)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entry_id,
                    repo_id,
                    change.get("pr_number"),
                    change.get("pr_url"),
                    change.get("author"),
                    change.get("date"),
                    change.get("summary"),
                    change.get("details"),
                    change.get("type"),
                    labels_json
                )
            )
        
        conn.commit()
        conn.close()
    
    def get_changelog(self, repo_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the changelog for a repository.
        
        Args:
            repo_id: Repository ID
            
        Returns:
            Changelog data dictionary or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get repository info
        cursor.execute("SELECT * FROM repositories WHERE id = ?", (repo_id,))
        repo = cursor.fetchone()
        
        if not repo:
            conn.close()
            return None
        
        # Get changelog entries
        cursor.execute("SELECT * FROM changelog_entries WHERE repo_id = ? ORDER BY date DESC", (repo_id,))
        rows = cursor.fetchall()
        
        changes = []
        for row in rows:
            entry = dict(row)
            
            # Parse labels from JSON if present
            if entry.get("labels"):
                try:
                    entry["labels"] = json.loads(entry["labels"])
                except json.JSONDecodeError:
                    entry["labels"] = []
            else:
                entry["labels"] = []
            
            changes.append(entry)
        
        conn.close()
        
        return {
            "repo": repo_id,
            "generated_at": datetime.now().isoformat(),
            "changes": changes
        }
    
    def add_changelog_entry(self, repo_id: str, date: str, entry: Dict[str, Any]) -> str:
        """
        Add a single changelog entry.
        
        Args:
            repo_id: Repository ID
            date: Entry date (YYYY-MM-DD)
            entry: Entry data dictionary
            
        Returns:
            ID of the created entry
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if repository exists
        cursor.execute("SELECT id FROM repositories WHERE id = ?", (repo_id,))
        repo = cursor.fetchone()
        
        if not repo:
            conn.close()
            raise ValueError(f"Repository '{repo_id}' not found")
        
        # Update repository last_updated timestamp
        cursor.execute(
            "UPDATE repositories SET last_updated = ? WHERE id = ?",
            (datetime.now().isoformat(), repo_id)
        )
        
        # Check if entry with this PR number already exists
        pr_number = entry.get("pr_number")
        existing_id = None
        
        if pr_number:
            cursor.execute(
                "SELECT id FROM changelog_entries WHERE repo_id = ? AND pr_number = ?", 
                (repo_id, pr_number)
            )
            existing = cursor.fetchone()
            if existing:
                existing_id = existing[0]
        
        # Convert labels to JSON string if present
        labels_json = json.dumps(entry.get("labels", [])) if entry.get("labels") else None
        
        if existing_id:
            # Update existing entry
            cursor.execute(
                """
                UPDATE changelog_entries 
                SET pr_url = ?, author = ?, date = ?, summary = ?, details = ?, type = ?, labels = ?
                WHERE id = ?
                """,
                (
                    entry.get("pr_url"),
                    entry.get("author"),
                    entry.get("date"),
                    entry.get("summary"),
                    entry.get("details"),
                    entry.get("type"),
                    labels_json,
                    existing_id
                )
            )
            entry_id = existing_id
        else:
            # Generate a unique ID for the entry
            entry_id = str(uuid.uuid4())
            
            # Insert new entry
            cursor.execute(
                """
                INSERT INTO changelog_entries 
                (id, repo_id, pr_number, pr_url, author, date, summary, details, type, labels)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entry_id,
                    repo_id,
                    entry.get("pr_number"),
                    entry.get("pr_url"),
                    entry.get("author"),
                    entry.get("date"),
                    entry.get("summary"),
                    entry.get("details"),
                    entry.get("type"),
                    labels_json
                )
            )
        
        conn.commit()
        conn.close()
        
        return entry_id
    
    def update_changelog_entry(self, repo_id: str, entry_id: str, entry: Dict[str, Any]) -> None:
        """
        Update a changelog entry.
        
        Args:
            repo_id: Repository ID
            entry_id: Entry ID
            entry: Updated entry data
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if entry exists
        cursor.execute(
            "SELECT id FROM changelog_entries WHERE id = ? AND repo_id = ?", 
            (entry_id, repo_id)
        )
        existing = cursor.fetchone()
        
        if not existing:
            conn.close()
            raise ValueError(f"Entry '{entry_id}' not found for repository '{repo_id}'")
        
        # Update repository last_updated timestamp
        cursor.execute(
            "UPDATE repositories SET last_updated = ? WHERE id = ?",
            (datetime.now().isoformat(), repo_id)
        )
        
        # Convert labels to JSON string if present
        labels_json = json.dumps(entry.get("labels", [])) if entry.get("labels") else None
        
        # Update entry
        cursor.execute(
            """
            UPDATE changelog_entries 
            SET pr_number = ?, pr_url = ?, author = ?, date = ?, summary = ?, details = ?, type = ?, labels = ?
            WHERE id = ?
            """,
            (
                entry.get("pr_number"),
                entry.get("pr_url"),
                entry.get("author"),
                entry.get("date"),
                entry.get("summary"),
                entry.get("details"),
                entry.get("type"),
                labels_json,
                entry_id
            )
        )
        
        conn.commit()
        conn.close()
    
    def delete_repository(self, repo_id: str) -> None:
        """
        Delete a repository and all its changelog entries.
        
        Args:
            repo_id: Repository ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Delete version entries
        cursor.execute(
            """
            DELETE FROM version_entries 
            WHERE version_id IN (SELECT id FROM versions WHERE repo_id = ?)
            """, 
            (repo_id,)
        )
        
        # Delete versions
        cursor.execute("DELETE FROM versions WHERE repo_id = ?", (repo_id,))
        
        # Delete changelog entries
        cursor.execute("DELETE FROM changelog_entries WHERE repo_id = ?", (repo_id,))
        
        # Delete repository
        cursor.execute("DELETE FROM repositories WHERE id = ?", (repo_id,))
        
        conn.commit()
        conn.close()
    
    def add_version(self, repo_id: str, version: str, release_date: Optional[str] = None, 
                   description: Optional[str] = None, is_breaking: bool = False) -> str:
        """
        Add a version to a repository.
        
        Args:
            repo_id: Repository ID
            version: Version string
            release_date: Release date (ISO format)
            description: Version description
            is_breaking: Whether this is a breaking change
            
        Returns:
            ID of the created version
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if repository exists
        cursor.execute("SELECT id FROM repositories WHERE id = ?", (repo_id,))
        repo = cursor.fetchone()
        
        if not repo:
            conn.close()
            raise ValueError(f"Repository '{repo_id}' not found")
        
        # Check if version already exists
        cursor.execute(
            "SELECT id FROM versions WHERE repo_id = ? AND version = ?", 
            (repo_id, version)
        )
        existing = cursor.fetchone()
        
        if existing:
            conn.close()
            raise ValueError(f"Version '{version}' already exists for repository '{repo_id}'")
        
        # Generate a unique ID for the version
        version_id = str(uuid.uuid4())
        
        # Use current date if release_date not provided
        if not release_date:
            release_date = datetime.now().isoformat()
        
        # Insert version
        cursor.execute(
            """
            INSERT INTO versions 
            (id, repo_id, version, release_date, description, is_breaking)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                version_id,
                repo_id,
                version,
                release_date,
                description,
                1 if is_breaking else 0
            )
        )
        
        # Update repository current_version
        cursor.execute(
            "UPDATE repositories SET current_version = ?, last_updated = ? WHERE id = ?",
            (version, datetime.now().isoformat(), repo_id)
        )
        
        conn.commit()
        conn.close()
        
        return version_id
    
    def get_versions(self, repo_id: str) -> List[Dict[str, Any]]:
        """
        Get all versions for a repository.
        
        Args:
            repo_id: Repository ID
            
        Returns:
            List of version dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM versions WHERE repo_id = ? ORDER BY release_date DESC", 
            (repo_id,)
        )
        rows = cursor.fetchall()
        
        versions = []
        for row in rows:
            versions.append(dict(row))
        
        conn.close()
        return versions
    
    def get_user_by_github_id(self, github_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a user by GitHub ID.
        
        Args:
            github_id: GitHub user ID
            
        Returns:
            User dictionary or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE github_id = ?", (github_id,))
        user = cursor.fetchone()
        
        conn.close()
        
        if user:
            return dict(user)
        return None
    
    def create_or_update_user(self, github_id: str, username: str, email: Optional[str] = None,
                             avatar_url: Optional[str] = None, access_token: Optional[str] = None) -> int:
        """
        Create or update a user.
        
        Args:
            github_id: GitHub user ID
            username: GitHub username
            email: User email
            avatar_url: User avatar URL
            access_token: GitHub access token
            
        Returns:
            User ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE github_id = ?", (github_id,))
        user = cursor.fetchone()
        
        now = datetime.now().isoformat()
        
        if user:
            # Update existing user
            cursor.execute(
                """
                UPDATE users 
                SET username = ?, email = ?, avatar_url = ?, 
                    access_token = ?, last_login = ?
                WHERE github_id = ?
                """,
                (
                    username,
                    email,
                    avatar_url,
                    access_token,
                    now,
                    github_id
                )
            )
            user_id = user[0]
        else:
            # Insert new user
            cursor.execute(
                """
                INSERT INTO users 
                (github_id, username, email, avatar_url, access_token, created_at, last_login)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    github_id,
                    username,
                    email,
                    avatar_url,
                    access_token,
                    now,
                    now
                )
            )
            user_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return user_id
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User dictionary or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        conn.close()
        
        if user:
            return dict(user)
        return None
        
    def get_changelog_entry(self, repo_id: str, pr_number: int) -> Optional[Dict[str, Any]]:
        """
        Get a changelog entry by PR number.
        
        Args:
            repo_id: Repository ID
            pr_number: PR number
            
        Returns:
            Entry dictionary or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM changelog_entries WHERE repo_id = ? AND pr_number = ?", 
            (repo_id, pr_number)
        )
        entry = cursor.fetchone()
        
        conn.close()
        
        if entry:
            result = dict(entry)
            
            # Parse labels from JSON if present
            if result.get("labels"):
                try:
                    result["labels"] = json.loads(result["labels"])
                except json.JSONDecodeError:
                    result["labels"] = []
            else:
                result["labels"] = []
                
            return result
        return None 