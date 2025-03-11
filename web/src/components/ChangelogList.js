import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import './ChangelogList.css';

function ChangelogList({ changelog }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');

  if (!changelog) {
    return <div className="empty-state">No changelog data available</div>;
  }

  // Extract all categories from the changelog
  const allCategories = ['All', ...new Set(
    Object.values(changelog.changes || [])
      .flatMap(change => change.type || 'Other')
  )];

  // Filter changes based on search and category
  const filteredChanges = Object.entries(changelog.changes || {})
    .filter(([date, changes]) => {
      // Filter by search term
      if (searchTerm) {
        return changes.some(change => 
          change.summary.toLowerCase().includes(searchTerm.toLowerCase()) ||
          (change.details && change.details.toLowerCase().includes(searchTerm.toLowerCase()))
        );
      }
      return true;
    })
    .filter(([date, changes]) => {
      // Filter by category
      if (selectedCategory !== 'All') {
        return changes.some(change => change.type === selectedCategory);
      }
      return true;
    })
    // Sort by date (newest first)
    .sort(([dateA], [dateB]) => new Date(dateB) - new Date(dateA));

  return (
    <div className="changelog-list">
      <div className="changelog-filters">
        <div className="search-container">
          <input
            type="text"
            placeholder="Search changes..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>
        
        <div className="category-filter">
          <label htmlFor="category-select">Category:</label>
          <select
            id="category-select"
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
          >
            {allCategories.map(category => (
              <option key={category} value={category}>
                {category}
              </option>
            ))}
          </select>
        </div>
      </div>

      {filteredChanges.length === 0 ? (
        <div className="empty-state">
          No changes match your filters
        </div>
      ) : (
        <div className="changelog-entries">
          {filteredChanges.map(([date, changes]) => (
            <div key={date} className="changelog-date-group">
              <h2 className="date-header">
                {new Date(date).toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric'
                })}
              </h2>
              
              <div className="changes-list">
                {changes
                  .filter(change => 
                    selectedCategory === 'All' || change.type === selectedCategory
                  )
                  .filter(change => 
                    !searchTerm || 
                    change.summary.toLowerCase().includes(searchTerm.toLowerCase()) ||
                    (change.details && change.details.toLowerCase().includes(searchTerm.toLowerCase()))
                  )
                  .map(change => (
                    <div key={change.pr_number} className={`change-item ${change.type}`}>
                      <div className="change-header">
                        <span className="change-type">{change.type}</span>
                        <a 
                          href={change.pr_url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="pr-link"
                        >
                          #{change.pr_number}
                        </a>
                      </div>
                      
                      <h3 className="change-summary">{change.summary}</h3>
                      
                      {change.details && (
                        <div className="change-details">
                          <ReactMarkdown>{change.details}</ReactMarkdown>
                        </div>
                      )}
                      
                      <div className="change-meta">
                        <span className="change-author">By {change.author}</span>
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default ChangelogList; 