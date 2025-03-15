import React, { useState, useEffect } from 'react';
import './App.css';
import Dashboard from './components/Dashboard';

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
      const response = await fetch('http://localhost:5001/api/repos');
      const data = await response.json();
      setRepositories(data);
      
      // If repositories are available, select the first one by default
      if (data.length > 0) {
        setSelectedRepo(data[0]);
        fetchChangelog(data[0].id);
      }
      
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
      const response = await fetch(`http://localhost:5001/api/repos/${repoId}/changelog`);
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
              <div className="dashboard-actions">
                <h2>{selectedRepo.name}</h2>
              </div>
              <Dashboard 
                repository={selectedRepo} 
                changelog={changelog} 
              />
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
