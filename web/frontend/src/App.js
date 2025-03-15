import React, { useState, useEffect } from 'react';
import './App.css';
import Dashboard from './components/Dashboard';

function App() {
  const [repositories, setRepositories] = useState([]);
  const [selectedRepo, setSelectedRepo] = useState(null);
  const [changelog, setChangelog] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Fetch user and repositories on component mount
  useEffect(() => {
    // Check for error parameters in URL
    const urlParams = new URLSearchParams(window.location.search);
    const errorParam = urlParams.get('error');
    
    if (errorParam) {
      if (errorParam === 'access_denied') {
        setError('GitHub access was denied or canceled.');
      } else if (errorParam === 'github_api_error') {
        setError('Error accessing GitHub API. Please try again.');
      } else {
        setError(`Authentication error: ${errorParam}`);
      }
    }
    
    checkAuthStatus();
  }, []);

  // Check if user is authenticated
  const checkAuthStatus = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/auth/user', {
        credentials: 'include'
      });
      const data = await response.json();
      
      setIsAuthenticated(data.authenticated);
      if (data.authenticated) {
        setUser(data);
        fetchRepositories();
      }
    } catch (err) {
      console.error('Error checking authentication status:', err);
      setIsAuthenticated(false);
    }
  };

  // Handle login
  const handleLogin = () => {
    window.location.href = 'http://localhost:5001/api/auth/login';
  };

  // Handle logout
  const handleLogout = async () => {
    try {
      await fetch('http://localhost:5001/api/auth/logout', {
        credentials: 'include'
      });
      setIsAuthenticated(false);
      setUser(null);
      setSelectedRepo(null);
      setChangelog(null);
    } catch (err) {
      console.error('Error logging out:', err);
    }
  };

  // Fetch repositories from the API
  const fetchRepositories = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:5001/api/repos', {
        credentials: 'include'
      });
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
      const response = await fetch(`http://localhost:5001/api/repos/${repoId}/changelog`, {
        credentials: 'include'
      });
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
    if (!selectedRepo || !isAuthenticated) return;

    try {
      setLoading(true);
      const response = await fetch(`http://localhost:5001/api/repos/${selectedRepo.id}/entries`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
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
        <div className="auth-container">
          {isAuthenticated ? (
            <div className="user-info">
              {user?.avatar_url && (
                <img 
                  src={user.avatar_url} 
                  alt={user.username} 
                  className="avatar"
                />
              )}
              <span className="username">{user?.username || 'User'}</span>
              <button onClick={handleLogout} className="logout-btn">Logout</button>
            </div>
          ) : (
            <button onClick={handleLogin} className="login-btn">Login with GitHub</button>
          )}
        </div>
      </header>

      {!isAuthenticated ? (
        <div className="login-prompt">
          <h2>Welcome to Changelog Viewer</h2>
          {error && <div className="auth-error">{error}</div>}
          <p>Please login with GitHub to access your repositories and changelogs.</p>
          <button onClick={handleLogin} className="login-btn-large">Login with GitHub</button>
        </div>
      ) : (
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
                <Dashboard repository={selectedRepo} changelog={changelog} />
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
      )}
    </div>
  );
}

export default App;
