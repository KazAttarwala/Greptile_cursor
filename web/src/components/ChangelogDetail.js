import React from 'react';
import { useParams, Link } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import './ChangelogDetail.css';

function ChangelogDetail({ changelog }) {
  const { versionId } = useParams();
  
  if (!changelog) {
    return <div className="empty-state">No changelog data available</div>;
  }
  
  // Find the specific version
  const version = changelog.versions?.find(v => v.id === versionId);
  
  if (!version) {
    return (
      <div className="not-found">
        <h2>Version not found</h2>
        <p>The requested version could not be found.</p>
        <Link to="/" className="back-link">Back to changelog</Link>
      </div>
    );
  }

  return (
    <div className="changelog-detail">
      <div className="version-header">
        <h2>{version.name}</h2>
        <div className="version-meta">
          <span className="version-date">
            {new Date(version.date).toLocaleDateString('en-US', {
              year: 'numeric',
              month: 'long',
              day: 'numeric'
            })}
          </span>
        </div>
      </div>
      
      {version.summary && (
        <div className="version-summary">
          <ReactMarkdown>{version.summary}</ReactMarkdown>
        </div>
      )}
      
      <div className="version-changes">
        {Object.entries(version.categories || {}).map(([category, changes]) => (
          <div key={category} className="category-section">
            <h3 className="category-title">{category}</h3>
            
            <ul className="category-changes">
              {changes.map(change => (
                <li key={change.pr_number} className="change-item">
                  <div className="change-content">
                    <span className="change-summary">{change.summary}</span>
                    
                    {change.details && (
                      <div className="change-details">
                        <ReactMarkdown>{change.details}</ReactMarkdown>
                      </div>
                    )}
                  </div>
                  
                  <a 
                    href={change.pr_url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="pr-link"
                  >
                    #{change.pr_number}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
      
      <div className="version-navigation">
        <Link to="/" className="back-link">Back to all changes</Link>
      </div>
    </div>
  );
}

export default ChangelogDetail; 