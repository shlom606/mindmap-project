import React from 'react';

const ControlPanel = ({ mapTitle, setMapTitle, inputText, setInputText, onGenerate, loading }) => {
  return (
    <div className="control-panel">
      <h2 style={{ margin: '0 0 15px 0', letterSpacing: '1px', color: '#4facfe' }}>MindNet Explorer</h2>
      <div className="input-group">
        <input 
          className="input-field"
          type="text" 
          placeholder="Map Title..."
          value={mapTitle}
          onChange={(e) => setMapTitle(e.target.value)}
        />
        <input 
          className="input-field"
          style={{ width: '350px' }}
          type="text" 
          placeholder="Enter concepts separated by commas..."
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
        />
        <button 
          className="btn-generate"
          onClick={onGenerate}
          disabled={loading}
        >
          {loading ? "Generating..." : "Generate"}
        </button>
      </div>
    </div>
  );
};

export default ControlPanel;