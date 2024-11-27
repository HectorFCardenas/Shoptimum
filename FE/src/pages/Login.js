import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Login.css';

function Login() {
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && name.trim() !== '') {
      handleLogin();
    }
  };

  const handleLogin = async () => {
    if (name.trim() !== '') {
      try {
        const response = await fetch('http://127.0.0.1:5000/mealplans/check');
        const data = await response.json();
        if (data.exists) {
          navigate('/home'); // Navigate to the home page
        } else {
          navigate('/set-initial-recommendations'); // Navigate to recommendations setup
        }
      } catch (error) {
        console.error('Error checking meal plans:', error);
        alert('Something went wrong. Please try again.');
      }
    }
  };

  return (
    <div className="login-container">
      <div className="floating-background">
        <div className="floating-element utensil">🍴</div>
        <div className="floating-element laptop">💻</div>
        <div className="floating-element chef-hat">👩‍🍳</div>
        <div className="floating-element cookie">🍪</div>
        <div className="floating-element pizza">🍕</div>
        <div className="floating-element burger">🍔</div>
        <div className="floating-element salad">🥗</div>
        <div className="floating-element tablet">📱</div>
        <div className="floating-element cake">🍰</div>
        <div className="floating-element coffee">☕</div>
        <div className="floating-element sushi">🍣</div>
        <div className="floating-element cupcake">🧁</div>
      </div>
      <div className="login-box">
        <h1>Welcome to Shoptimum</h1>
        <input
          type="text"
          placeholder="Enter your name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          onKeyDown={handleKeyPress}
        />
        <button onClick={handleLogin} disabled={name.trim() === '' || loading}>
          {loading ? 'Loading...' : 'Login'}
        </button>
      </div>
    </div>
  );
}

export default Login;