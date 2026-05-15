import React, { useState } from 'react';

const Auth = ({ onLoginSuccess }) => {
  const [isLogin, setIsLogin] = useState(true); // Toggle state
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    const endpoint = isLogin ? "login" : "signup";
    
    try {
      const response = await fetch(`http://127.0.0.1:8000/${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      const result = await response.json();

      if (response.ok) {
        if (isLogin) {
          // Pass the username back to App.jsx on success
          onLoginSuccess(username);
        } else {
          alert("Account created successfully! Now please login.");
          setIsLogin(true); // Switch to login mode after signup
          setPassword("");  // Clear password for security
        }
      } else {
        alert(result.detail || "Something went wrong.");
      }
    } catch (err) {
      alert("Failed to connect to the server. Is your backend running?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-overlay" style={styles.overlay}>
      <div className="auth-card" style={styles.card}>
        <h2 style={styles.title}>{isLogin ? "Welcome Back" : "Create Account"}</h2>
        <p style={styles.subtitle}>
          {isLogin ? "Login to access your mind maps" : "Join MindNet to start mapping"}
        </p>

        <form onSubmit={handleSubmit} style={styles.form}>
          <input 
            style={styles.input}
            type="text" 
            placeholder="Username" 
            value={username} 
            onChange={(e) => setUsername(e.target.value)} 
            required 
          />
          <input 
            style={styles.input}
            type="password" 
            placeholder="Password" 
            value={password} 
            onChange={(e) => setPassword(e.target.value)} 
            required 
          />
          <button 
            type="submit" 
            disabled={loading} 
            style={styles.button}
          >
            {loading ? "Processing..." : (isLogin ? "Login" : "Sign Up")}
          </button>
        </form>

        <p style={styles.toggleText}>
          {isLogin ? "New here?" : "Already have an account?"}{" "}
          <span 
            onClick={() => setIsLogin(!isLogin)} 
            style={styles.toggleLink}
          >
            {isLogin ? "Sign up now" : "Log in here"}
          </span>
        </p>
      </div>
    </div>
  );
};

// Inline styles for quick setup (you can move these to App.css)
const styles = {
  overlay: {
    height: '100vh',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    background: '#050a0f',
  },
  card: {
    background: 'rgba(255, 255, 255, 0.05)',
    backdropFilter: 'blur(10px)',
    padding: '40px',
    borderRadius: '20px',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    width: '350px',
    textAlign: 'center',
    boxShadow: '0 10px 30px rgba(0,0,0,0.5)'
  },
  title: { color: '#4facfe', margin: '0 0 10px 0' },
  subtitle: { color: '#888', fontSize: '14px', marginBottom: '25px' },
  form: { display: 'flex', flexDirection: 'column', gap: '15px' },
  input: {
    padding: '12px',
    borderRadius: '8px',
    border: '1px solid #333',
    background: '#1a222d',
    color: 'white',
    outline: 'none'
  },
  button: {
    padding: '12px',
    borderRadius: '8px',
    border: 'none',
    background: 'linear-gradient(45deg, #00f2fe 0%, #4facfe 100%)',
    color: '#000',
    fontWeight: 'bold',
    cursor: 'pointer',
    marginTop: '10px'
  },
  toggleText: { color: '#888', marginTop: '20px', fontSize: '13px' },
  toggleLink: { color: '#4facfe', cursor: 'pointer', fontWeight: 'bold' }
};

export default Auth;