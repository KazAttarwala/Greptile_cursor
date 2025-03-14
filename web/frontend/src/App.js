import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [repositories, setRepositories] = useState([]);
  const [selectedRepo, setSelectedRepo] = useState(null);
  const [changelog, setChangelog] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch repositories on component mount
  useEffect(() => {
    fetchRepositories();
  }, []);

  // Fetch repositories from the API
  const fetchRepositories = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:5000/api/repos');
      const data = await response.json();
      setRepositories(data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch repositories');
      console.error('Error fetching repositories:', err);
    } finally {
      setLoading(false);
    }
  };

  // Fetch changelog for a specific repository
  const fetchChangelog = async (repoId) => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:5000/api/repos/${repoId}/changelog`);
      const data = await response.json();
      setChangelog(data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch changelog');
      console.error('Error fetching changelog:', err);
    } finally {
      setLoading(false);
    }
  };

  // Handle repository selection
  const handleRepoSelect = (repo) => {
    setSelectedRepo(repo);
    fetchChangelog(repo.id);
  };

  // Add a new changelog entry
  const addEntry = async (entry) => {
    if (!selectedRepo) return;

    try {
      setLoading(true);
      const response = await fetch(`http://localhost:5000/api/repos/${selectedRepo.id}/entries`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          date: new Date().toISOString().split('T')[0],
          entry: entry,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to add entry');
      }

      // Refresh changelog after adding entry
      await fetchChangelog(selectedRepo.id);
      setError(null);
    } catch (err) {
      setError('Failed to add entry');
      console.error('Error adding entry:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Changelog Viewer</h1>
      </header>

      <div className="container">
        <div className="sidebar">
          <h2>Repositories</h2>
          {loading && <p>Loading...</p>}
          {error && <p className="error">{error}</p>}
          <ul className="repo-list">
            {repositories.map((repo) => (
              <li
                key={repo.id}
                className={selectedRepo?.id === repo.id ? 'selected' : ''}
                onClick={() => handleRepoSelect(repo)}
              >
                {repo.name}
              </li>
            ))}
          </ul>
        </div>

        <div className="main-content">
          {selectedRepo ? (
            <>
              <h2>{selectedRepo.name} Changelog</h2>
              <div className="add-entry">
                <h3>Add New Entry</h3>
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    const formData = new FormData(e.target);
                    addEntry({
                      summary: formData.get('summary'),
                      details: formData.get('details'),
                      type: formData.get('type'),
                    });
                    e.target.reset();
                  }}
                >
                  <div className="form-group">
                    <label htmlFor="summary">Summary:</label>
                    <input
                      type="text"
                      id="summary"
                      name="summary"
                      required
                      placeholder="Brief description of the change"
                    />
                  </div>
                  <div className="form-group">
                    <label htmlFor="details">Details:</label>
                    <textarea
                      id="details"
                      name="details"
                      placeholder="Additional details (optional)"
                    />
                  </div>
                  <div className="form-group">
                    <label htmlFor="type">Type:</label>
                    <select id="type" name="type" required>
                      <option value="feature">Feature</option>
                      <option value="bugfix">Bug Fix</option>
                      <option value="improvement">Improvement</option>
                      <option value="docs">Documentation</option>
                      <option value="other">Other</option>
                    </select>
                  </div>
                  <button type="submit">Add Entry</button>
                </form>
              </div>

              <div className="changelog">
                {changelog?.changes?.map((change, index) => (
                  <div key={index} className="changelog-entry">
                    <div className="entry-header">
                      <span className="entry-type">{change.type}</span>
                      <span className="entry-date">
                        {new Date(change.date).toLocaleDateString()}
                      </span>
                    </div>
                    <h4>{change.summary}</h4>
                    {change.details && <p>{change.details}</p>}
                    {change.pr_number && (
                      <a
                        href={change.pr_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="pr-link"
                      >
                        PR #{change.pr_number}
                      </a>
                    )}
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="no-selection">
              <p>Select a repository to view its changelog</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
