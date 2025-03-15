import React, { useState, useEffect } from 'react';
import './AddEntryModal.css'; // Reuse the same CSS

function EditEntryModal({ isOpen, onClose, onSubmit, entry }) {
  const [formData, setFormData] = useState({
    summary: '',
    details: '',
    type: 'feature'
  });

  useEffect(() => {
    if (entry) {
      setFormData({
        summary: entry.summary || '',
        details: entry.details || '',
        type: entry.type || 'feature'
      });
    }
  }, [entry]);

  if (!isOpen || !entry) return null;

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      ...entry,
      summary: formData.summary,
      details: formData.details,
      type: formData.type,
    });
    onClose();
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Edit Changelog Entry</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="summary">Summary:</label>
            <input
              type="text"
              id="summary"
              name="summary"
              required
              placeholder="Brief description of the change"
              value={formData.summary}
              onChange={handleChange}
            />
          </div>
          <div className="form-group">
            <label htmlFor="details">Details:</label>
            <textarea
              id="details"
              name="details"
              placeholder="Additional details (optional)"
              value={formData.details}
              onChange={handleChange}
            />
          </div>
          <div className="form-group">
            <label htmlFor="type">Type:</label>
            <select 
              id="type" 
              name="type" 
              required
              value={formData.type}
              onChange={handleChange}
            >
              <option value="feature">Feature</option>
              <option value="bugfix">Bug Fix</option>
              <option value="improvement">Improvement</option>
              <option value="docs">Documentation</option>
              <option value="other">Other</option>
            </select>
          </div>
          <div className="modal-actions">
            <button type="button" className="cancel-button" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="submit-button">
              Save Changes
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default EditEntryModal;