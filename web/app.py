from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import sys
from datetime import datetime, timedelta

# Add the CLI directory to the path so we can import the storage module
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'cli'))
from storage import ChangelogStorage

app = Flask(__name__, static_folder='build')
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev_key_change_this_in_production')

# Configure CORS to allow requests from any origin
CORS(app)

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

# Serve the React app for all other routes
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)