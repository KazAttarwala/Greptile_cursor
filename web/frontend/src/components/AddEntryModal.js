import React from 'react';
import './AddEntryModal.css';

function AddEntryModal({ isOpen, onClose, onSubmit }) {
  if (!isOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    onSubmit({
      summary: formData.get('summary'),
      details: formData.get('details'),
      type: formData.get('type'),
    });
    e.target.reset();
    onClose();
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Add New Entry</h2>
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
            />
          </div>
          <div className="form-group">
            <label htmlFor="details">Details:</label>
            <textarea
              id="details"
              name="details"
              placeholder="Additional details (optional)"
            />
          </div>
          <div className="form-group">
            <label htmlFor="type">Type:</label>
            <select id="type" name="type" required>
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
              Add Entry
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default AddEntryModal; 