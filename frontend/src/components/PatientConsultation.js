import axios from 'axios';
import React, { useState } from 'react';

function PatientConsultation({ user }) {
  const [formData, setFormData] = useState({
    chief_complaint: '',
    symptoms: '',
    duration: '',
    severity: '5',
    medical_history: '',
    current_medications: '',
    vital_signs: {
      temperature: '',
      blood_pressure: '',
      heart_rate: '',
      respiratory_rate: ''
    }
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    if (name.startsWith('vital_')) {
      const vitalSign = name.replace('vital_', '');
      setFormData({
        ...formData,
        vital_signs: {
          ...formData.vital_signs,
          [vitalSign]: value
        }
      });
    } else {
      setFormData({
        ...formData,
        [name]: value
      });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);

    try {
      // Create consultation
      const consultationResponse = await axios.post('/consultations', {
        chief_complaint: formData.chief_complaint,
        symptoms: formData.symptoms.split(',').map(s => s.trim()),
        medical_history: formData.medical_history.split(',').map(s => s.trim()).filter(s => s),
        current_medications: formData.current_medications.split(',').map(s => s.trim()).filter(s => s),
        duration: formData.duration,
        severity: parseInt(formData.severity),
        vital_signs: formData.vital_signs
      });

      const consultation = consultationResponse.data;

      // Trigger AI triage analysis
      try {
        const triageResponse = await axios.post('/triage/analyze', {
          consultation_id: consultation.id,
          symptoms: formData.symptoms.split(',').map(s => s.trim()),
          medical_history: formData.medical_history.split(',').map(s => s.trim()).filter(s => s),
          vital_signs: formData.vital_signs
        });

        setResult({
          consultation,
          triage: triageResponse.data
        });
      } catch (triageError) {
        console.error('Triage analysis failed:', triageError);
        setResult({
          consultation,
          triage: null,
          triageError: 'AI analysis is temporarily unavailable'
        });
      }

    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to create consultation');
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

  if (result) {
    return (
      <div>
        <div className="alert alert-success">
          <h3>Consultation Created Successfully!</h3>
          <p>Consultation ID: <strong>{result.consultation.id}</strong></p>
        </div>

        {result.triage && (
          <div className="card">
            <h2>AI Triage Assessment</h2>
            <div style={{ marginBottom: '1rem' }}>
              <strong>Triage Level: </strong>
              <span className={`triage-level ${getTriageClass(result.triage.triage_level)}`}>
                {result.triage.triage_level}
              </span>
            </div>
            <div style={{ marginBottom: '1rem' }}>
              <strong>Triage Score: </strong>
              {result.triage.triage_score.toFixed(2)} / 10
            </div>
            <div style={{ marginBottom: '1rem' }}>
              <strong>Confidence: </strong>
              {Math.round(result.triage.confidence * 100)}%
            </div>
            
            <h3>Assessment</h3>
            <div style={{ backgroundColor: '#f8f9fa', padding: '1rem', borderRadius: '8px', marginBottom: '1rem' }}>
              <p><strong>Primary Concern:</strong> {result.triage.assessment.primary_concern}</p>
              <p><strong>Risk Factors:</strong> {result.triage.assessment.risk_factors?.join(', ') || 'None identified'}</p>
              <p><strong>Red Flags:</strong> {result.triage.assessment.red_flags?.join(', ') || 'None identified'}</p>
            </div>

            <h3>Recommendations</h3>
            <ul>
              {result.triage.recommendations.map((recommendation, index) => (
                <li key={index} style={{ marginBottom: '0.5rem' }}>{recommendation}</li>
              ))}
            </ul>
          </div>
        )}

        {result.triageError && (
          <div className="alert alert-warning">
            {result.triageError}
          </div>
        )}

        <button 
          onClick={() => { setResult(null); setFormData({
            chief_complaint: '', symptoms: '', duration: '', severity: '5',
            medical_history: '', current_medications: '',
            vital_signs: { temperature: '', blood_pressure: '', heart_rate: '', respiratory_rate: '' }
          }); }} 
          className="btn"
        >
          Start New Consultation
        </button>
      </div>
    );
  }

  return (
    <div className="card">
      <h2>New Patient Consultation</h2>
      
      {error && (
        <div className="alert alert-danger">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Chief Complaint *</label>
          <textarea
            name="chief_complaint"
            value={formData.chief_complaint}
            onChange={handleChange}
            required
            placeholder="Describe your main concern or reason for this consultation..."
            rows="3"
          />
        </div>

        <div className="form-group">
          <label>Symptoms (comma-separated) *</label>
          <textarea
            name="symptoms"
            value={formData.symptoms}
            onChange={handleChange}
            required
            placeholder="fever, headache, cough, fatigue..."
            rows="2"
          />
        </div>

        <div className="form-group">
          <label>Duration</label>
          <input
            type="text"
            name="duration"
            value={formData.duration}
            onChange={handleChange}
            placeholder="e.g., 3 days, 1 week, 2 hours"
          />
        </div>

        <div className="form-group">
          <label>Severity (1-10) *</label>
          <input
            type="range"
            name="severity"
            value={formData.severity}
            onChange={handleChange}
            min="1"
            max="10"
            required
          />
          <div style={{ textAlign: 'center', marginTop: '0.5rem' }}>
            Current: {formData.severity}/10
          </div>
        </div>

        <div className="form-group">
          <label>Medical History (comma-separated)</label>
          <textarea
            name="medical_history"
            value={formData.medical_history}
            onChange={handleChange}
            placeholder="diabetes, hypertension, asthma..."
            rows="2"
          />
        </div>

        <div className="form-group">
          <label>Current Medications (comma-separated)</label>
          <textarea
            name="current_medications"
            value={formData.current_medications}
            onChange={handleChange}
            placeholder="aspirin, metformin, inhaler..."
            rows="2"
          />
        </div>

        <h3>Vital Signs (Optional)</h3>
        <div className="grid" style={{ gridTemplateColumns: 'repeat(2, 1fr)' }}>
          <div className="form-group">
            <label>Temperature (°F)</label>
            <input
              type="number"
              name="vital_temperature"
              value={formData.vital_signs.temperature}
              onChange={handleChange}
              step="0.1"
              placeholder="98.6"
            />
          </div>

          <div className="form-group">
            <label>Blood Pressure (mmHg)</label>
            <input
              type="text"
              name="vital_blood_pressure"
              value={formData.vital_signs.blood_pressure}
              onChange={handleChange}
              placeholder="120/80"
            />
          </div>

          <div className="form-group">
            <label>Heart Rate (BPM)</label>
            <input
              type="number"
              name="vital_heart_rate"
              value={formData.vital_signs.heart_rate}
              onChange={handleChange}
              placeholder="70"
            />
          </div>

          <div className="form-group">
            <label>Respiratory Rate</label>
            <input
              type="number"
              name="vital_respiratory_rate"
              value={formData.vital_signs.respiratory_rate}
              onChange={handleChange}
              placeholder="16"
            />
          </div>
        </div>

        <button type="submit" className="btn" disabled={loading} style={{ width: '100%' }}>
          {loading ? 'Creating Consultation & Running AI Analysis...' : 'Create Consultation'}
        </button>
      </form>
    </div>
  );
}

export default PatientConsultation; 