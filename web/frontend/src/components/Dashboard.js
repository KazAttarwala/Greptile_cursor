import React from 'react';
import './Dashboard.css';

function Dashboard({ repository, changelog }) {
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

  return (
    <div className="dashboard">
      <h2>Dashboard: {repository.name}</h2>
      
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
      
      <div className="activity-chart">
        <h3>Recent Activity</h3>
        <div className="chart-container">
          {/* Simple visual representation of activity */}
          <div className="activity-bars">
            {Array.from({ length: 30 }).map((_, i) => {
              const date = new Date();
              date.setDate(date.getDate() - (29 - i));
              const dateStr = date.toISOString().split('T')[0];
              
              const dayChanges = changelog.changes.filter(change => 
                change.date && change.date.startsWith(dateStr)
              ).length;
              
              const height = dayChanges ? Math.min(100, dayChanges * 20) : 5;
              
              return (
                <div key={i} className="activity-bar-container">
                  <div 
                    className="activity-bar" 
                    style={{ height: `${height}%` }}
                    title={`${dayChanges} changes on ${dateStr}`}
                  />
                  {i % 5 === 0 && <div className="date-label">{date.getDate()}</div>}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard; 