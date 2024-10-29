import React from 'react';
import { Link } from 'react-router-dom';
import './Navbar.css';

function Navbar() {
  return (
    <nav className="navbar">
      <h1 className="navbar-logo">Shoptimum</h1>
      <ul className="navbar-links">
        <li><Link to="/">Home</Link></li>
        <li><Link to="/preferences">Preferences</Link></li>
        <li><Link to="/recommendations">Recommendations</Link></li>
      </ul>
    </nav>
  );
}

export default Navbar;