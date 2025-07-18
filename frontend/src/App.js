
// export default App;
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import './index.css';
import DocumentResults from './components/DocumentResults';
import SubjectView from './components/SubjectView';
import DocumentLibrary from './components/DocumentLibrary';

// Main Dashboard Component
const Dashboard = () => {
  const navigate = useNavigate();
  const [showDropdown, setShowDropdown] = useState(false);
  const [message, setMessage] = useState('Loading subjects...');
  const [subjects, setSubjects] = useState([]);
  const [apiConnected, setApiConnected] = useState(false);
  const [uploadedDocument, setUploadedDocument] = useState(null);
  const [showResults, setShowResults] = useState(false);

  useEffect(() => {
    fetchSubjects();
  }, []);

  const fetchSubjects = async () => {
    try {
      const response = await fetch('http://localhost:8000/subjects?include_stats=true');
      if (response.ok) {
        const data = await response.json();
        setSubjects(data);
        setApiConnected(true);
        setMessage(`✅ Loaded ${data.length} subjects from database`);
      } else {
        setMessage('❌ Failed to load subjects');
      }
    } catch (error) {
      setMessage('❌ API not reachable - Make sure backend is running');
    }
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      uploadFile(file);
    }
  };

  const uploadFile = async (file) => {
    setMessage('🔄 Uploading file...');
    
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/extract', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setMessage(`✅ Uploaded ${file.name} successfully!`);
        setUploadedDocument(data.document);
        setShowResults(true);
        fetchSubjects();
      } else {
        const error = await response.json();
        setMessage(`❌ Upload failed: ${error.detail}`);
      }
    } catch (error) {
      setMessage('❌ Upload failed - Check your connection');
    }
  };

  const addNewSubject = async () => {
    const subjectName = prompt('Enter subject name:');
    if (subjectName) {
      try {
        const response = await fetch('http://localhost:8000/subjects', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            subject_name: subjectName,
            description: `Subject for ${subjectName}`,
            keywords: [subjectName.toLowerCase()],
          }),
        });

        if (response.ok) {
          setMessage(`✅ Added subject: ${subjectName}`);
          fetchSubjects();
        } else {
          setMessage('❌ Failed to add subject');
        }
      } catch (error) {
        setMessage('❌ Failed to add subject');
      }
    }
  };

  // Updated color array with your specified colors and translucency
  const subjectColors = [
    'rgba(162, 139, 108, 0.6)', // A28B6C with translucency
    'rgba(192, 192, 192, 0.6)', // C0C0C0 with translucency
    'rgba(213, 196, 167, 0.6)', // D5C4A7 with translucency
    'rgba(162, 139, 108, 0.6)', // A28B6C with more translucency
    'rgba(192, 192, 192, 0.6)', // C0C0C0 with more translucency
    'rgba(213, 196, 167, 0.6)'  // D5C4A7 with more translucency
  ];

  return (
    <div>
      {/* Header with Dropdown */}
      <div className="header">
        <div className="container">
          <div className="header-content">
            {/* Dropdown Menu */}
            <div style={{ position: 'relative' }}>
              <button 
                onClick={(e) => {
                  e.stopPropagation();
                  console.log('🍔 Hamburger clicked!');
                  setShowDropdown(!showDropdown);
                }}
                style={{ 
                  background: 'none', 
                  border: 'none', 
                  fontSize: '24px', 
                  cursor: 'pointer',
                  padding: '8px',
                  zIndex: 10001,
                  position: 'relative',
                  color: 'white'
                }}
              >
                ☰
              </button>
              
              {/* Dropdown Content */}
              {showDropdown && (
                <>
                  {/* Background overlay to close dropdown */}
                  <div 
                    style={{
                      position: 'fixed',
                      top: 0,
                      left: 0,
                      right: 0,
                      bottom: 0,
                      zIndex: 9998,
                      background: 'transparent'
                    }}
                    onClick={() => {
                      console.log('🌍 Overlay clicked - closing dropdown');
                      setShowDropdown(false);
                    }}
                  />
                  
                  {/* Dropdown menu */}
                  <div style={{
                    position: 'absolute',
                    top: '100%',
                    left: '-50px',
                    background: 'rgba(240, 237, 232, 0.95)',
                    border: '1px solid rgba(162, 139, 108, 0.3)',
                    borderRadius: '8px',
                    boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
                    zIndex: 9999,
                    minWidth: '200px',
                    marginTop: '4px'
                  }}>
                    <button
  onClick={(e) => {
    e.stopPropagation();
    console.log('🏠 Dashboard clicked!');
    setShowDropdown(false);
    navigate('/');
  }}
  style={{
    width: '100%',
    padding: '12px 16px',
    border: 'none',
    background: 'none',
    textAlign: 'left',
    cursor: 'pointer',
    fontSize: '16px',
    color: '#374151',
    display: 'flex',
    alignItems: 'center',
    gap: '10px'
  }}
  onMouseEnter={(e) => e.target.style.backgroundColor = 'rgba(162, 139, 108, 0.1)'}
  onMouseLeave={(e) => e.target.style.backgroundColor = 'transparent'}
>
  <svg xmlns="http://www.w3.org/2000/svg" fill="black" width="20" height="20" viewBox="0 0 24 24">
    <path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/>
  </svg>
  Dashboard
</button>

<button
  onClick={(e) => {
    e.stopPropagation();
    console.log('📚 Document Library clicked!');
    setShowDropdown(false);
    navigate('/library');
  }}
  style={{
    width: '100%',
    padding: '12px 16px',
    border: 'none',
    background: 'none',
    textAlign: 'left',
    cursor: 'pointer',
    fontSize: '16px',
    color: '#374151',
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    borderTop: '1px solid rgba(162, 139, 108, 0.2)'
  }}
  onMouseEnter={(e) => e.target.style.backgroundColor = 'rgba(162, 139, 108, 0.1)'}
  onMouseLeave={(e) => e.target.style.backgroundColor = 'transparent'}
>
  <svg xmlns="http://www.w3.org/2000/svg" fill="black" width="20" height="20" viewBox="0 0 24 24">
    <path d="M4 6v16h16V6H4zm4 2h8v2H8V8zm0 4h8v2H8v-2zm0 4h5v2H8v-2zM6 2h12v2H6V2z"/>
  </svg>
  Document Library
</button>

                  </div>
                </>
              )}
            </div>
            
            <div className="logo-text">CLUTTERFLOW</div>
            <div></div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        <div className="container">
          <div className="grid grid-cols-2" style={{ marginBottom: '30px' }}>
            <div className="upload-area" onClick={() => document.getElementById('fileInput').click()}>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>⬆</div>
              <div style={{ fontSize: '18px', color: '#374151' }}>
                drag and drop/ chose file
              </div>
              <input
                id="fileInput"
                type="file"
                accept=".pdf,.png,.jpg,.jpeg"
                style={{ display: 'none' }}
                onChange={handleFileUpload}
              />
            </div>

            <div className="upload-area" onClick={addNewSubject}>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>⊕</div>
              <div style={{ fontSize: '18px', color: '#374151' }}>
                add new subject
              </div>
            </div>
          </div>

          <div className="grid grid-cols-3">
            {subjects.map((subject, index) => (
              <div
                key={subject.id}
                className="subject-card"
                style={{ 
                  background: subjectColors[index % subjectColors.length],
                  cursor: 'pointer'
                }}
                onClick={() => navigate(`/subject/${subject.id}`)}
              >
                <div style={{ textAlign: 'center' }}>
                  <div>{subject.subject_name}</div>
                  {subject.document_count !== undefined && (
                    <div style={{ fontSize: '14px', opacity: '0.8', marginTop: '4px' }}>
                      {subject.document_count} docs
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

          <div className="card-base" style={{ padding: '20px', textAlign: 'center', marginTop: '30px' }}>
            <p style={{ color: '#64748b', margin: '0' }}>{message}</p>
          </div>
        </div>
      </div>

      {showResults && uploadedDocument && (
        <DocumentResults
          document={uploadedDocument}
          onClose={() => {
            setShowResults(false);
            setUploadedDocument(null);
          }}
          onSubjectAssigned={(subject) => {
            setMessage(`✅ Document assigned to ${subject.subject_name}`);
            fetchSubjects();
          }}
        />
      )}
    </div>
  );
};

// Main App with Router
function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/subject/:subjectId" element={<SubjectView />} />
        <Route path="/library" element={<DocumentLibrary />} />
      </Routes>
    </Router>
  );
}

export default App;