from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import sys
import json
from datetime import datetime

# Add the CLI directory to the path so we can import the storage module
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'cli'))
from storage import ChangelogStorage

app = Flask(__name__, static_folder='build')
CORS(app)  # Enable CORS for all routes

# Initialize storage
storage = ChangelogStorage(os.path.join(os.path.dirname(__file__), '..', 'data', 'changelog.db'))

# Ensure the data directory exists
os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'data'), exist_ok=True)

@app.route('/api/repos', methods=['GET'])
def get_repos():
    """Get all repositories."""
    repos = storage.get_repositories()
    return jsonify(repos)

@app.route('/api/repos/<repo_id>/changelog', methods=['GET'])
def get_changelog(repo_id):
    """Get changelog for a specific repository."""
    changelog = storage.get_changelog(repo_id)
    
    if not changelog:
        return jsonify({"error": "Changelog not found"}), 404
    
    return jsonify(changelog)

@app.route('/api/repos/<repo_id>/changelog', methods=['POST'])
def update_changelog(repo_id):
    """Update or create a changelog for a repository."""
    data = request.json
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Ensure the repository exists
    repos = storage.get_repositories()
    repo_exists = any(repo['id'] == repo_id for repo in repos)
    
    if not repo_exists:
        return jsonify({"error": "Repository not found"}), 404
    
    # Save the changelog
    storage.save_changelog(repo_id, data)
    
    return jsonify({"success": True})

@app.route('/api/repos', methods=['POST'])
def add_repo():
    """Add a new repository."""
    data = request.json
    
    if not data or 'id' not in data or 'name' not in data:
        return jsonify({"error": "Invalid repository data"}), 400
    
    storage.add_repository(
        repo_id=data['id'],
        name=data['name'],
        url=data.get('url')
    )
    
    return jsonify({"success": True})

@app.route('/api/repos/<repo_id>', methods=['DELETE'])
def delete_repo(repo_id):
    """Delete a repository."""
    storage.delete_repository(repo_id)
    return jsonify({"success": True})

@app.route('/api/repos/<repo_id>/entries', methods=['POST'])
def add_entry(repo_id):
    """Add a new changelog entry."""
    data = request.json
    
    if not data or 'date' not in data or 'entry' not in data:
        return jsonify({"error": "Invalid entry data"}), 400
    
    # Ensure the repository exists
    repos = storage.get_repositories()
    repo_exists = any(repo['id'] == repo_id for repo in repos)
    
    if not repo_exists:
        return jsonify({"error": "Repository not found"}), 404
    
    # Add the entry
    storage.add_changelog_entry(
        repo_id=repo_id,
        date=data['date'],
        entry=data['entry']
    )
    
    return jsonify({"success": True})

# Serve the React app for all other routes
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000) 