import React, { useState, useEffect } from 'react';
import './App.css';
import Dashboard from './components/Dashboard';
import AddEntryModal from './components/AddEntryModal';

function App() {
  const [repositories, setRepositories] = useState([]);
  const [selectedRepo, setSelectedRepo] = useState(null);
  const [changelog, setChangelog] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isAddEntryModalOpen, setIsAddEntryModalOpen] = useState(false);

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

  // Open add entry modal
  const openAddEntryModal = () => {
    setIsAddEntryModalOpen(true);
  };

  // Close add entry modal
  const closeAddEntryModal = () => {
    setIsAddEntryModalOpen(false);
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
        <h1>Changelog Dashboard</h1>
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
          <h2>Welcome to Changelog Dashboard</h2>
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
                <div className="dashboard-actions">
                  <h2>{selectedRepo.name}</h2>
                  <button className="add-entry-btn" onClick={openAddEntryModal}>
                    Add New Entry
                  </button>
                </div>
                <Dashboard repository={selectedRepo} changelog={changelog} />
              </>
            ) : (
              <div className="no-selection">
                <p>Select a repository to view its changelog</p>
              </div>
            )}
          </div>
        </div>
      )}

      <AddEntryModal 
        isOpen={isAddEntryModalOpen} 
        onClose={closeAddEntryModal} 
        onSubmit={addEntry} 
      />
    </div>
  );
}

export default App;
