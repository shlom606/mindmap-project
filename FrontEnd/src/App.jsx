import React, { useState, useEffect } from 'react';
import ControlPanel from './components/ControlPanel.jsx';
import Sidebar from './components/Sidebar.jsx';
import GraphView from './components/GraphView.jsx';
import './App.css';

function App() {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [inputText, setInputText] = useState("");
  const [mapTitle, setMapTitle] = useState("My New Mind Map");
  const [username, setUsername] = useState("Student_1");
  const [loading, setLoading] = useState(false);
  const [savedMaps, setSavedMaps] = useState([]);
  const [hoverNode, setHoverNode] = useState(null);

  useEffect(() => {
    fetchSavedMaps();
  }, []);

  const fetchSavedMaps = async () => {
    try {
      const response = await fetch(`http://127.0.0.1:8000/my-maps/${username}`);
      const data = await response.json();
      setSavedMaps(data.maps);
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
        body: JSON.stringify({ username, map_title: mapTitle, concepts: conceptArray }), 
      });
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
    setGraphData(JSON.parse(mapObj.graph_json));
    setMapTitle(mapObj.title);
  };

  return (
    <div className="app-container">
      <ControlPanel 
        mapTitle={mapTitle} setMapTitle={setMapTitle}
        inputText={inputText} setInputText={setInputText}
        onGenerate={handleGenerateAndSave} loading={loading}
      />

      <Sidebar savedMaps={savedMaps} onLoadMap={loadSpecificMap} />

      {graphData.nodes.length > 0 ? (
        <GraphView 
          graphData={graphData} 
          hoverNode={hoverNode} 
          setHoverNode={setHoverNode} 
        />
      ) : (
        <div className="empty-state">
          <div style={{ fontSize: '50px', marginBottom: '20px' }}>🕸️</div>
          <h3>Ready to map your thoughts? Enter concepts above.</h3>
        </div>
      )}
    </div>
  );
}

export default App;