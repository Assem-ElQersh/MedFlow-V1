import axios from 'axios';
import React, { useEffect, useState } from 'react';
import { Link, Navigate, Route, BrowserRouter as Router, Routes } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import ImageUpload from './components/ImageUpload';
import Login from './components/Login';
import PatientConsultation from './components/PatientConsultation';
import TriageQueue from './components/TriageQueue';

// Configure axios defaults
axios.defaults.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem('token');
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      fetchCurrentUser();
    } else {
      setLoading(false);
    }
  }, []);

  const fetchCurrentUser = async () => {
    try {
      const response = await axios.get('/auth/me');
      setUser(response.data);
    } catch (error) {
      console.error('Error fetching user:', error);
      localStorage.removeItem('token');
      delete axios.defaults.headers.common['Authorization'];
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = (userData, token) => {
    localStorage.setItem('token', token);
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    setUser(userData.user);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
    setUser(null);
  };

  if (loading) {
    return (
      <div className="loading">
        <h2>Loading MedFlow AI...</h2>
      </div>
    );
  }

  if (!user) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <Router>
      <div className="App">
        <header className="header">
          <div className="container">
            <h1>🏥 MedFlow AI</h1>
            <p>AI-Powered Medical Assistance System</p>
          </div>
        </header>

        <div className="container">
          <nav className="navigation">
            <Link to="/dashboard" className="nav-btn">Dashboard</Link>
            {user.role === 'patient' && (
              <>
                <Link to="/consultation" className="nav-btn">New Consultation</Link>
                <Link to="/upload-image" className="nav-btn">Upload Image</Link>
              </>
            )}
            {user.role !== 'patient' && (
              <Link to="/triage" className="nav-btn">Triage Queue</Link>
            )}
            <button onClick={handleLogout} className="nav-btn">Logout ({user.full_name})</button>
          </nav>

          <Routes>
            <Route path="/dashboard" element={<Dashboard user={user} />} />
            {user.role === 'patient' && (
              <>
                <Route path="/consultation" element={<PatientConsultation user={user} />} />
                <Route path="/upload-image" element={<ImageUpload user={user} />} />
              </>
            )}
            {user.role !== 'patient' && (
              <Route path="/triage" element={<TriageQueue user={user} />} />
            )}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App; 