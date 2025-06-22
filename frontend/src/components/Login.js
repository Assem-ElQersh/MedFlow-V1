import axios from 'axios';
import React, { useState } from 'react';

function Login({ onLogin }) {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
    role: 'patient'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (isLogin) {
        // Login
        const response = await axios.post('/auth/login', {
          username: formData.email,
          password: formData.password
        }, {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          }
        });
        onLogin(response.data, response.data.access_token);
      } else {
        // Register
        await axios.post('/auth/register', {
          email: formData.email,
          password: formData.password,
          full_name: formData.full_name,
          role: formData.role
        });
        
        // Auto login after registration
        const loginResponse = await axios.post('/auth/login', {
          username: formData.email,
          password: formData.password
        }, {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          }
        });
        onLogin(loginResponse.data, loginResponse.data.access_token);
      }
    } catch (error) {
      setError(error.response?.data?.detail || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
      <div className="card" style={{ maxWidth: '400px', width: '100%', margin: '20px' }}>
        <h2 style={{ textAlign: 'center', marginBottom: '2rem' }}>
          {isLogin ? 'Login to MedFlow AI' : 'Register for MedFlow AI'}
        </h2>

        {error && (
          <div className="alert alert-danger">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {!isLogin && (
            <div className="form-group">
              <label>Full Name</label>
              <input
                type="text"
                name="full_name"
                value={formData.full_name}
                onChange={handleChange}
                required={!isLogin}
                placeholder="Enter your full name"
              />
            </div>
          )}

          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              placeholder="Enter your email"
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              placeholder="Enter your password"
            />
          </div>

          {!isLogin && (
            <div className="form-group">
              <label>Role</label>
              <select name="role" value={formData.role} onChange={handleChange}>
                <option value="patient">Patient</option>
                <option value="physician">Physician</option>
                <option value="nurse">Nurse</option>
                <option value="specialist">Specialist</option>
              </select>
            </div>
          )}

          <button type="submit" className="btn" style={{ width: '100%' }} disabled={loading}>
            {loading ? 'Processing...' : (isLogin ? 'Login' : 'Register')}
          </button>
        </form>

        <div style={{ textAlign: 'center', marginTop: '1rem' }}>
          <button
            type="button"
            onClick={() => setIsLogin(!isLogin)}
            style={{ background: 'none', border: 'none', color: '#667eea', textDecoration: 'underline', cursor: 'pointer' }}
          >
            {isLogin ? "Don't have an account? Register" : "Already have an account? Login"}
          </button>
        </div>

        {isLogin && (
          <div style={{ marginTop: '2rem', padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
            <h4>Demo Credentials:</h4>
            <p><strong>Patient:</strong> patient@demo.com / password123</p>
            <p><strong>Doctor:</strong> doctor@demo.com / password123</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default Login; 