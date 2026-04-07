import React, { useEffect, useRef } from 'react'

function Canvas() {
    const canvas = useRef();
    const example = () => {
        const ctx = canvas.current.getContext("2d");
        ctx.beginPath();
        ctx.arc(95, 50, 40, 0, 2 * Math.PI);
        ctx.stroke();
    }
    
    useEffect(() => {
      
    if (canvas.current) {
        example();
    }
      return () => {
        
      }
    }, [canvas.current])
    

    return (
        <canvas ref={canvas}>

        </canvas>
    )
}


export default Canvas