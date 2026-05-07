export const drawLink = (ctx, startNode, endNode) => {
    ctx.beginPath();
    ctx.moveTo(startNode.x, startNode.y);
    ctx.lineTo(endNode.x, endNode.y);
    ctx.strokeStyle = "#94a3b8";
    ctx.lineWidth = 2;
    ctx.stroke();
};