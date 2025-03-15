import React, { useState } from 'react';
import './Dashboard.css';
import EditEntryModal from './EditEntryModal';

function Dashboard({ repository, changelog, onEditEntry }) {
  const [activeFilter, setActiveFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedChange, setSelectedChange] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [editingEntry, setEditingEntry] = useState(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
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

  // Calculate contributors
  const contributorStats = changelog.changes.reduce((acc, change) => {
    const author = change.author || 'Unknown';
    if (!acc[author]) {
      acc[author] = { count: 0, avatar: change.avatar_url };
    }
    acc[author].count += 1;
    return acc;
  }, {});

  // Sort contributors by contribution count
  const topContributors = Object.entries(contributorStats)
    .sort((a, b) => b[1].count - a[1].count)
    .slice(0, 5);

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

  // Function to generate markdown export
  const generateMarkdown = () => {
    // Group changes by date
    const changesByDate = changelog.changes.reduce((acc, change) => {
      const date = change.date ? change.date.split('T')[0] : 'Unknown Date';
      if (!acc[date]) {
        acc[date] = [];
      }
      acc[date].push(change);
      return acc;
    }, {});

    // Sort dates in reverse chronological order
    const sortedDates = Object.keys(changesByDate).sort().reverse();

    let markdown = `# Changelog for ${repository.name}\n\n`;
    markdown += `Generated on ${new Date().toLocaleDateString()}\n\n`;

    // Add each date and its changes
    sortedDates.forEach(date => {
      try {
        const formattedDate = new Date(date).toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        });
        markdown += `## ${formattedDate}\n\n`;
      } catch (e) {
        markdown += `## ${date}\n\n`;
      }

      // Group by type
      const changesByType = changesByDate[date].reduce((acc, change) => {
        const type = change.type || 'other';
        if (!acc[type]) {
          acc[type] = [];
        }
        acc[type].push(change);
        return acc;
      }, {});

      // Add each type and its changes
      Object.entries(changesByType).forEach(([type, changes]) => {
        const typeHeader = type.charAt(0).toUpperCase() + type.slice(1);
        markdown += `### ${typeHeader}\n\n`;

        changes.forEach(change => {
          markdown += `- ${change.summary}`;
          if (change.pr_number) {
            markdown += ` ([#${change.pr_number}](${change.pr_url}))`;
          }
          if (change.details) {
            markdown += `\n  ${change.details}`;
          }
          markdown += '\n';
        });

        markdown += '\n';
      });
    });

    return markdown;
  };

  // Function to download markdown file
  const downloadMarkdown = () => {
    const markdown = generateMarkdown();
    const blob = new Blob([markdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${repository.name.replace(/\s+/g, '-').toLowerCase()}-changelog.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // Function to handle edit button click
  const handleEditClick = (e, change) => {
    e.stopPropagation(); // Prevent triggering the parent click event
    setEditingEntry(change);
    setIsEditModalOpen(true);
  };

  // Function to close edit modal
  const closeEditModal = () => {
    setIsEditModalOpen(false);
    setEditingEntry(null);
  };

  // Function to handle edit submission
  const handleEditSubmit = (updatedEntry) => {
    if (onEditEntry) {
      onEditEntry(updatedEntry);
    }
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>Metrics</h2>
        <button className="export-button" onClick={downloadMarkdown}>
          Export as Markdown
        </button>
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
        <div className="activity-chart">
          <h3>Activity Timeline</h3>
          <div className="chart-container">
            <div className="activity-bars">
              {Array.from({ length: 30 }).map((_, i) => {
                const date = new Date();
                date.setDate(date.getDate() - (29 - i));
                const dateStr = date.toISOString().split('T')[0];
                
                const dayChanges = changelog.changes.filter(change => 
                  change.date && change.date.startsWith(dateStr)
                ).length;
                
                // Only calculate height if there are changes
                const height = dayChanges ? Math.min(100, dayChanges * 20) : 0;
                
                // Format date for label
                const monthDay = `${date.getMonth() + 1}/${date.getDate()}`;
                
                return (
                  <div key={i} className="activity-bar-container">
                    {height > 0 && (
                      <div 
                        className="activity-bar" 
                        style={{ height: `${height}%` }}
                        title={`${dayChanges} changes on ${dateStr}`}
                      >
                        {dayChanges > 0 && (
                          <div className="activity-tooltip">
                            <div className="tooltip-date">{formatDate(dateStr)}</div>
                            <div className="tooltip-count">{dayChanges} changes</div>
                          </div>
                        )}
                      </div>
                    )}
                    {i % 3 === 0 && <div className="date-label">{monthDay}</div>}
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        <div className="contributors-card">
          <h3>Top Contributors</h3>
          <div className="contributors-list">
            {topContributors.length > 0 ? (
              topContributors.map(([author, data]) => (
                <div key={author} className="contributor-item">
                  <div className="contributor-info">
                    <span className="contributor-name">{author}</span>
                    <span className="contributor-count">{data.count} changes</span>
                  </div>
                  <div className="contributor-bar-container">
                    <div 
                      className="contributor-bar" 
                      style={{ 
                        width: `${Math.min(100, (data.count / topContributors[0][1].count) * 100)}%` 
                      }}
                    />
                  </div>
                </div>
              ))
            ) : (
              <div className="no-data">No contributor data available</div>
            )}
          </div>
        </div>
      </div>

      <div className="latest-changes-card">
        <div className="latest-changes-header">
          <h3>All Changes</h3>
          <div className="filter-controls">
            <div className="filter-buttons">
              <button 
                className={`filter-button ${activeFilter === 'all' ? 'active' : ''}`}
                onClick={() => {
                  setActiveFilter('all');
                  setCurrentPage(1);
                }}
              >
                All
              </button>
              {Object.keys(changesByType).map(type => (
                <button 
                  key={type}
                  className={`filter-button ${activeFilter === type ? 'active' : ''}`}
                  onClick={() => {
                    setActiveFilter(type);
                    setCurrentPage(1);
                  }}
                >
                  {type.charAt(0).toUpperCase() + type.slice(1)}
                </button>
              ))}
            </div>
            <div className="search-container">
              <input
                type="text"
                className="search-input"
                placeholder="Search changes..."
                value={searchQuery}
                onChange={handleSearchChange}
              />
              {searchQuery && (
                <button className="clear-search" onClick={clearSearch}>
                  ×
                </button>
              )}
            </div>
          </div>
        </div>
        <div className="latest-changes-list">
          {currentEntries.length > 0 ? (
            currentEntries.map((change, index) => (
              <div 
                key={index} 
                className={`latest-change-item ${selectedChange === change ? 'expanded' : ''}`}
                onClick={() => handleChangeClick(change)}
              >
                <div className="latest-change-header">
                  <span className={`type-badge ${change.type}`}>{change.type}</span>
                  <div className="latest-change-actions">
                    <button 
                      className="edit-button" 
                      onClick={(e) => handleEditClick(e, change)}
                      title="Edit entry"
                    >
                      ✏️
                    </button>
                    <span className="latest-change-date">
                      {formatDate(change.date)}
                    </span>
                  </div>
                </div>
                <div className="latest-change-summary">{change.summary}</div>
                {change.author && (
                  <div className="latest-change-author">by {change.author}</div>
                )}
                {selectedChange === change && (
                  <div className="change-details">
                    {change.details && (
                      <div className="change-details-section">
                        <h4>Details</h4>
                        <p>{change.details}</p>
                      </div>
                    )}
                    {change.pr_number && (
                      <div className="change-details-section">
                        <h4>Pull Request</h4>
                        <a 
                          href={change.pr_url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          onClick={(e) => e.stopPropagation()}
                        >
                          #{change.pr_number}
                        </a>
                      </div>
                    )}
                    {change.files && change.files.length > 0 && (
                      <div className="change-details-section">
                        <h4>Files Changed</h4>
                        <ul className="files-list">
                          {change.files.map((file, i) => (
                            <li key={i}>{file}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))
          ) : (
            <div className="no-data">No changes found with the selected filter</div>
          )}
        </div>
        
        {totalPages > 1 && (
          <div className="pagination">
            <button 
              className="pagination-button"
              onClick={prevPage}
              disabled={currentPage === 1}
            >
              &laquo; Previous
            </button>
            <div className="pagination-info">
              Page {currentPage} of {totalPages} ({filteredChanges.length} entries)
            </div>
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

      {/* Change details modal */}
      {selectedChange && (
        <div className="change-details-overlay" onClick={closeChangeDetails}>
          <div className="change-details-modal" onClick={(e) => e.stopPropagation()}>
            <button className="close-modal" onClick={closeChangeDetails}>×</button>
            <h3>{selectedChange.summary}</h3>
            
            <div className="modal-meta">
              <div className="modal-meta-item">
                <span className="meta-label">Type:</span>
                <span className={`type-badge ${selectedChange.type}`}>{selectedChange.type}</span>
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
            </div>
            
            <div className="modal-actions">
              <button 
                className="edit-button-large" 
                onClick={(e) => {
                  e.stopPropagation();
                  closeChangeDetails();
                  handleEditClick(e, selectedChange);
                }}
              >
                Edit Entry
              </button>
            </div>
            
            {selectedChange.details && (
              <div className="modal-section">
                <h4>Details</h4>
                <p>{selectedChange.details}</p>
              </div>
            )}
            
            {selectedChange.pr_number && (
              <div className="modal-section">
                <h4>Pull Request</h4>
                <a 
                  href={selectedChange.pr_url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                >
                  #{selectedChange.pr_number}
                </a>
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

      {/* Edit Entry Modal */}
      <EditEntryModal 
        isOpen={isEditModalOpen}
        onClose={closeEditModal}
        onSubmit={handleEditSubmit}
        entry={editingEntry}
      />
    </div>
  );
}

export default Dashboard;