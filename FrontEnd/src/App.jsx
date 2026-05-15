import React, { useState, useRef, useEffect, useCallback } from 'react';
import ForceGraph2D from 'react-force-graph-2d';

function App() {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [inputText, setInputText] = useState("");
  const [mapTitle, setMapTitle] = useState("My New Mind Map");
  const [username, setUsername] = useState("Student_1");
  const [loading, setLoading] = useState(false);
  const [savedMaps, setSavedMaps] = useState([]);
  const [hoverNode, setHoverNode] = useState(null); // Track hovered node for effects
  const fgRef = useRef();

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
        body: JSON.stringify({ 
          username: username,
          map_title: mapTitle,
          concepts: conceptArray 
        }), 
      });
      if (!response.ok) throw new Error("Server Error");
      const result = await response.json();
      setGraphData(result.data);
      fetchSavedMaps();
    } catch (error) {
      console.error("Error:", error);
      alert("Database error!");
    } finally {
      setLoading(false);
    }
  };

  const loadSpecificMap = (mapObj) => {
    const parsedData = JSON.parse(mapObj.graph_json);
    setGraphData(parsedData);
    setMapTitle(mapObj.title);
  };
  const drawNode = useCallback((node, ctx, globalScale) => {
      const isHovered = node === hoverNode;
      const label = node.id;
      const fontSize = isHovered ? 16 / globalScale : 12 / globalScale;
      
      // Fallback: use the color assigned by nodeAutoColorBy
      // If that fails, use a default hex color
      const nodeColor = node.color || '#4facfe'; 

      // Draw node circle
      ctx.beginPath();
      ctx.arc(node.x, node.y, isHovered ? 7 : 5, 0, 2 * Math.PI, false);
      ctx.fillStyle = nodeColor;
      ctx.fill();

      // Draw text label
      ctx.font = `${isHovered ? 'bold' : 'normal'} ${fontSize}px Sans-Serif`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = '#000000'; // Dark text for readability
      ctx.fillText(label, node.x, node.y + (isHovered ? 12 : 10) / globalScale);
    }, [hoverNode]);
    // This function builds the HTML string for the tooltip
  const getTooltipContent = (node) => {
    return `
      <div style="
        background: rgba(255, 255, 255, 0.95);
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #ccc;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        font-family: sans-serif;
        color: #333;
        direction: rtl; /* Support for Hebrew text alignment */
      ">
        <strong style="font-size: 1.1em; color: #2c3e50;">${node.id}</strong>
        <hr style="margin: 5px 0; border: 0; border-top: 1px solid #eee;" />
        <div style="text-align: left; direction: ltr; font-size: 0.85em;">
          <div><b>Category:</b> ${node.category}</div>
          <div><b>FFNN Group:</b> ${node.ffnn_group}</div>
          <div><b>HDBSCAN Group:</b> ${node.hdbscan_group}</div>
          <div><b>Louvain Group:</b> ${node.louvain_group}</div>
        </div>
      </div>
    `;
  };
  return (
    <div style={{ width: '100vw', height: '100vh', backgroundColor: '#050a0f', color: 'white', overflow: 'hidden' }}>
      
      {/* 1. Glassmorphism Control Panel */}
      <div style={{ 
        position: 'absolute', top: '20px', left: '50%', transform: 'translateX(-50%)', zIndex: 10, 
        textAlign: 'center', background: 'rgba(255, 255, 255, 0.05)', backdropFilter: 'blur(10px)',
        padding: '25px', borderRadius: '20px', border: '1px solid rgba(255,255,255,0.1)',
        boxShadow: '0 8px 32px 0 rgba(0,0,0,0.8)' 
      }}>
        <h2 style={{ margin: '0 0 15px 0', letterSpacing: '1px', color: '#4facfe' }}>MindNet Explorer</h2>
        
        <div style={{ display: 'flex', gap: '10px', justifyContent: 'center' }}>
          <input 
            type="text" 
            placeholder="Map Title..."
            value={mapTitle}
            onChange={(e) => setMapTitle(e.target.value)}
            style={{ background: '#1a222d', color: 'white', border: '1px solid #333', padding: '10px', borderRadius: '8px' }}
          />
          <input 
            type="text" 
            placeholder="Enter concepts separated by commas..."
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            style={{ width: '350px', background: '#1a222d', color: 'white', border: '1px solid #333', padding: '10px', borderRadius: '8px' }}
          />
          <button 
            onClick={handleGenerateAndSave}
            disabled={loading}
            style={{ 
              padding: '10px 25px', cursor: 'pointer', background: 'linear-gradient(45deg, #00f2fe 0%, #4facfe 100%)', 
              color: 'black', fontWeight: 'bold', border: 'none', borderRadius: '8px', transition: '0.3s'
            }}
          >
            {loading ? "Generating..." : "Generate"}
          </button>
        </div>
      </div>

      {/* 2. History Sidebar */}
      <div style={{ 
        position: 'absolute', left: '20px', top: '120px', width: '220px', 
        background: 'rgba(0,0,0,0.6)', padding: '15px', borderRadius: '15px', 
        border: '1px solid rgba(255,255,255,0.05)', zIndex: 5, maxHeight: '70vh', overflowY: 'auto'
      }}>
        <h4 style={{ borderBottom: '1px solid #4facfe', paddingBottom: '10px', color: '#4facfe' }}>Saved Maps</h4>
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {savedMaps.map(map => (
            <li key={map.id} onClick={() => loadSpecificMap(map)} 
                style={{ padding: '10px', cursor: 'pointer', borderRadius: '5px', marginBottom: '5px', transition: 'background 0.2s', fontSize: '14px', borderBottom: '1px solid #222' }}
                onMouseEnter={(e) => e.target.style.background = 'rgba(79, 172, 254, 0.2)'}
                onMouseLeave={(e) => e.target.style.background = 'transparent'}>
              📁 {map.title}
            </li>
          ))}
        </ul>
      </div>

      {/* 3. The Graph Display */}
      {graphData.nodes.length > 0 ? (
        <ForceGraph2D
          graphData={graphData}
          
          /* FIX: Explicitly point to the key in your JSON */
          nodeAutoColorBy="ffnn_group" 
          //nodeAutoColorBy="hdbscan_group"
          // nodeAutoColorBy="louvain_group"
          nodeLabel={node => getTooltipContent(node)}
          /* STYLING LINKS: Make them look professional */
          linkWidth={1.5}
          linkColor={() => '#d3d3d3'} // Soft grey links
          linkDirectionalParticles={1} // Adds "flow" to the mind map
          linkDirectionalParticleSpeed={0.005}
          
          /* NODE INTERACTION */
          nodeCanvasObject={drawNode}
          onNodeHover={setHoverNode}
          nodePointerAreaPaint={(node, color, ctx) => {
            ctx.fillStyle = color;
            ctx.beginPath();
            ctx.arc(node.x, node.y, 8, 0, 2 * Math.PI, false);
            ctx.fill();
          }}
        />
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', height: '100%', color: '#555' }}>
          <div style={{ fontSize: '50px', marginBottom: '20px' }}>🕸️</div>
          <h3>Ready to map your thoughts? Enter concepts above.</h3>
        </div>
      )}
    </div>
  );
}

export default App;