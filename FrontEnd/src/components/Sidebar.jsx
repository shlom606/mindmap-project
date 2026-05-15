// src/components/Sidebar.jsx
import React from 'react';

const Sidebar = ({ savedMaps, onLoadMap, onDeleteMap }) => {
  return (
    <div className="sidebar">
      <h4>Saved Maps</h4>
      <ul style={{ padding: 0 }}>
        {savedMaps.map(map => (
          <li 
            key={map.id} 
            className="map-history-item"
            style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
          >
            <span onClick={() => onLoadMap(map)} style={{ flexGrow: 1 }}>
              📁 {map.title}
            </span>
            
            {/* The Delete Button */}
            <button 
              onClick={(e) => {
                e.stopPropagation(); // Prevents loading the map when clicking delete
                onDeleteMap(map.id);
              }}
              style={{
                background: 'transparent',
                border: 'none',
                color: '#ff4b2b',
                cursor: 'pointer',
                fontSize: '16px',
                padding: '0 5px'
              }}
              title="Delete Map"
            >
              🗑️
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Sidebar;