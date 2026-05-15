import React from 'react';

const Sidebar = ({ savedMaps, onLoadMap }) => {
  return (
    <div className="sidebar">
      <h4>Saved Maps</h4>
      <ul style={{ padding: 0 }}>
        {savedMaps.map(map => (
          <li 
            key={map.id} 
            className="map-history-item"
            onClick={() => onLoadMap(map)}
          >
            📁 {map.title}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Sidebar;