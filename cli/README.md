# Changelog Generator CLI

An AI-powered changelog generator that creates user-friendly changelog entries from GitHub pull requests.

## Features

- Generate changelogs from GitHub PRs automatically
- Create changelog entries for specific PRs
- Authenticate with GitHub to discover repositories
- Categorize changes into logical groups
- Format changelogs as markdown
- Store changelog data in a local database
- Web interface for viewing changelogs

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   ```
   ANTHROPIC_API_KEY=your_anthropic_api_key
   GITHUB_CLIENT_ID=your_github_oauth_client_id
   GITHUB_CLIENT_SECRET=your_github_oauth_client_secret
   ```

## Usage

### Authentication

Authenticate with GitHub to access your repositories:

```
python cli/main.py auth
```

This will open a browser window for GitHub authentication. After authenticating, the CLI will store your GitHub token for future use.

### Discovering Repositories

Automatically discover repositories you have access to:

```
python cli/main.py discover
```

This will fetch all repositories you have access to and add them to the changelog database.

### Generating Changelogs

Generate a changelog for a specific PR:

```
python cli/main.py generate --repo repo-id --pr 123 --include-diff
```

Generate a changelog for recent PRs:

```
python cli/main.py generate --repo repo-id --days 30 --include-diff
```

### Adding Manual Entries

Add a manual changelog entry:

```
python cli/main.py add --repo repo-id --summary "Added new feature" --details "Description of the feature" --type feature
```

### Previewing Changelogs

Preview the changelog for a repository:

```
python cli/main.py preview --repo repo-id
```

### Publishing Changelogs

Publish the changelog for a repository:

```
python cli/main.py publish --repo repo-id --version v1.0.0
```

### Listing Repositories

List all repositories in the changelog database:

```
python cli/main.py list
```

## Web Interface

The web interface allows you to view changelogs in a user-friendly format.

To start the web interface:

```
python web/app.py
```

Then open your browser to http://localhost:5001

## How It Works

1. The CLI fetches PR information from GitHub
2. It uses Claude AI to generate user-friendly changelog entries
3. The entries are stored in a local SQLite database
4. The web interface displays the changelogs in a user-friendly format

## Configuration

You can configure the CLI using environment variables or command-line arguments:

- `GITHUB_TOKEN`: GitHub personal access token
- `ANTHROPIC_API_KEY`: Anthropic API key
- `ANTHROPIC_MODEL`: Anthropic model to use (default: claude-3-7-sonnet-20250219)
- `GITHUB_CLIENT_ID`: GitHub OAuth client ID
- `GITHUB_CLIENT_SECRET`: GitHub OAuth client secret

## License

MIT 