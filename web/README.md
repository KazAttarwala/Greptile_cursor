# Changelog Generator Web App

A web application for generating and managing changelogs for your GitHub repositories.

## Features

- GitHub authentication
- View and manage repositories
- Generate changelogs from GitHub PRs
- Add manual changelog entries
- Categorize changes by type
- Export changelogs in markdown format

## Setup

### Prerequisites

- Python 3.7+
- Node.js 14+
- npm or yarn
- GitHub account

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

   Or install the core dependencies manually:
   ```
   pip install flask flask-cors authlib flask-login requests python-dotenv
   ```

3. Install frontend dependencies:
   ```
   cd web/frontend
   npm install
   ```

### Setting up GitHub OAuth

1. Run the setup script:
   ```
   cd web
   ./setup_github_oauth.sh
   ```

2. Follow the instructions to create a GitHub OAuth application and enter the credentials.

3. Alternatively, you can manually create a GitHub OAuth application:
   - Go to [GitHub Developer Settings](https://github.com/settings/developers)
   - Click "New OAuth App"
   - Fill in the application details:
     - Application name: Changelog Generator
     - Homepage URL: http://localhost:5001
     - Authorization callback URL: http://localhost:5001/api/auth/callback
   - Create a `.env` file in the project root with the following content:
     ```
     GITHUB_CLIENT_ID=your_client_id
     GITHUB_CLIENT_SECRET=your_client_secret
     FLASK_SECRET_KEY=your_secret_key
     FLASK_APP=web/app.py
     FLASK_ENV=development
     ```

## Running the Application

1. Load the environment variables:
   ```
   source .env
   ```

2. Start the Flask backend:
   ```
   python web/app.py
   ```

3. In a separate terminal, start the React frontend:
   ```
   cd web/frontend
   npm start
   ```

4. Open your browser and navigate to:
   ```
   http://localhost:3000
   ```

5. Click "Login with GitHub" to authenticate with your GitHub account.

## Troubleshooting

### Authentication Issues

If you encounter authentication issues:

1. Make sure your GitHub OAuth credentials are correct in the `.env` file
2. Check that the callback URL in your GitHub OAuth app settings matches exactly: `http://localhost:5001/api/auth/callback`
3. Ensure cookies are enabled in your browser
4. Try clearing your browser cookies and cache

### CORS Issues

If you encounter CORS issues:

1. Make sure the frontend is running on `http://localhost:3000`
2. Check that the backend CORS configuration allows requests from `http://localhost:3000`
3. Ensure credentials are included in all API requests

## Usage

After logging in with your GitHub account, you can:

1. Add repositories to track
2. Generate changelogs from GitHub PRs
3. Add manual changelog entries
4. View and filter changelog entries
5. Export changelogs in markdown format

## Development

### Backend

The backend is built with Flask and uses SQLite for storage. The main components are:

- `app.py`: Main Flask application
- `storage.py`: Database operations
- `github_client.py`: GitHub API client
- `changelog_generator.py`: Changelog generation logic

### Frontend

The frontend is built with React and uses the Fetch API to communicate with the backend. The main components are:

- `App.js`: Main React component
- `App.css`: Styles for the application

## License

MIT 