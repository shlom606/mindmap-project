export const drawNode = (ctx, node, isSelected) => {
    const radiusX = 50; // רוחב האליפסה
    const radiusY = 30; // גובה האליפסה

    ctx.beginPath();
    // ציור אליפסה: x, y, radiusX, radiusY, rotation, startAngle, endAngle
    ctx.ellipse(node.x, node.y, radiusX, radiusY, 0, 0, 2 * Math.PI);
    
    ctx.fillStyle = isSelected ? "#f87171" : "#6366f1";
    ctx.fill();
    ctx.strokeStyle = "white";
    ctx.lineWidth = 2;
    ctx.stroke();

    // ציור הטקסט (הפתקית) בתוך האליפסה
    if (node.text) {
        ctx.fillStyle = "white";
        ctx.font = "14px Arial";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        // חיתוך טקסט אם הוא ארוך מדי (אופציונלי)
        const displayText = node.text.length > 10 ? node.text.substring(0, 8) + ".." : node.text;
        ctx.fillText(displayText, node.x, node.y);
    }
};