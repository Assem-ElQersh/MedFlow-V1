import axios from 'axios';
import React, { useEffect, useState } from 'react';

function Dashboard({ user }) {
  const [consultations, setConsultations] = useState([]);
  const [stats, setStats] = useState(null);
  const [serviceStatus, setServiceStatus] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [consultationsRes, servicesRes] = await Promise.all([
        axios.get('/consultations'),
        axios.get('/services/status')
      ]);

      setConsultations(consultationsRes.data);
      setServiceStatus(servicesRes.data);

      // Mock stats for demonstration
      setStats({
        totalConsultations: consultationsRes.data.length,
        pendingReviews: consultationsRes.data.filter(c => c.status === 'pending').length,
        todayConsultations: Math.floor(Math.random() * 20) + 5,
        aiAccuracy: 0.91
      });
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getTriageClass = (level) => {
    switch (level) {
      case 'critical': return 'triage-critical';
      case 'urgent': return 'triage-urgent';
      case 'routine': return 'triage-routine';
      default: return 'triage-routine';
    }
  };

  if (loading) {
    return <div className="loading">Loading dashboard...</div>;
  }

  return (
    <div>
      <div className="card">
        <h2>Welcome, {user.full_name}</h2>
        <p>Role: <strong>{user.role.charAt(0).toUpperCase() + user.role.slice(1)}</strong></p>
        <p>Today's date: {new Date().toLocaleDateString()}</p>
      </div>

      {stats && (
        <div className="grid">
          <div className="stats-card">
            <div className="stats-number">{stats.totalConsultations}</div>
            <div className="stats-label">Total Consultations</div>
          </div>
          <div className="stats-card">
            <div className="stats-number">{stats.pendingReviews}</div>
            <div className="stats-label">Pending Reviews</div>
          </div>
          <div className="stats-card">
            <div className="stats-number">{stats.todayConsultations}</div>
            <div className="stats-label">Today's Consultations</div>
          </div>
          <div className="stats-card">
            <div className="stats-number">{Math.round(stats.aiAccuracy * 100)}%</div>
            <div className="stats-label">AI Accuracy</div>
          </div>
        </div>
      )}

      <div className="card">
        <h2>Recent Consultations</h2>
        {consultations.length === 0 ? (
          <p>No consultations found.</p>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid #e1e8ed' }}>
                  <th style={{ padding: '12px', textAlign: 'left' }}>ID</th>
                  <th style={{ padding: '12px', textAlign: 'left' }}>Chief Complaint</th>
                  <th style={{ padding: '12px', textAlign: 'left' }}>Triage Level</th>
                  <th style={{ padding: '12px', textAlign: 'left' }}>Status</th>
                  <th style={{ padding: '12px', textAlign: 'left' }}>Created</th>
                </tr>
              </thead>
              <tbody>
                {consultations.slice(0, 10).map((consultation) => (
                  <tr key={consultation.id} style={{ borderBottom: '1px solid #e1e8ed' }}>
                    <td style={{ padding: '12px' }}>{consultation.id}</td>
                    <td style={{ padding: '12px' }}>{consultation.chief_complaint}</td>
                    <td style={{ padding: '12px' }}>
                      {consultation.triage_level ? (
                        <span className={`triage-level ${getTriageClass(consultation.triage_level)}`}>
                          {consultation.triage_level}
                        </span>
                      ) : (
                        <span>Pending</span>
                      )}
                    </td>
                    <td style={{ padding: '12px' }}>
                      <span style={{ 
                        padding: '4px 8px', 
                        borderRadius: '4px', 
                        backgroundColor: consultation.status === 'completed' ? '#d4edda' : '#fff3cd',
                        color: consultation.status === 'completed' ? '#155724' : '#856404'
                      }}>
                        {consultation.status}
                      </span>
                    </td>
                    <td style={{ padding: '12px' }}>
                      {new Date(consultation.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="card">
        <h2>System Status</h2>
        <div className="grid">
          {Object.entries(serviceStatus).map(([serviceName, status]) => (
            <div key={serviceName} className="stats-card">
              <div style={{ 
                fontSize: '1.2rem', 
                marginBottom: '0.5rem',
                color: status.status === 'healthy' ? '#28a745' : 
                      status.status === 'unhealthy' ? '#ffc107' : '#dc3545'
              }}>
                {status.status === 'healthy' ? '✅' : 
                 status.status === 'unhealthy' ? '⚠️' : '❌'}
              </div>
              <div className="stats-label" style={{ fontWeight: 'bold' }}>
                {serviceName.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </div>
              <div className="stats-label">{status.status}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Dashboard; 