from flask import Flask, jsonify, request, send_from_directory, redirect, url_for, session
from flask_cors import CORS
import os
import sys
from datetime import datetime, timedelta
from functools import wraps
from authlib.integrations.flask_client import OAuth

# Add the CLI directory to the path so we can import the storage module
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'cli'))
from storage import ChangelogStorage

app = Flask(__name__, static_folder='build')
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev_key_change_this_in_production')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Configure CORS to allow requests from your React frontend
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)

# Initialize storage
storage = ChangelogStorage(os.path.join(os.path.dirname(__file__), '..', 'data', 'changelog.db'))

# Ensure the data directory exists
os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'data'), exist_ok=True)

# Setup OAuth
oauth = OAuth(app)
oauth.register(
    name='github',
    client_id=os.environ.get('GITHUB_CLIENT_ID'),
    client_secret=os.environ.get('GITHUB_CLIENT_SECRET'),
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'},
)

# Authentication decorator
def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'access_token' not in session:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/auth/login')
def login():
    redirect_uri = url_for('authorized', _external=True)
    return oauth.github.authorize_redirect(redirect_uri)

@app.route('/api/auth/logout')
def logout():
    session.pop('access_token', None)
    session.pop('user_id', None)
    return jsonify({"success": True})

@app.route('/api/auth/callback')
def authorized():
    token = oauth.github.authorize_access_token()
    if not token:
        return redirect('/login?error=access_denied')
    
    session['access_token'] = token['access_token']
    
    # Get user info from GitHub
    resp = oauth.github.get('user', token=token)
    if resp.status_code != 200:
        return redirect('/login?error=github_api_error')
    
    user_data = resp.json()
    
    # Get user email if not public
    if not user_data.get('email'):
        emails_resp = oauth.github.get('user/emails', token=token)
        if emails_resp.status_code == 200:
            emails = emails_resp.json()
            primary_email = next((email for email in emails if email.get('primary')), None)
            if primary_email:
                user_data['email'] = primary_email.get('email')
    
    # Save user to database
    user_id = storage.create_or_update_user(
        github_id=str(user_data.get('id')),
        username=user_data.get('login'),
        email=user_data.get('email'),
        avatar_url=user_data.get('avatar_url'),
        access_token=token['access_token']
    )
    
    session['user_id'] = user_id
    
    # Redirect to frontend
    return redirect('/')

@app.route('/api/auth/user')
def get_user():
    if 'access_token' not in session:
        return jsonify({"authenticated": False})
    
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"authenticated": False})
    
    # Get user from database by ID
    # This would require adding a method to your storage class
    # For now, we'll just return basic info
    return jsonify({
        "authenticated": True,
        "user_id": user_id
    })

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
@auth_required
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
@auth_required
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
@auth_required
def delete_repo(repo_id):
    """Delete a repository."""
    storage.delete_repository(repo_id)
    return jsonify({"success": True})

@app.route('/api/repos/<repo_id>/entries', methods=['POST'])
@auth_required
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
    app.run(debug=True, port=5001)