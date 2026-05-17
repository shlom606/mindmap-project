import React, { useState, useEffect } from 'react';
import ControlPanel from './components/ControlPanel.jsx';
import Sidebar from './components/Sidebar.jsx';
import GraphView from './components/GraphView.jsx';
import Auth from './components/Auth.jsx';
import './App.css';

function App() {
  const [user, setUser] = useState(null); // Track logged in user
  const [username, setUsername] = useState(""); // Remove the "Student_1" default here!
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [inputText, setInputText] = useState("");
  const [mapTitle, setMapTitle] = useState("My New Mind Map");
  const [loading, setLoading] = useState(false);
  const [savedMaps, setSavedMaps] = useState([]);
  const [hoverNode, setHoverNode] = useState(null);
  const [modelType, setModelType] = useState("minibert");
  const [colorMode, setColorMode] = useState('ffnn_group');
  useEffect(() => {
    if (user) fetchSavedMaps();
  }, [user]);

  // Logout handler
  const handleLogout = () => {
    setUser(null);
    setGraphData({ nodes: [], links: [] });
  };
  const handleLoginSuccess = (name) => {
    setUser(name);
    setUsername(name); // Update the username used for generation
  };
  
  if (!user) return <Auth onLoginSuccess={handleLoginSuccess} />;

  const fetchSavedMaps = async () => {
  if (!user) return;
  try {
    const response = await fetch(`http://127.0.0.1:8000/my-maps/${user}`);
    const data = await response.json();
    // Use an empty array as fallback if maps is missing
    setSavedMaps(data.maps || []); 
  } catch (err) {
    console.error("Failed to load map history:", err);
  }
  };

  const handleGenerateAndSave = async () => {
    const conceptArray = inputText.split(',').map(c => c.trim()).filter(c => c.length > 0);
    if (conceptArray.length < 2) {
      alert("Please enter at least 2 concepts.");
      return;
    }
    setLoading(true);
    try {
      const response = await fetch("http://127.0.0.1:8000/generate-and-save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          username: username,
          map_title: mapTitle,
          concepts: conceptArray,
          model_type: modelType // Send the choice to the backend
        }), 
      });
      if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
      const result = await response.json();
      setGraphData(result.data);
      fetchSavedMaps();
    } catch (error) {
      alert("Database error!");
    } finally {
      setLoading(false);
    }
  };
  const loadSpecificMap = (mapObj) => {
    try {
      if (mapObj && mapObj.graph_json) {
        const parsedData = JSON.parse(mapObj.graph_json);
        // Ensure the parsed data has the required arrays
        setGraphData({
          nodes: parsedData.nodes || [],
          links: parsedData.links || []
        });
        setMapTitle(mapObj.title);
      }
    } catch (err) {
      console.error("Error parsing map data:", err);
      setGraphData({ nodes: [], links: [] }); // Reset to safe state
    }
  };

  const handleDeleteMap = async (mapId) => {
    // Always ask for confirmation before deleting data!
    if (!window.confirm("Are you sure you want to permanently delete this mind map?")) {
      return;
    }

    try {
      const response = await fetch(`http://127.0.0.1:8000/delete-map/${user}/${mapId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        // Refresh the list after successful deletion
        fetchSavedMaps();
        // Optional: Clear the graph if the deleted map was the one currently open
        setGraphData({ nodes: [], links: [] });
      } else {
        const errorData = await response.json();
        alert(`Delete failed: ${errorData.detail}`);
      }
    } catch (error) {
      console.error("Error deleting map:", error);
      alert("Server connection error.");
    }
  };

  return (
    <div className="app-container">
      <button onClick={handleLogout} style={styles.logoutBtn}>Logout ({user})</button>
      <ControlPanel 
      username={user}
      mapTitle={mapTitle} 
      setMapTitle={setMapTitle}
      inputText={inputText} 
      setInputText={setInputText}
      onGenerate={handleGenerateAndSave} 
      loading={loading}
      
      modelType={modelType}
      setModelType={setModelType}
      colorMode={colorMode} setColorMode={setColorMode} // <-- ADDED PROPS
      />

      <Sidebar savedMaps={savedMaps} 
      onLoadMap={loadSpecificMap} 
      onDeleteMap={handleDeleteMap} />
      
      {graphData && graphData.nodes && graphData.nodes.length > 0 ? (
        <GraphView 
          graphData={graphData} 
          hoverNode={hoverNode} 
          setHoverNode={setHoverNode} 
          colorMode={colorMode} // <-- PASS COLOR MODE DOWN TO GRAPH
        />
      ) : (
        <div className="empty-state">
          <div style={{ fontSize: '50px', marginBottom: '20px' }}>🕸️</div>
          <h3>{loading ? "Generating your map..." : "Ready to map your thoughts? Enter concepts above."}</h3>
        </div>
      )}
    </div>
  );
  
}
const styles = {
  logoutBtn: {
    position: 'absolute',
    top: '20px',
    right: '20px',
    zIndex: 100,
    background: 'transparent',
    color: '#ff4b2b',
    border: '1px solid #ff4b2b',
    padding: '5px 15px',
    borderRadius: '5px',
    cursor: 'pointer'
  }
};
export default App;