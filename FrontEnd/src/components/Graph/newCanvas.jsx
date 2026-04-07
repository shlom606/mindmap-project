import React, { useEffect, useRef, useState } from 'react';
import { drawNode } from '../Elements/Node';
import { drawLink } from '../Elements/Link';

function NewCanvas() {
    const canvasRef = useRef(null);
    const [nodes, setNodes] = useState([]);
    const [links, setLinks] = useState([]);
    const [selectedNodeIndex, setSelectedNodeIndex] = useState(null);
    
    // גרירה
    const [isDragging, setIsDragging] = useState(false);
    const [draggedNodeIndex, setDraggedNodeIndex] = useState(null);
    const [didDrag, setDidDrag] = useState(false);

    // עריכת טקסט
    const [editingIndex, setEditingIndex] = useState(null);
    const [tempText, setTempText] = useState("");
    
    // עוקב אחרי מיקום העכבר בשביל הקו הגמיש
    const [mousePos, setMousePos] = useState({ x: 0, y: 0 });

    const isInsideNode = (x, y, node) => {
        return Math.pow(x - node.x, 2) / Math.pow(50, 2) + Math.pow(y - node.y, 2) / Math.pow(30, 2) <= 1;
    };

    const draw = () => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext("2d");
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // 1. ציור קשרים קיימים
        links.forEach(link => {
            if (nodes[link.from] && nodes[link.to]) {
                drawLink(ctx, nodes[link.from], nodes[link.to]);
            }
        });

        // 2. ציור "קו גמיש" בזמן בחירה
        if (selectedNodeIndex !== null && !isDragging) {
            ctx.beginPath();
            ctx.moveTo(nodes[selectedNodeIndex].x, nodes[selectedNodeIndex].y);
            ctx.lineTo(mousePos.x, mousePos.y);
            ctx.strokeStyle = "rgba(99, 102, 241, 0.5)"; // סגול שקוף
            ctx.setLineDash([5, 5]); // קו מקווקו
            ctx.stroke();
            ctx.setLineDash([]); // ביטול קו מקווקו להמשך הציור
        }

        // 3. ציור האליפסות
        nodes.forEach((node, index) => {
            drawNode(ctx, node, index === selectedNodeIndex);
        });
    };

    useEffect(() => {
        draw();
    }, [nodes, links, selectedNodeIndex, mousePos, isDragging]);

    const handleMouseDown = (event) => {
        const rect = canvasRef.current.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;

        const clickedNodeIndex = nodes.findIndex(node => isInsideNode(x, y, node));

        if (clickedNodeIndex !== -1) {
            setIsDragging(true);
            setDraggedNodeIndex(clickedNodeIndex);
            setDidDrag(false);
        }
    };

    const handleMouseMove = (event) => {
        const rect = canvasRef.current.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        
        // עדכון מיקום העכבר תמיד (בשביל הקו הגמיש)
        setMousePos({ x, y });

        if (isDragging && draggedNodeIndex !== null) {
            setDidDrag(true);
            const newNodes = [...nodes];
            newNodes[draggedNodeIndex] = { ...newNodes[draggedNodeIndex], x, y };
            setNodes(newNodes);
        }
    };

    const handleMouseUp = () => {
        setIsDragging(false);
        setDraggedNodeIndex(null);
    };

    const handleCanvasClick = (event) => {
        // אם גררנו, לא יוצרים קשר או עיגול חדש
        if (didDrag) {
            setDidDrag(false);
            return;
        }

        const rect = canvasRef.current.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;

        const clickedNodeIndex = nodes.findIndex(node => isInsideNode(x, y, node));

        if (clickedNodeIndex !== -1) {
            if (selectedNodeIndex === null) {
                setSelectedNodeIndex(clickedNodeIndex);
            } else if (selectedNodeIndex === clickedNodeIndex) {
                setSelectedNodeIndex(null);
            } else {
                // בדיקה אם הקשר כבר קיים כדי למנוע כפילויות
                const linkExists = links.some(l => 
                    (l.from === selectedNodeIndex && l.to === clickedNodeIndex) ||
                    (l.from === clickedNodeIndex && l.to === selectedNodeIndex)
                );
                
                if (!linkExists) {
                    setLinks([...links, { from: selectedNodeIndex, to: clickedNodeIndex }]);
                }
                setSelectedNodeIndex(null);
            }
        } else {
            // לחיצה על רקע ריק
            if (selectedNodeIndex !== null) {
                setSelectedNodeIndex(null);
            } else {
                setNodes([...nodes, { x, y, text: "" }]);
            }
        }
    };

    const handleDoubleClick = (event) => {
        const rect = canvasRef.current.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        const clickedNodeIndex = nodes.findIndex(node => isInsideNode(x, y, node));
        if (clickedNodeIndex !== -1) {
            setEditingIndex(clickedNodeIndex);
            setTempText(nodes[clickedNodeIndex].text);
        }
    };

    const saveText = () => {
        if (editingIndex !== null) {
            const newNodes = [...nodes];
            newNodes[editingIndex].text = tempText;
            setNodes(newNodes);
            setEditingIndex(null);
        }
    };

    return (
        <div className="flex flex-col items-center bg-gray-900 h-screen p-8 relative overflow-hidden">
            <div className="text-white mb-4 text-center">
                <p className="text-sm opacity-70">קליק: יצירה/בחירה | גרירה: הזזה | דאבל קליק: עריכה</p>
            </div>
            
            <canvas
                ref={canvasRef}
                width={1800}
                height={800}
                onMouseDown={handleMouseDown}
                onMouseMove={handleMouseMove}
                onMouseUp={handleMouseUp}
                onClick={handleCanvasClick}
                onDoubleClick={handleDoubleClick}
                className="bg-gray-800 border-2 border-indigo-500 rounded-lg cursor-crosshair shadow-2xl"
            />

            {editingIndex !== null && (
                <div style={{
                    position: 'absolute',
                    top: nodes[editingIndex].y + 40,
                    left: nodes[editingIndex].x + 40,
                    zIndex: 20
                }}>
                    <input 
                        autoFocus
                        value={tempText}
                        onChange={(e) => setTempText(e.target.value)}
                        onBlur={saveText}
                        onKeyDown={(e) => e.key === 'Enter' && saveText()}
                        className="p-2 rounded bg-white text-black border-2 border-indigo-500 shadow-lg outline-none"
                    />
                </div>
            )}
        </div>
    );
}

export default NewCanvas;