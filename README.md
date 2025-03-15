# AI-Powered Changelog Generator

A developer-friendly tool to automatically generate changelogs from GitHub pull requests using AI, with a clean web interface to display the results.

## Notes for reviewers
I used Cursor and Anthropic for this project

I wanted to make the developer tool really simple without a need for manual intervention. So it works by initializing a Github repo and then specifying a number of days to look back in that repo. The code grabs all of the closed PRs in the specified timeframe and uses Anthropic's LLM
to autogenerate a changelog based on the diffs in the PRs. You can preview the changelog after it is generated and also create manual changelogs without AI.

The web UI shows an overview of recent activities in different repos as well as all of the changes for that repo. It also allows you to filter between categories of changes and search through changes.

Looking back there are several flaws with the system that I don't like
1. The cli forces you to manually add git repos. This could be improved by setting up a Github OAuth App and allowing the user to authenticate to Github in the CLI so we can pull and save their repos automatically.
2. The cli does not allow you to generate changelogs by branch, commit, or by PR. It only allows you to specify how far back you want to look and then it finds all closed PRs in that timeframe and generates a changelog for all diffs in those PRs. If I did this over I would allow the user to specify PRs, branches, or a range of commits to give more flexibility.
3. When a changelog is autogenerated for a repo the entire changelog history is reproduced! This is super inefficient and violates data integrity! If I redid the design I think I would only allow autogenerating a changelog per PR and if the PR number already exists in the database then a subsequent add would just replace the existing changelog for that PR number
4. The cli does not allow editing of a changelog during generation. I would like to add that capability.
5. The changelogs are not semantically versioned. I want to add versions so it is clear what version a developer would have to have to use the features in the changelog.
6. The cli of course would have to be deployed as a python package


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
python cli/main.py generate --repo repo-id --days 30 --include-diff
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