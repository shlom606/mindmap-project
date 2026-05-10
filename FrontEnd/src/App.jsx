import React, { useState, useRef, useEffect } from 'react';
import ForceGraph2D from 'react-force-graph-2d';

function App() {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [inputText, setInputText] = useState("");
  const [mapTitle, setMapTitle] = useState("My New Mind Map");
  const [username, setUsername] = useState("Student_1"); // For now, a static user
  const [loading, setLoading] = useState(false);
  const [savedMaps, setSavedMaps] = useState([]); // List of maps from DB
  const fgRef = useRef();

  // Load history when the app starts
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
    const conceptArray = inputText
      .split(',')
      .map(c => c.trim())
      .filter(c => c.length > 0);

    if (conceptArray.length < 2) {
      alert("Please enter at least 2 concepts.");
      return;
    }

    setLoading(true);

    try {
      // Calling the NEW save endpoint we designed
      const response = await fetch("http://127.0.0.1:8000/generate-and-save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          username: username,
          map_title: mapTitle,
          concepts: conceptArray 
        }), 
      });

      if (!response.ok) throw new Error("Server Error");
      
      const result = await response.json();
      setGraphData(result.data); // result.data contains the nodes/links
      fetchSavedMaps(); // Refresh the list
    } catch (error) {
      console.error("Error:", error);
      alert("Database error! Check your FastAPI console.");
    } finally {
      setLoading(false);
    }
  };

  // Function to load an old map from history
  const loadSpecificMap = (mapObj) => {
    const parsedData = JSON.parse(mapObj.graph_json);
    setGraphData(parsedData);
    setMapTitle(mapObj.title);
  };

  return (
    <div style={{ width: '100vw', height: '100vh', backgroundColor: '#000d1a', color: 'white', fontFamily: 'Arial' }}>
      
      {/* 1. Control Panel */}
      <div style={{ position: 'absolute', top: '20px', left: '50%', transform: 'translateX(-50%)', zIndex: 10, textAlign: 'center', background: 'rgba(20, 40, 60, 0.9)', padding: '20px', borderRadius: '15px', border: '1px solid #007bff', boxShadow: '0 0 15px rgba(0,123,255,0.5)' }}>
        <h2 style={{ margin: '0 0 10px 0' }}>MindNet Cloud Storage</h2>
        
        <input 
          type="text" 
          placeholder="Map Title (e.g., Physics Lesson)"
          value={mapTitle}
          onChange={(e) => setMapTitle(e.target.value)}
          style={{ width: '200px', padding: '10px', marginBottom: '10px', borderRadius: '5px', border: '1px solid #444' }}
        /><br/>

        <input 
          type="text" 
          placeholder="Concepts (Banana, Apple...)"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          style={{ width: '400px', padding: '10px', borderRadius: '5px', border: 'none' }}
        />
        <button 
          onClick={handleGenerateAndSave}
          disabled={loading}
          style={{ padding: '10px 20px', cursor: 'pointer', backgroundColor: '#28a745', color: 'white', border: 'none', borderRadius: '5px', marginLeft: '10px' }}
        >
          {loading ? "Saving..." : "Generate & Save"}
        </button>
      </div>

      {/* 2. History Sidebar */}
      <div style={{ position: 'absolute', left: '20px', top: '100px', width: '200px', background: 'rgba(0,0,0,0.5)', padding: '10px', borderRadius: '10px', zIndex: 5 }}>
        <h4>Your Saved Maps</h4>
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {savedMaps.map(map => (
            <li key={map.id} onClick={() => loadSpecificMap(map)} style={{ padding: '5px', cursor: 'pointer', borderBottom: '1px solid #333', fontSize: '14px' }}>
              📁 {map.title}
            </li>
          ))}
        </ul>
      </div>

      {/* 3. The Graph Display */}
      {graphData.nodes.length > 0 ? (
        <ForceGraph2D
          ref={fgRef}
          graphData={graphData}
          nodeAutoColorBy="group"
          nodeRelSize={7}
          linkDirectionalParticles={2}
          linkColor={() => 'rgba(255, 255, 255, 0.3)'}
          nodeCanvasObject={(node, ctx, globalScale) => {
            const label = node.id;
            const fontSize = 14 / globalScale;
            ctx.font = `${fontSize}px Sans-Serif`;
            ctx.textAlign = 'center';
            ctx.fillStyle = node.color;
            ctx.beginPath();
            ctx.arc(node.x, node.y, 5, 0, 2 * Math.PI, false);
            ctx.fill();
            ctx.fillStyle = 'white';
            ctx.fillText(label, node.x, node.y + 12);
          }}
        />
      ) : (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
          <h3>Enter data to generate your first saved MindNet...</h3>
        </div>
      )}
    </div>
  );
}

export default App;