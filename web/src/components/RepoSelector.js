import React from 'react';
import './RepoSelector.css';

function RepoSelector({ repos, selectedRepo, onSelectRepo }) {
  if (!repos || repos.length === 0) {
    return null;
  }

  return (
    <div className="repo-selector">
      <label htmlFor="repo-select">Repository:</label>
      <select 
        id="repo-select"
        value={selectedRepo?.id || ''}
        onChange={(e) => {
          const repo = repos.find(r => r.id === e.target.value);
          onSelectRepo(repo);
        }}
      >
        {repos.map(repo => (
          <option key={repo.id} value={repo.id}>
            {repo.name}
          </option>
        ))}
      </select>
    </div>
  );
}

export default RepoSelector; 