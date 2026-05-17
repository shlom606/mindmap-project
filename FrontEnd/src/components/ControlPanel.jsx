import React from 'react';

const ControlPanel = ({ mapTitle, setMapTitle, inputText, setInputText, modelType, setModelType, onGenerate, loading,colorMode, setColorMode }) => {
  return (
    <div className="control-panel">
      <h2 style={{ margin: '0 0 15px 0', letterSpacing: '1px', color: '#4facfe' }}>MindNet Explorer</h2>
      <div className="input-group">
        {/* Model Selection Dropdown */}
        <select 
          value={modelType} 
          onChange={(e) => setModelType(e.target.value)}
          className="input-field"
          style={{ cursor: 'pointer', border: '1px solid #4facfe' }}
        >
          <option value="minibert">Model: miniBERT (8-dim)</option>
          <option value="sbert">Model: SBERT (384-dim)</option>
        </select>

        {/* NEW DROPDOWN: Visual Layer Selection */}
        <select 
          value={colorMode} 
          onChange={(e) => setColorMode(e.target.value)}
          className="input-field"
          style={{ border: '1px solid #00f2fe', color: '#00f2fe' }} // Colored border to highlight it
        >
          <option value="ffnn_group">Color By: AI Categories (FFNN)</option>
          <option value="hdbscan_group">Color By: Density Clusters (HDBSCAN)</option>
          <option value="louvain_group">Color By: Graph Communities (Louvain)</option>
        </select>

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