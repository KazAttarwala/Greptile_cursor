# AI-Powered Changelog Generator

A developer-friendly tool to automatically generate changelogs from GitHub pull requests using AI, with a clean web interface to display the results.

## Features

- 🤖 AI-powered changelog generation using Anthropic's Claude
- 🔄 Automatic categorization of changes
- 📝 Manual entry support
- 🌐 Clean, searchable web interface
- 🔍 Preview before publishing
- 📅 Chronological organization

## Setup

### Prerequisites

- Python 3.8+
- Node.js 14+
- Anthropic API key

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/changelog-generator.git
   cd changelog-generator
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install frontend dependencies:
   ```bash
   cd web
   npm install
   cd ..
   ```

4. Set up environment variables:
   ```bash
   export GITHUB_TOKEN=your_github_token
   export ANTHROPIC_API_KEY=your_anthropic_api_key
   export ANTHROPIC_MODEL=claude-3-7-sonnet-20250219  # or your preferred model
   ```

5. Initialize the database with sample data:
   ```bash
   python scripts/init_db.py
   ```

### Running the Application

1. Start the backend server:
   ```bash
   cd web
   python app.py
   ```

2. In a separate terminal, start the frontend development server:
   ```bash
   cd web
   npm start
   ```

3. Open your browser and navigate to `http://localhost:3000`

## CLI Usage

The CLI tool provides several commands for managing changelogs:

### Initialize a Repository

```bash
python cli/main.py init owner/repo --name "Display Name"
```

### Generate Changelog from PRs

```bash
python cli/main.py generate --repo repo-id --days 30
```

### Add a Manual Entry

```bash
python cli/main.py add --repo repo-id --summary "Added new feature" --type feature
```

### Preview Changelog

```bash
python cli/main.py preview --repo repo-id
```

### Publish Changelog

```bash
python cli/main.py publish --repo repo-id --version v1.0.0
```

### List Repositories

```bash
python cli/main.py list
```

## Web Interface

The web interface provides a clean, user-friendly way to browse changelogs:

- View changes organized by date
- Filter by category or search text
- See detailed information about each change
- Navigate between repositories

## API Reference

The backend provides the following API endpoints:

- `GET /api/repos` - List all repositories
- `GET /api/repos/{repo_id}/changelog` - Get changelog for a repository
- `POST /api/repos` - Add a new repository
- `POST /api/repos/{repo_id}/changelog` - Update a repository's changelog
- `POST /api/repos/{repo_id}/entries` - Add a new changelog entry
- `DELETE /api/repos/{repo_id}` - Delete a repository