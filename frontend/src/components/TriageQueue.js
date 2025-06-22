import axios from 'axios';
import React, { useEffect, useState } from 'react';

function TriageQueue({ user }) {
  const [queue, setQueue] = useState({ critical: [], urgent: [], routine: [] });
  const [stats, setStats] = useState(null);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    fetchTriageData();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchTriageData, 30000);
    
    return () => {
      clearInterval(interval);
    };
  }, []);

  const fetchTriageData = async () => {
    try {
      const [queueRes, statsRes] = await Promise.all([
        axios.get('/triage/queue'),
        axios.get('/triage/stats')
      ]);

      setQueue(queueRes.data);
      setStats(statsRes.data);
    } catch (error) {
      console.error('Error fetching triage data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePatientClick = async (patientId) => {
    try {
      const response = await axios.get(`/consultations/${patientId}`);
      setSelectedPatient(response.data);
    } catch (error) {
      console.error('Error fetching patient details:', error);
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

  const renderPatientCard = (patient, level) => (
    <div 
      key={patient.consultation_id}
      style={{
        backgroundColor: 'white',
        border: `2px solid ${
          level === 'critical' ? '#dc3545' : 
          level === 'urgent' ? '#ffc107' : '#28a745'
        }`,
        borderRadius: '8px',
        padding: '1rem',
        marginBottom: '1rem',
        cursor: 'pointer',
        transition: 'transform 0.2s ease'
      }}
      onClick={() => handlePatientClick(patient.consultation_id)}
      onMouseEnter={(e) => e.target.style.transform = 'translateY(-2px)'}
      onMouseLeave={(e) => e.target.style.transform = 'translateY(0)'}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h4 style={{ margin: '0 0 0.5rem 0' }}>{patient.patient_name}</h4>
          <p style={{ margin: '0 0 0.5rem 0', color: '#666' }}>{patient.chief_complaint}</p>
          <span className={`triage-level ${getTriageClass(level)}`}>
            {level.toUpperCase()}
          </span>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#dc3545' }}>
            {patient.wait_time}
          </div>
          <div style={{ fontSize: '0.8rem', color: '#666' }}>
            Wait Time
          </div>
        </div>
      </div>
    </div>
  );

  if (loading) {
    return <div className="loading">Loading triage queue...</div>;
  }

  return (
    <div>
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2>Triage Queue - {user.role.charAt(0).toUpperCase() + user.role.slice(1)} View</h2>
          <button onClick={fetchTriageData} className="btn btn-secondary">
            🔄 Refresh
          </button>
        </div>
      </div>

      {stats && (
        <div className="grid">
          <div className="stats-card">
            <div className="stats-number">{stats.total_patients}</div>
            <div className="stats-label">Total Patients</div>
          </div>
          <div className="stats-card">
            <div className="stats-number">{stats.current_queue}</div>
            <div className="stats-label">In Queue</div>
          </div>
          <div className="stats-card">
            <div className="stats-number">{stats.processed_today}</div>
            <div className="stats-label">Processed Today</div>
          </div>
          <div className="stats-card">
            <div className="stats-number">{Math.round(stats.ai_accuracy * 100)}%</div>
            <div className="stats-label">AI Accuracy</div>
          </div>
        </div>
      )}

      <div className="grid">
        {/* Critical Patients */}
        <div className="card" style={{ borderLeft: '5px solid #dc3545' }}>
          <h3 style={{ color: '#dc3545', display: 'flex', alignItems: 'center' }}>
            🚨 Critical ({queue.critical.length})
          </h3>
          <p style={{ color: '#666', fontSize: '0.9rem' }}>
            Avg Wait: {stats?.average_wait_time?.critical}
          </p>
          {queue.critical.length === 0 ? (
            <p style={{ color: '#666', fontStyle: 'italic' }}>No critical patients</p>
          ) : (
            queue.critical.map(patient => renderPatientCard(patient, 'critical'))
          )}
        </div>

        {/* Urgent Patients */}
        <div className="card" style={{ borderLeft: '5px solid #ffc107' }}>
          <h3 style={{ color: '#ffc107', display: 'flex', alignItems: 'center' }}>
            ⚠️ Urgent ({queue.urgent.length})
          </h3>
          <p style={{ color: '#666', fontSize: '0.9rem' }}>
            Avg Wait: {stats?.average_wait_time?.urgent}
          </p>
          {queue.urgent.length === 0 ? (
            <p style={{ color: '#666', fontStyle: 'italic' }}>No urgent patients</p>
          ) : (
            queue.urgent.map(patient => renderPatientCard(patient, 'urgent'))
          )}
        </div>

        {/* Routine Patients */}
        <div className="card" style={{ borderLeft: '5px solid #28a745' }}>
          <h3 style={{ color: '#28a745', display: 'flex', alignItems: 'center' }}>
            ✅ Routine ({queue.routine.length})
          </h3>
          <p style={{ color: '#666', fontSize: '0.9rem' }}>
            Avg Wait: {stats?.average_wait_time?.routine}
          </p>
          {queue.routine.length === 0 ? (
            <p style={{ color: '#666', fontStyle: 'italic' }}>No routine patients</p>
          ) : (
            queue.routine.map(patient => renderPatientCard(patient, 'routine'))
          )}
        </div>
      </div>

      {/* Patient Details Modal */}
      {selectedPatient && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            backgroundColor: 'white',
            borderRadius: '12px',
            padding: '2rem',
            maxWidth: '600px',
            width: '90%',
            maxHeight: '80vh',
            overflowY: 'auto'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h2>Patient Details</h2>
              <button 
                onClick={() => setSelectedPatient(null)}
                style={{ background: 'none', border: 'none', fontSize: '1.5rem', cursor: 'pointer' }}
              >
                ✕
              </button>
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <strong>Patient ID:</strong> {selectedPatient.patient_id}
            </div>
            <div style={{ marginBottom: '1rem' }}>
              <strong>Chief Complaint:</strong> {selectedPatient.chief_complaint}
            </div>
            <div style={{ marginBottom: '1rem' }}>
              <strong>Symptoms:</strong> {selectedPatient.symptoms?.join(', ')}
            </div>
            <div style={{ marginBottom: '1rem' }}>
              <strong>Duration:</strong> {selectedPatient.duration}
            </div>
            <div style={{ marginBottom: '1rem' }}>
              <strong>Severity:</strong> {selectedPatient.severity}/10
            </div>
            <div style={{ marginBottom: '1rem' }}>
              <strong>Medical History:</strong> {selectedPatient.medical_history?.join(', ') || 'None'}
            </div>

            {selectedPatient.triage_assessment && (
              <div style={{ backgroundColor: '#f8f9fa', padding: '1rem', borderRadius: '8px', marginBottom: '1rem' }}>
                <h4>AI Triage Assessment</h4>
                <p><strong>Level:</strong> 
                  <span className={`triage-level ${getTriageClass(selectedPatient.triage_assessment.level)}`}>
                    {selectedPatient.triage_assessment.level}
                  </span>
                </p>
                <p><strong>Confidence:</strong> {Math.round(selectedPatient.triage_assessment.confidence * 100)}%</p>
                <p><strong>Recommendations:</strong></p>
                <ul>
                  {selectedPatient.triage_assessment.recommendations?.map((rec, index) => (
                    <li key={index}>{rec}</li>
                  ))}
                </ul>
              </div>
            )}

            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end' }}>
              <button className="btn btn-success">Accept Patient</button>
              <button className="btn btn-secondary">Refer to Specialist</button>
              <button onClick={() => setSelectedPatient(null)} className="btn">Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default TriageQueue; 