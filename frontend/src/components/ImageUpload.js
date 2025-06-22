import axios from 'axios';
import React, { useState } from 'react';

function ImageUpload({ user }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [imageType, setImageType] = useState('xray');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!selectedFile) {
      setError('Please select an image file');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('image_type', imageType);
      formData.append('user_id', user.id);

      const uploadResponse = await axios.post('/images/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        }
      });

      const uploadResult = uploadResponse.data;
      
        setResult({
        upload: uploadResult
        });

    } catch (error) {
      setError(error.response?.data?.detail || 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  const handleNewUpload = () => {
    setResult(null);
    setSelectedFile(null);
    setError('');
  };

  if (result) {
    return (
      <div>
        <div className="alert alert-success">
          <h3>🎉 Image Uploaded Successfully!</h3>
          <p>Image ID: <strong>{result.upload.id}</strong></p>
          <p>Status: <strong>{result.upload.status}</strong></p>
          <p>Message: <em>{result.upload.message}</em></p>
        </div>

        {result.upload && result.upload.analysis && (
          <div className="card">
            <h2>🤖 MedGemma AI Analysis</h2>
            
            <div style={{ marginBottom: '1.5rem' }}>
              <strong>AI Model: </strong>
              <span style={{ color: '#007bff', fontWeight: 'bold' }}>
                {result.upload.ai_model || 'MedGemma 4B'}
              </span>
            </div>

            <h3>🔍 Analysis Results</h3>
            <div style={{ backgroundColor: '#f8f9fa', padding: '1rem', borderRadius: '8px', marginBottom: '1rem' }}>
              {(result.upload.analysis.findings || []).map((finding, index) => (
                <p key={index} style={{ marginBottom: '0.5rem', lineHeight: '1.5' }}>{finding}</p>
              ))}
            </div>

            <h3>💡 Recommendation</h3>
            <div style={{ backgroundColor: '#e7f3ff', padding: '1rem', borderRadius: '8px', marginBottom: '1rem', borderLeft: '4px solid #007bff' }}>
              <p>{result.upload.analysis.recommendation}</p>
            </div>
          </div>
        )}

        {result.analysisError && (
          <div className="alert alert-warning">
            {result.analysisError}
          </div>
        )}

        <button onClick={handleNewUpload} className="btn">
          Upload Another Image
        </button>
      </div>
    );
  }

  return (
    <div className="card">
      <h2>Medical Image Upload</h2>
      <p>Upload medical images for AI-powered analysis and diagnosis assistance.</p>

      {error && (
        <div className="alert alert-danger">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Image Type *</label>
          <select 
            value={imageType} 
            onChange={(e) => setImageType(e.target.value)}
            required
          >
            <option value="xray">X-Ray</option>
            <option value="ct">CT Scan</option>
            <option value="mri">MRI</option>
            <option value="skin">Skin/Dermatology</option>
            <option value="fundus">Eye/Fundus</option>
          </select>
        </div>

        <div className="form-group">
          <label>Select Image File *</label>
          <input
            type="file"
            onChange={handleFileChange}
            accept="image/*"
            required
            style={{
              width: '100%',
              padding: '12px',
              border: '2px dashed #e1e8ed',
              borderRadius: '8px',
              textAlign: 'center',
              cursor: 'pointer'
            }}
          />
          {selectedFile && (
            <p style={{ marginTop: '0.5rem', color: '#28a745' }}>
              Selected: {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
            </p>
          )}
        </div>

        {selectedFile && (
          <div className="form-group">
            <label>Preview</label>
            <img
              src={URL.createObjectURL(selectedFile)}
              alt="Preview"
              style={{
                maxWidth: '100%',
                maxHeight: '300px',
                borderRadius: '8px',
                border: '1px solid #e1e8ed'
              }}
            />
          </div>
        )}

        <div style={{ backgroundColor: '#fff3cd', padding: '1rem', borderRadius: '8px', marginBottom: '1rem' }}>
          <h4>⚠️ Important Notes:</h4>
          <ul style={{ margin: '0.5rem 0' }}>
            <li>Ensure images are clear and properly oriented</li>
            <li>Remove any personal identifying information</li>
            <li>AI analysis is for assistance only - not a replacement for professional medical opinion</li>
            <li>High-priority findings will be flagged for immediate review</li>
          </ul>
        </div>

        <button type="submit" className="btn" disabled={loading || !selectedFile} style={{ width: '100%' }}>
          {loading ? 'Uploading & Analyzing...' : 'Upload & Analyze Image'}
        </button>
      </form>
    </div>
  );
}

export default ImageUpload; 