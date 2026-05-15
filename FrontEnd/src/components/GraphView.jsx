import React, { useCallback } from 'react';
import ForceGraph2D from 'react-force-graph-2d';

const GraphView = ({ graphData, hoverNode, setHoverNode }) => {
  
  const getTooltipContent = (node) => `
    <div style="background: rgba(255, 255, 255, 0.95); padding: 10px; border-radius: 8px; border: 1px solid #ccc; font-family: sans-serif; color: #333; direction: rtl;">
      <strong style="font-size: 1.1em; color: #2c3e50;">${node.id}</strong>
      <hr style="margin: 5px 0; border: 0; border-top: 1px solid #eee;" />
      <div style="text-align: left; direction: ltr; font-size: 0.85em;">
        <div><b>Category:</b> ${node.category}</div>
        <div><b>Group:</b> ${node.ffnn_group}</div>
      </div>
    </div>
  `;

  const drawNode = useCallback((node, ctx, globalScale) => {
    const isHovered = node === hoverNode;
    const label = node.id;
    const fontSize = isHovered ? 16 / globalScale : 12 / globalScale;
    const nodeColor = node.color || '#4facfe'; 

    ctx.beginPath();
    ctx.arc(node.x, node.y, isHovered ? 7 : 5, 0, 2 * Math.PI, false);
    ctx.fillStyle = nodeColor;
    ctx.fill();

    ctx.font = `${isHovered ? 'bold' : 'normal'} ${fontSize}px Sans-Serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = '#FFFFFF'; 
    ctx.fillText(label, node.x, node.y + (isHovered ? 12 : 10) / globalScale);
  }, [hoverNode]);

  return (
    <ForceGraph2D
      graphData={graphData}
      nodeAutoColorBy="ffnn_group"
      nodeLabel={getTooltipContent}
      linkWidth={1.5}
      linkColor={() => '#d3d3d3'}
      linkDirectionalParticles={1}
      linkDirectionalParticleSpeed={0.005}
      nodeCanvasObject={drawNode}
      onNodeHover={setHoverNode}
    />
  );
};

export default GraphView;