import React, { useState, useRef } from 'react';
import ForceGraph2D from 'react-force-graph-2d';

function App() {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [inputText, setInputText] = useState(""); // שומר את מה שהמשתמש מקליד
  const [loading, setLoading] = useState(false);
  const fgRef = useRef();

  const handleGenerate = () => {
    if (!inputText.trim()) return;
    setLoading(true);

    // הפיכת הטקסט לרשימה (מפרידים לפי פסיקים)
    const concepts = inputText.split(',').map(c => c.trim()).filter(c => c !== "");

    fetch('http://127.0.0.1:8000/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ concepts: concepts }),
    })
      .then((res) => res.json())
      .then((data) => {
        setGraphData(data);
        setLoading(false);
        // מיקוד המצלמה בגרף החדש
        setTimeout(() => fgRef.current.zoomToFit(400), 500);
      })
      .catch((err) => {
        console.error("Error:", err);
        setLoading(false);
      });
  };

  return (
    <div style={{ width: '100vw', height: '100vh', backgroundColor: '#000d1a', color: 'white', fontFamily: 'Arial' }}>
      
      {/* לוח בקרה עליון */}
      <div style={{ position: 'absolute', top: '20px', left: '50%', transform: 'translateX(-50%)', zIndex: 10, textAlign: 'center', background: 'rgba(255, 255, 255, 0.6)', padding: '20px', borderRadius: '15px', border: '1px solid #444' }}>
        <h2>MindNet Generator</h2>
        <input 
          type="text" 
          placeholder="הכנס מושגים מופרדים בפסיקים (למשל: Apple, Banana, Fruit)"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          style={{ width: '400px', padding: '10px', borderRadius: '5px', border: 'none', marginLeft: '10px' }}
        />
        <button 
          onClick={handleGenerate}
          disabled={loading}
          style={{ padding: '10px 20px', cursor: 'pointer', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '5px' }}
        >
          {loading ? "מייצר מפה..." : "צור מפה"}
        </button>
      </div>

      {/* הגרף */}
      {graphData.nodes.length > 0 ? (
        <ForceGraph2D
          ref={fgRef}
          graphData={graphData}
          nodeLabel={node => `${node.id} (${node.category_name})`} 
          // nodeLabel="id"
          nodeAutoColorBy="group"
          nodeRelSize={7}
          linkDirectionalParticles={2}
          linkDirectionalParticleSpeed={0.005}
          linkColor={() => 'rgba(255, 255, 255, 0.3)'} // לבן עם 30% שקיפות (נראה מאוד מודרני)
          linkWidth={1.5}
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
          <h3>הכנס מושגים למעלה כדי להתחיל...</h3>
        </div>
      )}
    </div>
  );
}

export default App;