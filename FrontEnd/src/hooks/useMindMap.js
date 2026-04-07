import { useState, useCallback } from 'react';

export const useMindMap = () => {
    const [graphData, setGraphData] = useState({ nodes: [], links: [] });
    const [loading, setLoading] = useState(false);

    const addConcept = useCallback(async (text) => {
        if (!text.trim()) return;

        setLoading(true);
        
        // כאן בעתיד תבצע fetch ל-API של הפייתון שלך
        // כרגע נבצע סימולציה של הוספת צומת
        const newNode = { 
            id: text, 
            name: text, 
            val: 10, // גודל העיגול
            color: '#4f46e5' // צבע ברירת מחדל
        };

        setGraphData(prev => {
            const isExist = prev.nodes.find(n => n.id === newNode.id);
            if (isExist) return prev;

            // חיבור אוטומטי לצומת האחרון לצורך התצוגה הראשונית
            const newLinks = prev.nodes.length > 0 
                ? [...prev.links, { source: prev.nodes[prev.nodes.length - 1].id, target: newNode.id }]
                : prev.links;

            return {
                nodes: [...prev.nodes, newNode],
                links: newLinks
            };
        });
        
        setLoading(false);
    }, []);

    return { graphData, addConcept, loading };
};