import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import ChangelogList from './components/ChangelogList';
import ChangelogDetail from './components/ChangelogDetail';
import RepoSelector from './components/RepoSelector';
import { fetchRepos, fetchChangelog } from './utils/api';
import './App.css';

function App() {
  const [repos, setRepos] = useState([]);
  const [selectedRepo, setSelectedRepo] = useState(null);
  const [changelog, setChangelog] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch available repositories on load
  useEffect(() => {
    const loadRepos = async () => {
      try {
        setLoading(true);
        const repoList = await fetchRepos();
        setRepos(repoList);
        
        // Select the first repo by default if available
        if (repoList.length > 0) {
          setSelectedRepo(repoList[0]);
        }
        
        setLoading(false);
      } catch (err) {
        setError('Failed to load repositories');
        setLoading(false);
      }
    };
    
    loadRepos();
  }, []);

  // Fetch changelog when selected repo changes
  useEffect(() => {
    const loadChangelog = async () => {
      if (!selectedRepo) return;
      
      try {
        setLoading(true);
        const changelogData = await fetchChangelog(selectedRepo.id);
        setChangelog(changelogData);
        setLoading(false);
      } catch (err) {
        setError('Failed to load changelog');
        setLoading(false);
      }
    };
    
    loadChangelog();
  }, [selectedRepo]);

  const handleRepoChange = (repo) => {
    setSelectedRepo(repo);
  };

  return (
    <Router>
      <div className="app">
        <Header />
        
        <main className="content">
          <RepoSelector 
            repos={repos} 
            selectedRepo={selectedRepo} 
            onSelectRepo={handleRepoChange} 
          />
          
          {loading ? (
            <div className="loading">Loading changelog data...</div>
          ) : error ? (
            <div className="error">{error}</div>
          ) : (
            <Routes>
              <Route 
                path="/" 
                element={<ChangelogList changelog={changelog} />} 
              />
              <Route 
                path="/version/:versionId" 
                element={<ChangelogDetail changelog={changelog} />} 
              />
            </Routes>
          )}
        </main>
        
        <footer className="footer">
          <p>Generated with AI-Powered Changelog Generator</p>
        </footer>
      </div>
    </Router>
  );
}

export default App; 