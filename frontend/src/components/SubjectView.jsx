// // src/components/SubjectView.jsx
// import React, { useState, useEffect } from 'react';
// import { useParams, useNavigate } from 'react-router-dom';

// const SubjectView = () => {
//   const { subjectId } = useParams();
//   const navigate = useNavigate();
  
//   const [subject, setSubject] = useState(null);
//   const [documents, setDocuments] = useState([]);
//   const [subjects, setSubjects] = useState([]);
//   const [loading, setLoading] = useState(true);
//   const [selectedDocument, setSelectedDocument] = useState(null);
//   const [showSummary, setShowSummary] = useState(false);
//   const [showMoveModal, setShowMoveModal] = useState(false);
//   const [documentToMove, setDocumentToMove] = useState(null);

//   useEffect(() => {
//     if (subjectId) {
//       fetchSubjectData();
//       fetchAllSubjects();
//     }
//   }, [subjectId]);

//   const fetchSubjectData = async () => {
//     try {
//       // Get subject info
//       const subjectResponse = await fetch(`http://localhost:8000/subjects/${subjectId}`);
//       if (subjectResponse.ok) {
//         const subjectData = await subjectResponse.json();
//         setSubject(subjectData);
//       }

//       // Get documents in this subject
//       const documentsResponse = await fetch(`http://localhost:8000/subjects/${subjectId}/documents`);
//       if (documentsResponse.ok) {
//         const documentsData = await documentsResponse.json();
//         setDocuments(documentsData.documents || []);
//       }

//       setLoading(false);
//     } catch (error) {
//       console.error('Failed to fetch subject data:', error);
//       setLoading(false);
//     }
//   };

//   const fetchAllSubjects = async () => {
//     try {
//       const response = await fetch('http://localhost:8000/subjects');
//       if (response.ok) {
//         const data = await response.json();
//         setSubjects(data);
//       }
//     } catch (error) {
//       console.error('Failed to fetch subjects:', error);
//     }
//   };

//   const handleMove = (document) => {
//     setDocumentToMove(document);
//     setShowMoveModal(true);
//   };

//   const moveDocument = async (newSubjectId) => {
//     try {
//       const response = await fetch(`http://localhost:8000/documents/${documentToMove.id}/assign-subject?subject_id=${newSubjectId}&confidence=1.0&auto_assigned=false`, {
//         method: 'POST',
//       });

//       if (response.ok) {
//         // Remove document from current list
//         setDocuments(documents.filter(doc => doc.id !== documentToMove.id));
//         setShowMoveModal(false);
//         setDocumentToMove(null);
//       }
//     } catch (error) {
//       console.error('Failed to move document:', error);
//     }
//   };

//   const handleOpen = (document) => {
//     window.open(`http://localhost:8000/documents/${document.id}/view`, '_blank');
//   };

//   const handleSummary = async (document) => {
//     try {
//       const response = await fetch(`http://localhost:8000/documents/${document.id}/summary`);
//       if (response.ok) {
//         const summaryData = await response.json();
//         setSelectedDocument({
//           ...document,
//           summary: summaryData.summary_text
//         });
//         setShowSummary(true);
//       }
//     } catch (error) {
//       console.error('Failed to fetch summary:', error);
//       alert('Summary not available yet');
//     }
//   };

//   const handleDelete = async (document) => {
//     if (window.confirm(`Are you sure you want to delete "${document.filename}"?`)) {
//       try {
//         const response = await fetch(`http://localhost:8000/documents/${document.id}`, {
//           method: 'DELETE',
//         });

//         if (response.ok) {
//           setDocuments(documents.filter(doc => doc.id !== document.id));
//         }
//       } catch (error) {
//         console.error('Failed to delete document:', error);
//       }
//     }
//   };

//   if (loading) {
//     return (
//       <div style={{ padding: '40px', textAlign: 'center' }}>
//         <div>Loading documents...</div>
//       </div>
//     );
//   }

//   return (
//     <div>
//       {/* Header */}
//       <div className="header">
//         <div className="container">
//           <div className="header-content">
//             <button 
//               onClick={() => navigate('/')}
//               style={{ 
//                 background: 'none', 
//                 border: 'none', 
//                 fontSize: '24px', 
//                 cursor: 'pointer' 
//               }}
//             >
//               🏠
//             </button>
//             <div className="logo-text">CLUTTERFLOW</div>
//             <div></div>
//           </div>
//         </div>
//       </div>

//       {/* Main Content */}
//       <div className="main-content">
//         <div className="container">
//           {/* Subject Header */}
//           <div style={{ 
//             textAlign: 'center', 
//             marginBottom: '30px' 
//           }}>
//             <div className="card-base" style={{ 
//               padding: '20px', 
//               display: 'inline-block',
//               minWidth: '200px'
//             }}>
//               <h2 style={{ 
//                 margin: '0', 
//                 fontSize: '24px', 
//                 color: '#374151' 
//               }}>
//                 {subject?.subject_name || 'Subject'}
//               </h2>
//             </div>
            
//             <div style={{ 
//               position: 'absolute', 
//               right: '100px', 
//               top: '50%', 
//               transform: 'translateY(-50%)',
//               color: '#6B7280',
//               fontSize: '14px',
//               display: 'flex',
//               alignItems: 'center',
//               gap: '8px'
//             }}>
//               <div>chose where to move the subject</div>
//               <div>→</div>
//             </div>
//           </div>

//           {/* Documents List */}
//           <div className="card-base" style={{ padding: '0', overflow: 'hidden' }}>
//             {documents.length === 0 ? (
//               <div style={{ 
//                 padding: '60px', 
//                 textAlign: 'center', 
//                 color: '#6B7280' 
//               }}>
//                 <div style={{ fontSize: '48px', marginBottom: '16px' }}>📄</div>
//                 <div>No documents in this subject yet</div>
//               </div>
//             ) : (
//               documents.map((document, index) => (
//                 <div 
//                   key={document.id}
//                   style={{
//                     display: 'flex',
//                     alignItems: 'center',
//                     padding: '16px 24px',
//                     borderBottom: index < documents.length - 1 ? '1px solid #E5E7EB' : 'none'
//                   }}
//                 >
//                   {/* Document Name */}
//                   <div style={{ 
//                     flex: 1, 
//                     fontSize: '16px', 
//                     color: '#374151' 
//                   }}>
//                     {document.filename || 'Document'}
//                   </div>

//                   {/* Action Buttons */}
//                   <div style={{ 
//                     display: 'flex', 
//                     gap: '8px' 
//                   }}>
//                     <button
//                       onClick={() => handleMove(document)}
//                       style={{
//                         background: '#374151',
//                         color: 'white',
//                         border: 'none',
//                         padding: '8px 16px',
//                         borderRadius: '6px',
//                         fontSize: '14px',
//                         cursor: 'pointer'
//                       }}
//                     >
//                       move
//                     </button>
//                     <button
//                       onClick={() => handleOpen(document)}
//                       style={{
//                         background: '#374151',
//                         color: 'white',
//                         border: 'none',
//                         padding: '8px 16px',
//                         borderRadius: '6px',
//                         fontSize: '14px',
//                         cursor: 'pointer'
//                       }}
//                     >
//                       open
//                     </button>
//                     <button
//                       onClick={() => handleSummary(document)}
//                       style={{
//                         background: '#374151',
//                         color: 'white',
//                         border: 'none',
//                         padding: '8px 16px',
//                         borderRadius: '6px',
//                         fontSize: '14px',
//                         cursor: 'pointer'
//                       }}
//                     >
//                       Summary
//                     </button>
//                     <button
//                       onClick={() => handleDelete(document)}
//                       style={{
//                         background: '#374151',
//                         color: 'white',
//                         border: 'none',
//                         padding: '8px 12px',
//                         borderRadius: '6px',
//                         fontSize: '14px',
//                         cursor: 'pointer'
//                       }}
//                     >
//                       🗑️
//                     </button>
//                   </div>
//                 </div>
//               ))
//             )}
//           </div>
//         </div>
//       </div>

//       {/* Move Document Modal */}
//       {showMoveModal && (
//         <div style={{ 
//           position: 'fixed', 
//           top: 0, 
//           left: 0, 
//           right: 0, 
//           bottom: 0, 
//           background: 'rgba(0,0,0,0.5)', 
//           display: 'flex', 
//           alignItems: 'center', 
//           justifyContent: 'center',
//           zIndex: 1000 
//         }}>
//           <div className="card-base" style={{ 
//             padding: '30px', 
//             maxWidth: '500px', 
//             width: '90%' 
//           }}>
//             <h3 style={{ marginBottom: '20px' }}>
//               Move "{documentToMove?.filename}" to:
//             </h3>
//             <div style={{ 
//               display: 'grid', 
//               gridTemplateColumns: 'repeat(2, 1fr)', 
//               gap: '12px',
//               marginBottom: '20px' 
//             }}>
//               {subjects.filter(s => s.id !== subjectId).map((subj) => (
//                 <button
//                   key={subj.id}
//                   onClick={() => moveDocument(subj.id)}
//                   style={{
//                     background: '#0284c7',
//                     color: 'white',
//                     border: 'none',
//                     padding: '12px',
//                     borderRadius: '8px',
//                     cursor: 'pointer'
//                   }}
//                 >
//                   {subj.subject_name}
//                 </button>
//               ))}
//             </div>
//             <button
//               onClick={() => setShowMoveModal(false)}
//               style={{
//                 background: '#6B7280',
//                 color: 'white',
//                 border: 'none',
//                 padding: '8px 16px',
//                 borderRadius: '6px',
//                 width: '100%'
//               }}
//             >
//               Cancel
//             </button>
//           </div>
//         </div>
//       )}

//       {/* Summary Modal */}
//       {showSummary && selectedDocument && (
//         <div style={{ 
//           position: 'fixed', 
//           top: 0, 
//           left: 0, 
//           right: 0, 
//           bottom: 0, 
//           background: 'rgba(0,0,0,0.5)', 
//           display: 'flex', 
//           alignItems: 'center', 
//           justifyContent: 'center',
//           zIndex: 1000 
//         }}>
//           <div className="card-base" style={{ 
//             padding: '30px', 
//             maxWidth: '600px', 
//             width: '90%',
//             maxHeight: '80vh',
//             overflow: 'auto'
//           }}>
//             <h3 style={{ marginBottom: '20px' }}>
//               Summary: {selectedDocument.filename}
//             </h3>
//             <div style={{ 
//               marginBottom: '20px',
//               lineHeight: '1.6',
//               color: '#374151'
//             }}>
//               {selectedDocument.summary || 'Summary not available'}
//             </div>
//             <button
//               onClick={() => setShowSummary(false)}
//               className="btn-primary"
//               style={{ width: '100%' }}
//             >
//               Close
//             </button>
//           </div>
//         </div>
//       )}
//     </div>
//   );
// };

// export default SubjectView;
// src/components/SubjectView.jsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

// Define the API URL from environment variables
const API_URL = process.env.REACT_APP_BACKEND_API_URL;

const SubjectView = () => {
  const { subjectId } = useParams();
  const navigate = useNavigate();
  
  const [subject, setSubject] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [showSummary, setShowSummary] = useState(false);
  const [showMoveModal, setShowMoveModal] = useState(false);
  const [documentToMove, setDocumentToMove] = useState(null);

  useEffect(() => {
    if (subjectId) {
      fetchSubjectData();
      fetchAllSubjects();
    }
  }, [subjectId]);

  const fetchSubjectData = async () => {
    try {
      // Get subject info
      const subjectResponse = await fetch(`${API_URL}/subjects/${subjectId}`);
      if (subjectResponse.ok) {
        const subjectData = await subjectResponse.json();
        setSubject(subjectData);
      }

      // Get documents in this subject
      const documentsResponse = await fetch(`${API_URL}/subjects/${subjectId}/documents`);
      if (documentsResponse.ok) {
        const documentsData = await documentsResponse.json();
        setDocuments(documentsData.documents || []);
      }

      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch subject data:', error);
      setLoading(false);
    }
  };

  const fetchAllSubjects = async () => {
    try {
      const response = await fetch(`${API_URL}/subjects`);
      if (response.ok) {
        const data = await response.json();
        setSubjects(data);
      }
    } catch (error) {
      console.error('Failed to fetch subjects:', error);
    }
  };

  const handleMove = (document) => {
    setDocumentToMove(document);
    setShowMoveModal(true);
  };

  const moveDocument = async (newSubjectId) => {
    try {
      const response = await fetch(`${API_URL}/documents/${documentToMove.id}/assign-subject?subject_id=${newSubjectId}&confidence=1.0&auto_assigned=false`, {
        method: 'POST',
      });

      if (response.ok) {
        // Remove document from current list
        setDocuments(documents.filter(doc => doc.id !== documentToMove.id));
        setShowMoveModal(false);
        setDocumentToMove(null);
      }
    } catch (error) {
      console.error('Failed to move document:', error);
    }
  };

  const handleOpen = (document) => {
    window.open(`${API_URL}/documents/${document.id}/view`, '_blank');
  };

  const handleSummary = async (document) => {
    try {
      const response = await fetch(`${API_URL}/documents/${document.id}/summary`);
      if (response.ok) {
        const summaryData = await response.json();
        setSelectedDocument({
          ...document,
          summary: summaryData.summary_text
        });
        setShowSummary(true);
      }
    } catch (error) {
      console.error('Failed to fetch summary:', error);
      alert('Summary not available yet');
    }
  };

  const handleDelete = async (document) => {
    if (window.confirm(`Are you sure you want to delete "${document.filename}"?`)) {
      try {
        const response = await fetch(`${API_URL}/documents/${document.id}`, {
          method: 'DELETE',
        });

        if (response.ok) {
          setDocuments(documents.filter(doc => doc.id !== document.id));
        }
      } catch (error) {
        console.error('Failed to delete document:', error);
      }
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '40px', textAlign: 'center' }}>
        <div>Loading documents...</div>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="header">
        <div className="container">
          <div className="header-content">
            <button 
              onClick={() => navigate('/')}
              style={{ 
                background: 'none', 
                border: 'none', 
                fontSize: '24px', 
                cursor: 'pointer' 
              }}
            >
              🏠
            </button>
            <div className="logo-text">CLUTTERFLOW</div>
            <div></div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        <div className="container">
          {/* Subject Header */}
          <div style={{ 
            textAlign: 'center', 
            marginBottom: '30px' 
          }}>
            <div className="card-base" style={{ 
              padding: '20px', 
              display: 'inline-block',
              minWidth: '200px'
            }}>
              <h2 style={{ 
                margin: '0', 
                fontSize: '24px', 
                color: '#374151' 
              }}>
                {subject?.subject_name || 'Subject'}
              </h2>
            </div>
            
            <div style={{ 
              position: 'absolute', 
              right: '100px', 
              top: '50%', 
              transform: 'translateY(-50%)',
              color: '#6B7280',
              fontSize: '14px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <div>chose where to move the subject</div>
              <div>→</div>
            </div>
          </div>

          {/* Documents List */}
          <div className="card-base" style={{ padding: '0', overflow: 'hidden' }}>
            {documents.length === 0 ? (
              <div style={{ 
                padding: '60px', 
                textAlign: 'center', 
                color: '#6B7280' 
              }}>
                <div style={{ fontSize: '48px', marginBottom: '16px' }}>📄</div>
                <div>No documents in this subject yet</div>
              </div>
            ) : (
              documents.map((document, index) => (
                <div 
                  key={document.id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    padding: '16px 24px',
                    borderBottom: index < documents.length - 1 ? '1px solid #E5E7EB' : 'none'
                  }}
                >
                  {/* Document Name */}
                  <div style={{ 
                    flex: 1, 
                    fontSize: '16px', 
                    color: '#374151' 
                  }}>
                    {document.filename || 'Document'}
                  </div>

                  {/* Action Buttons */}
                  <div style={{ 
                    display: 'flex', 
                    gap: '8px' 
                  }}>
                    <button
                      onClick={() => handleMove(document)}
                      style={{
                        background: '#374151',
                        color: 'white',
                        border: 'none',
                        padding: '8px 16px',
                        borderRadius: '6px',
                        fontSize: '14px',
                        cursor: 'pointer'
                      }}
                    >
                      move
                    </button>
                    <button
                      onClick={() => handleOpen(document)}
                      style={{
                        background: '#374151',
                        color: 'white',
                        border: 'none',
                        padding: '8px 16px',
                        borderRadius: '6px',
                        fontSize: '14px',
                        cursor: 'pointer'
                      }}
                    >
                      open
                    </button>
                    <button
                      onClick={() => handleSummary(document)}
                      style={{
                        background: '#374151',
                        color: 'white',
                        border: 'none',
                        padding: '8px 16px',
                        borderRadius: '6px',
                        fontSize: '14px',
                        cursor: 'pointer'
                      }}
                    >
                      Summary
                    </button>
                    <button
                      onClick={() => handleDelete(document)}
                      style={{
                        background: '#374151',
                        color: 'white',
                        border: 'none',
                        padding: '8px 12px',
                        borderRadius: '6px',
                        fontSize: '14px',
                        cursor: 'pointer'
                      }}
                    >
                      🗑️
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Move Document Modal */}
      {showMoveModal && (
        <div style={{ 
          position: 'fixed', 
          top: 0, 
          left: 0, 
          right: 0, 
          bottom: 0, 
          background: 'rgba(0,0,0,0.5)', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          zIndex: 1000 
        }}>
          <div className="card-base" style={{ 
            padding: '30px', 
            maxWidth: '500px', 
            width: '90%' 
          }}>
            <h3 style={{ marginBottom: '20px' }}>
              Move "{documentToMove?.filename}" to:
            </h3>
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(2, 1fr)', 
              gap: '12px',
              marginBottom: '20px' 
            }}>
              {subjects.filter(s => s.id !== subjectId).map((subj) => (
                <button
                  key={subj.id}
                  onClick={() => moveDocument(subj.id)}
                  style={{
                    background: '#0284c7',
                    color: 'white',
                    border: 'none',
                    padding: '12px',
                    borderRadius: '8px',
                    cursor: 'pointer'
                  }}
                >
                  {subj.subject_name}
                </button>
              ))}
            </div>
            <button
              onClick={() => setShowMoveModal(false)}
              style={{
                background: '#6B7280',
                color: 'white',
                border: 'none',
                padding: '8px 16px',
                borderRadius: '6px',
                width: '100%'
              }}
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Summary Modal */}
      {showSummary && selectedDocument && (
        <div style={{ 
          position: 'fixed', 
          top: 0, 
          left: 0, 
          right: 0, 
          bottom: 0, 
          background: 'rgba(0,0,0,0.5)', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          zIndex: 1000 
        }}>
          <div className="card-base" style={{ 
            padding: '30px', 
            maxWidth: '600px', 
            width: '90%',
            maxHeight: '80vh',
            overflow: 'auto'
          }}>
            <h3 style={{ marginBottom: '20px' }}>
              Summary: {selectedDocument.filename}
            </h3>
            <div style={{ 
              marginBottom: '20px',
              lineHeight: '1.6',
              color: '#374151'
            }}>
              {selectedDocument.summary || 'Summary not available'}
            </div>
            <button
              onClick={() => setShowSummary(false)}
              className="btn-primary"
              style={{ width: '100%' }}
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default SubjectView;