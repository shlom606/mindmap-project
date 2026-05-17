// src/components/SearchBar.jsx
import React, { useState, useEffect } from 'react';

const SearchBar = ({ onNodeFound }) => {
  const [query, setQuery] = useState('');
  const [searching, setSearching] = useState(false);
  const [matchMessage, setMatchMessage] = useState('');

  useEffect(() => {
    const delayDebounceFn = setTimeout(() => {
      if (query.trim().length > 1) {
        executeSearch(query);
      } else {
        setMatchMessage('');
      }
    }, 500);

    return () => clearTimeout(delayDebounceFn);
  }, [query]);

  const executeSearch = async (text) => {
    setSearching(true);
    try {
      const response = await fetch("http://127.0.0.1:8000/api/semantic-search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query_text: text })
      });
      const data = await response.json();
      
      if (data.status === "success") {
        setMatchMessage(`🎯 הכי קרוב סמנטית: "${data.concept}"`);
        if (onNodeFound) onNodeFound(data.concept); // מעביר את שם הצומת שמצאנו למעלה
      } else {
        setMatchMessage("❌ לא נמצאו מושגים מאונדקסים");
      }
    } catch (err) {
      console.error("Search failed", err);
    } finally {
      setSearching(false);
    }
  };

  return (
    <div style={{ margin: '15px 0', position: 'relative' }}>
      <input
        type="text"
        placeholder="🔍 חיפוש סמנטי מהיר בגרף (HNSW)..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        style={{
          width: '100%', padding: '12px', borderRadius: '6px',
          background: '#1a1a24', color: '#fff', border: '1px solid #00f2fe',
          outline: 'none', fontSize: '14px'
        }}
      />
      {searching && <span style={{ position: 'absolute', right: '15px', top: '12px', color: '#00f2fe' }}>⚡</span>}
      {matchMessage && (
        <div style={{ marginTop: '5px', fontSize: '12px', color: '#4facfe', paddingRight: '5px' }}>
          {matchMessage}
        </div>
      )}
    </div>
  );
};

export default SearchBar;