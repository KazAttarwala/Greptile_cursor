import React, { useState } from 'react';
import './Dashboard.css';

function Dashboard({ repository, changelog }) {
  const [activeFilter, setActiveFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedChange, setSelectedChange] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const entriesPerPage = 10;

  // Skip rendering if no data
  if (!repository || !changelog || !changelog.changes) {
    return <div className="dashboard-placeholder">Select a repository to view analytics</div>;
  }

  // Calculate metrics
  const totalChanges = changelog.changes.length;
  const changesByType = changelog.changes.reduce((acc, change) => {
    const type = change.type || 'other';
    acc[type] = (acc[type] || 0) + 1;
    return acc;
  }, {});
  
  // Get last 30 days of activity
  const thirtyDaysAgo = new Date();
  thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
  
  const recentChanges = changelog.changes.filter(change => {
    const changeDate = new Date(change.date);
    return changeDate >= thirtyDaysAgo;
  });

  // Get latest changes with filter and search
  const filteredChanges = changelog.changes.filter(change => {
    // Type filter
    const typeMatch = activeFilter === 'all' || change.type === activeFilter;
    
    // Search filter
    const searchMatch = !searchQuery || 
      (change.summary && change.summary.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (change.details && change.details.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (change.author && change.author.toLowerCase().includes(searchQuery.toLowerCase()));
    
    return typeMatch && searchMatch;
  });
  
  // Sort changes by date (newest first)
  const sortedChanges = [...filteredChanges].sort((a, b) => new Date(b.date) - new Date(a.date));
  
  // Calculate pagination
  const totalPages = Math.ceil(sortedChanges.length / entriesPerPage);
  const indexOfLastEntry = currentPage * entriesPerPage;
  const indexOfFirstEntry = indexOfLastEntry - entriesPerPage;
  const currentEntries = sortedChanges.slice(indexOfFirstEntry, indexOfLastEntry);

  // Function to change page
  const paginate = (pageNumber) => setCurrentPage(pageNumber);

  // Function to go to next page
  const nextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1);
    }
  };

  // Function to go to previous page
  const prevPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };

  // Function to handle search input change
  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
    setCurrentPage(1); // Reset to first page when searching
  };

  // Function to clear search
  const clearSearch = () => {
    setSearchQuery('');
    setCurrentPage(1); // Reset to first page when clearing search
  };

  // Function to handle change click
  const handleChangeClick = (change) => {
    setSelectedChange(selectedChange === change ? null : change);
  };

  // Function to close change details modal
  const closeChangeDetails = () => {
    setSelectedChange(null);
  };

  // Function to format date correctly
  const formatDate = (dateString) => {
    // Create a date object with the UTC time
    const date = new Date(dateString);
    // Format the date manually to avoid timezone issues
    const year = date.getUTCFullYear();
    const month = date.getUTCMonth() + 1;
    const day = date.getUTCDate();
    
    // Get month name
    const monthNames = [
      'January', 'February', 'March', 'April', 'May', 'June',
      'July', 'August', 'September', 'October', 'November', 'December'
    ];
    
    return `${monthNames[month-1]} ${day}, ${year}`;
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>At a glance</h2>
      </div>

      <div className="metrics-grid">
        <div className="metric-card">
          <h3>Total Changes</h3>
          <div className="metric-value">{totalChanges}</div>
        </div>
        
        <div className="metric-card">
          <h3>Recent Activity</h3>
          <div className="metric-value">{recentChanges.length}</div>
          <div className="metric-subtitle">changes in last 30 days</div>
        </div>
        
        <div className="metric-card">
          <h3>Change Types</h3>
          <div className="change-types">
            {Object.entries(changesByType).map(([type, count]) => (
              <div key={type} className="change-type">
                <span className={`type-badge ${type}`}>{type}</span>
                <span className="type-count">{count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="dashboard-row">
        <div className="latest-changes-card">
          <div className="latest-changes-header">
            <h3>Changelog Entries</h3>
            <div className="filter-controls">
              <div className="filter-buttons">
                <button 
                  className={`filter-button ${activeFilter === 'all' ? 'active' : ''}`}
                  onClick={() => { setActiveFilter('all'); setCurrentPage(1); }}
                >
                  All
                </button>
                <button 
                  className={`filter-button ${activeFilter === 'feature' ? 'active' : ''}`}
                  onClick={() => { setActiveFilter('feature'); setCurrentPage(1); }}
                >
                  Features
                </button>
                <button 
                  className={`filter-button ${activeFilter === 'bugfix' ? 'active' : ''}`}
                  onClick={() => { setActiveFilter('bugfix'); setCurrentPage(1); }}
                >
                  Bug Fixes
                </button>
                <button 
                  className={`filter-button ${activeFilter === 'improvement' ? 'active' : ''}`}
                  onClick={() => { setActiveFilter('improvement'); setCurrentPage(1); }}
                >
                  Improvements
                </button>
              </div>
              <div className="search-container">
                <input
                  type="text"
                  className="search-input"
                  placeholder="Search entries..."
                  value={searchQuery}
                  onChange={handleSearchChange}
                />
                {searchQuery && (
                  <button className="clear-search" onClick={clearSearch}>×</button>
                )}
              </div>
            </div>
          </div>
          
          {currentEntries.length === 0 ? (
            <div className="no-data">No entries found matching your criteria</div>
          ) : (
            <div className="latest-changes-list">
              {currentEntries.map((change, index) => (
                <div 
                  key={change.id || index}
                  className={`latest-change-item ${selectedChange === change ? 'expanded' : ''}`}
                  onClick={() => handleChangeClick(change)}
                >
                  <div className="latest-change-header">
                    <span className={`type-badge ${change.type || 'other'}`}>
                      {change.type || 'Other'}
                    </span>
                    <span className="latest-change-date">
                      {formatDate(change.date)}
                    </span>
                  </div>
                  <h4 className="latest-change-summary">{change.summary}</h4>
                  {change.author && (
                    <div className="latest-change-author">
                      By: {change.author}
                    </div>
                  )}
                  {selectedChange === change && change.details && (
                    <div className="change-details">
                      <div className="change-details-section">
                        <h4>Details</h4>
                        <p>{change.details}</p>
                      </div>
                      {change.pr_number && (
                        <div className="change-details-section">
                          <h4>Pull Request</h4>
                          <a 
                            href={change.pr_url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="pr-link"
                          >
                            #{change.pr_number}
                          </a>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
          
          {totalPages > 1 && (
            <div className="pagination">
              <button 
                className="pagination-button" 
                onClick={prevPage}
                disabled={currentPage === 1}
              >
                &laquo; Previous
              </button>
              <span className="pagination-info">
                Page {currentPage} of {totalPages}
              </span>
              <button 
                className="pagination-button" 
                onClick={nextPage}
                disabled={currentPage === totalPages}
              >
                Next &raquo;
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Change Details Modal */}
      {selectedChange && (
        <div className="change-details-overlay" onClick={closeChangeDetails}>
          <div className="change-details-modal" onClick={e => e.stopPropagation()}>
            <button className="close-modal" onClick={closeChangeDetails}>×</button>
            <h3>{selectedChange.summary}</h3>
            
            <div className="modal-meta">
              <div className="modal-meta-item">
                <span className="meta-label">Type:</span>
                <span className={`type-badge ${selectedChange.type || 'other'}`}>
                  {selectedChange.type || 'Other'}
                </span>
              </div>
              <div className="modal-meta-item">
                <span className="meta-label">Date:</span>
                <span>{formatDate(selectedChange.date)}</span>
              </div>
              {selectedChange.author && (
                <div className="modal-meta-item">
                  <span className="meta-label">Author:</span>
                  <span>{selectedChange.author}</span>
                </div>
              )}
              {selectedChange.pr_number && (
                <div className="modal-meta-item">
                  <span className="meta-label">PR:</span>
                  <a 
                    href={selectedChange.pr_url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="pr-link"
                  >
                    #{selectedChange.pr_number}
                  </a>
                </div>
              )}
            </div>
            
            {selectedChange.details && (
              <div className="modal-section">
                <h4>Details</h4>
                <p>{selectedChange.details}</p>
              </div>
            )}
            
            {selectedChange.files && selectedChange.files.length > 0 && (
              <div className="modal-section">
                <h4>Files Changed</h4>
                <ul className="files-list">
                  {selectedChange.files.map((file, i) => (
                    <li key={i}>{file}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default Dashboard;