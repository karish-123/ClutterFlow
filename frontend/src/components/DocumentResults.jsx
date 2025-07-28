// // // src/components/DocumentResults.jsx
// // import React, { useState, useEffect } from 'react';

// // const DocumentResults = ({ document, onClose, onSubjectAssigned }) => {
// //   const [summary, setSummary] = useState(null);
// //   const [classification, setClassification] = useState(null);
// //   const [subjects, setSubjects] = useState([]);
// //   const [selectedSubject, setSelectedSubject] = useState(null);
// //   const [loading, setLoading] = useState(true);
// //   const [editing, setEditing] = useState(false);

// //   useEffect(() => {
// //     if (document?.id) {
// //       fetchDocumentData();
// //       fetchSubjects();
// //     }
// //   }, [document]);

// //   const fetchDocumentData = async () => {
// //     try {
// //       // Fetch summary
// //       const summaryResponse = await fetch(`http://localhost:8000/documents/${document.id}/summary`);
// //       if (summaryResponse.ok) {
// //         const summaryData = await summaryResponse.json();
// //         setSummary(summaryData);
// //       }

// //       // Fetch classification
// //       const classificationResponse = await fetch(`http://localhost:8000/documents/${document.id}/classification`);
// //       if (classificationResponse.ok) {
// //         const classificationData = await classificationResponse.json();
// //         setClassification(classificationData);
        
// //         // If document is already assigned to a subject, find that subject
// //         if (classificationData.subject_id) {
// //           const subjectResponse = await fetch(`http://localhost:8000/subjects/${classificationData.subject_id}`);
// //           if (subjectResponse.ok) {
// //             const subjectData = await subjectResponse.json();
// //             setSelectedSubject(subjectData);
// //           }
// //         }
// //       }

// //       setLoading(false);
// //     } catch (error) {
// //       console.error('Failed to fetch document data:', error);
// //       setLoading(false);
// //     }
// //   };

// //   const fetchSubjects = async () => {
// //     try {
// //       const response = await fetch('http://localhost:8000/subjects');
// //       if (response.ok) {
// //         const data = await response.json();
// //         setSubjects(data);
// //       }
// //     } catch (error) {
// //       console.error('Failed to fetch subjects:', error);
// //     }
// //   };

// //   const assignToSubject = async (subjectId) => {
// //     try {
// //       const response = await fetch(`http://localhost:8000/documents/${document.id}/assign-subject?subject_id=${subjectId}&confidence=1.0&auto_assigned=false`, {
// //         method: 'POST',
// //       });

// //       if (response.ok) {
// //         const subject = subjects.find(s => s.id === subjectId);
// //         setSelectedSubject(subject);
// //         setEditing(false);
// //         if (onSubjectAssigned) {
// //           onSubjectAssigned(subject);
// //         }
// //       }
// //     } catch (error) {
// //       console.error('Failed to assign subject:', error);
// //     }
// //   };

// //   // Color scheme for subject cards
// //   const subjectColors = [
// //     '#8B7355', // brown
// //     '#9CA3AF', // light gray
// //     '#D4C4A0', // light beige
// //     '#6B7280', // darker gray
// //     '#A78BFA', // purple
// //     '#F59E0B', // amber
// //   ];

// //   if (loading) {
// //     return (
// //       <div style={{ 
// //         position: 'fixed', 
// //         top: 0, 
// //         left: 0, 
// //         right: 0, 
// //         bottom: 0, 
// //         background: 'rgba(0,0,0,0.5)', 
// //         display: 'flex', 
// //         alignItems: 'center', 
// //         justifyContent: 'center',
// //         zIndex: 1000 
// //       }}>
// //         <div className="card-base" style={{ padding: '40px', textAlign: 'center' }}>
// //           <div style={{ fontSize: '24px', marginBottom: '16px' }}>🔄</div>
// //           <div>Loading document analysis...</div>
// //         </div>
// //       </div>
// //     );
// //   }

// //   return (
// //     <div style={{ 
// //       position: 'fixed', 
// //       top: 0, 
// //       left: 0, 
// //       right: 0, 
// //       bottom: 0, 
// //       background: 'rgba(0,0,0,0.5)', 
// //       display: 'flex', 
// //       alignItems: 'center', 
// //       justifyContent: 'center',
// //       zIndex: 1000,
// //       padding: '20px' 
// //     }}>
// //       <div style={{ 
// //         background: '#8B8680', 
// //         borderRadius: '16px', 
// //         padding: '40px', 
// //         maxWidth: '1000px', 
// //         width: '100%',
// //         maxHeight: '90vh',
// //         overflow: 'auto'
// //       }}>
// //         {/* Header */}
// //         <div style={{ 
// //           textAlign: 'center', 
// //           fontSize: '32px', 
// //           fontWeight: 'bold', 
// //           color: 'white', 
// //           marginBottom: '30px',
// //           fontStyle: 'italic'
// //         }}>
// //           CLUTTERFLOW
// //         </div>

// //         {/* Summary and Classification Row */}
// //         <div className="grid grid-cols-1 lg:grid-cols-2" style={{ marginBottom: '30px', gap: '20px' }}>
// //           {/* Summary */}
// //           <div className="card-base" style={{ padding: '24px' }}>
// //             <h3 style={{ 
// //               fontSize: '24px', 
// //               color: '#8B7355', 
// //               marginBottom: '16px',
// //               fontStyle: 'italic'
// //             }}>
// //               summary
// //             </h3>
// //             <div style={{ 
// //               fontSize: '14px', 
// //               lineHeight: '1.6', 
// //               color: '#374151' 
// //             }}>
// //               {summary?.summary_text || 'Summary is being generated...'}
// //             </div>
// //           </div>

// //           {/* Classification and Subject */}
// //           <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
// //             {/* Classification Tags */}
// //             <div className="card-base" style={{ padding: '16px' }}>
// //               <div style={{ fontSize: '14px', color: '#6B7280', marginBottom: '8px' }}>
// //                 classification tags
// //               </div>
// //               <div style={{ fontSize: '16px', color: '#374151' }}>
// //                 {classification?.tags?.join(' , ') || classification?.category || 'Processing...'}
// //               </div>
// //             </div>

// //             {/* Suggested Subject */}
// //             <div className="card-base" style={{ padding: '16px', position: 'relative' }}>
// //               <div style={{ fontSize: '14px', color: '#6B7280', marginBottom: '8px' }}>
// //                 suggested subject
// //               </div>
// //               <div style={{ 
// //                 display: 'flex', 
// //                 alignItems: 'center', 
// //                 justifyContent: 'space-between' 
// //               }}>
// //                 <div style={{ fontSize: '16px', color: '#374151' }}>
// //                   {selectedSubject?.subject_name || 'Machine Learning'}
// //                 </div>
// //                 <button
// //                   onClick={() => setEditing(!editing)}
// //                   style={{
// //                     background: '#6B7280',
// //                     color: 'white',
// //                     border: 'none',
// //                     padding: '4px 12px',
// //                     borderRadius: '12px',
// //                     fontSize: '12px',
// //                     cursor: 'pointer'
// //                   }}
// //                 >
// //                   EDIT
// //                 </button>
// //               </div>
              
// //               {/* Arrow pointing to subjects */}
// //               {editing && (
// //                 <div style={{
// //                   position: 'absolute',
// //                   right: '-60px',
// //                   top: '50%',
// //                   transform: 'translateY(-50%)',
// //                   color: 'white',
// //                   fontSize: '14px',
// //                   display: 'flex',
// //                   alignItems: 'center',
// //                   gap: '8px'
// //                 }}>
// //                   <div style={{ 
// //                     width: '40px', 
// //                     height: '2px', 
// //                     background: 'white' 
// //                   }}></div>
// //                   <div>→</div>
// //                   <div>can change the subject</div>
// //                 </div>
// //               )}
// //             </div>
// //           </div>
// //         </div>

// //         {/* Subject Selection */}
// //         <div className="grid grid-cols-3" style={{ marginBottom: '30px', gap: '16px' }}>
// //           {subjects.map((subject, index) => (
// //             <div
// //               key={subject.id}
// //               className="subject-card"
// //               style={{ 
// //                 background: subjectColors[index % subjectColors.length],
// //                 opacity: editing ? 1 : 0.8,
// //                 cursor: editing ? 'pointer' : 'default',
// //                 border: selectedSubject?.id === subject.id ? '3px solid white' : 'none',
// //                 transform: editing ? 'scale(1)' : 'scale(0.95)',
// //                 transition: 'all 0.3s ease'
// //               }}
// //               onClick={() => editing && assignToSubject(subject.id)}
// //             >
// //               {subject.subject_name}
// //             </div>
// //           ))}
// //         </div>

// //         {/* Action Buttons */}
// //         <div style={{ 
// //           display: 'flex', 
// //           justifyContent: 'center', 
// //           gap: '16px' 
// //         }}>
// //           <button
// //             onClick={onClose}
// //             className="btn-primary"
// //             style={{ minWidth: '120px' }}
// //           >
// //             Done
// //           </button>
// //           {document && (
// //             <button
// //               onClick={() => window.open(`http://localhost:8000/documents/${document.id}/view`, '_blank')}
// //               style={{
// //                 background: '#6B7280',
// //                 color: 'white',
// //                 border: 'none',
// //                 padding: '12px 24px',
// //                 borderRadius: '8px',
// //                 cursor: 'pointer',
// //                 minWidth: '120px'
// //               }}
// //             >
// //               View Document
// //             </button>
// //           )}
// //         </div>
// //       </div>
// //     </div>
// //   );
// // };

// // export default DocumentResults;


// // Update your DocumentResults component like this:
// // import React, { useState } from 'react';
// // import useDocumentPolling from './useDocumentPolling'; // Import the hook

// // const DocumentResults = ({ document, onClose, onSubjectAssigned }) => {
// //   const [selectedSubject, setSelectedSubject] = useState(null);
// //   const [subjects, setSubjects] = useState([]);
  
// //   // Use the polling hook
// //   const { 
// //     status, 
// //     summary, 
// //     classification, 
// //     error, 
// //     isProcessing, 
// //     isComplete 
// //   } = useDocumentPolling(document?.id, 'processing');

// //   // Fetch subjects when component mounts
// //   React.useEffect(() => {
// //     fetchSubjects();
// //   }, []);
  

// //   const fetchSubjects = async () => {
// //     try {
// //       const response = await fetch('http://localhost:8000/subjects');
// //       if (response.ok) {
// //         const data = await response.json();
// //         setSubjects(data);
// //       }
// //     } catch (error) {
// //       console.error('Failed to fetch subjects:', error);
// //     }
// //   };

// //   const assignToSubject = async (subject) => {
// //     if (!document?.id) return;
    
// //     try {
// //       const response = await fetch(`http://localhost:8000/documents/${document.id}/assign-subject?subject_id=${subject.id}&confidence=1.0&auto_assigned=false`, {
// //         method: 'POST',
// //       });

// //       if (response.ok) {
// //         onSubjectAssigned(subject);
// //         onClose();
// //       }
// //     } catch (error) {
// //       console.error('Failed to assign subject:', error);
// //     }
// //   };

// //   return (
// //     <div style={{
// //       position: 'fixed',
// //       top: 0,
// //       left: 0,
// //       right: 0,
// //       bottom: 0,
// //       background: 'rgba(0,0,0,0.5)',
// //       display: 'flex',
// //       alignItems: 'center',
// //       justifyContent: 'center',
// //       zIndex: 1000
// //     }}>
// //       <div className="card-base" style={{
// //         padding: '30px',
// //         maxWidth: '600px',
// //         width: '90%',
// //         maxHeight: '80vh',
// //         overflow: 'auto'
// //       }}>
// //         <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
// //           <h3 style={{ margin: 0 }}>Document Processing Results</h3>
// //           <button onClick={onClose} style={{ 
// //             background: 'none', 
// //             border: 'none', 
// //             fontSize: '24px', 
// //             cursor: 'pointer' 
// //           }}>×</button>
// //         </div>

// //         {/* Document Info */}
// //         <div style={{ marginBottom: '20px' }}>
// //           <h4>📄 {document?.filename || 'Uploaded Document'}</h4>
// //         </div>

// //         {/* Processing Status */}
// //         <div style={{ marginBottom: '20px' }}>
// //           <h4>Processing Status:</h4>
// //           <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
// //             <span>{isProcessing ? '🔄' : isComplete ? '✅' : '❌'}</span>
// //             <span>{
// //               isProcessing ? 'Processing...' : 
// //               isComplete ? 'Complete!' : 
// //               error ? `Error: ${error}` : 'Unknown status'
// //             }</span>
// //           </div>
// //         </div>

// //         {/* Summary Section */}
// //         <div style={{ marginBottom: '20px' }}>
// //           <h4>📝 Summary:</h4>
// //           <div style={{ 
// //             background: '#f8f9fa', 
// //             padding: '15px', 
// //             borderRadius: '8px',
// //             minHeight: '60px'
// //           }}>
// //             {isProcessing ? (
// //               <div style={{ color: '#6b7280' }}>🔄 Generating summary...</div>
// //             ) : summary?.summary_text ? (
// //               <div>{summary.summary_text}</div>
// //             ) : (
// //               <div style={{ color: '#ef4444' }}>❌ Summary not available</div>
// //             )}
// //           </div>
// //         </div>

// //         {/* Classification Section */}
// //         <div style={{ marginBottom: '20px' }}>
// //           <h4>🏷️ Classification:</h4>
// //           <div style={{ 
// //             background: '#f8f9fa', 
// //             padding: '15px', 
// //             borderRadius: '8px',
// //             minHeight: '60px'
// //           }}>
// //             {isProcessing ? (
// //               <div style={{ color: '#6b7280' }}>🔄 Classifying document...</div>
// //             ) : classification ? (
// //               <div>
// //                 <div><strong>Subject:</strong> {classification.subject_name || 'Unknown'}</div>
// //                 <div><strong>Confidence:</strong> {(classification.confidence * 100).toFixed(1)}%</div>
// //                 {classification.keywords && (
// //                   <div><strong>Keywords:</strong> {classification.keywords.join(', ')}</div>
// //                 )}
// //               </div>
// //             ) : (
// //               <div style={{ color: '#ef4444' }}>❌ Classification not available</div>
// //             )}
// //           </div>
// //         </div>

// //         {/* Subject Assignment */}
// //         {isComplete && (
// //           <div style={{ marginBottom: '20px' }}>
// //             <h4>📁 Assign to Subject:</h4>
// //             <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '10px' }}>
// //               {subjects.map(subject => (
// //                 <button
// //                   key={subject.id}
// //                   onClick={() => assignToSubject(subject)}
// //                   style={{
// //                     padding: '10px',
// //                     border: '1px solid #d1d5db',
// //                     borderRadius: '6px',
// //                     background: classification?.subject_id === subject.id ? '#3b82f6' : 'white',
// //                     color: classification?.subject_id === subject.id ? 'white' : '#374151',
// //                     cursor: 'pointer'
// //                   }}
// //                 >
// //                   {subject.subject_name}
// //                 </button>
// //               ))}
// //             </div>
// //           </div>
// //         )}

// //         {/* Action Buttons */}
// //         <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
// //           {isProcessing && (
// //             <button
// //               onClick={() => window.location.reload()}
// //               style={{
// //                 padding: '10px 20px',
// //                 background: '#6b7280',
// //                 color: 'white',
// //                 border: 'none',
// //                 borderRadius: '6px',
// //                 cursor: 'pointer'
// //               }}
// //             >
// //               Refresh Page
// //             </button>
// //           )}
// //           <button
// //             onClick={onClose}
// //             style={{
// //               padding: '10px 20px',
// //               background: '#374151',
// //               color: 'white',
// //               border: 'none',
// //               borderRadius: '6px',
// //               cursor: 'pointer'
// //             }}
// //           >
// //             Close
// //           </button>
// //         </div>
// //       </div>
// //     </div>
// //   );
  
// // };




// import React, { useState } from 'react';
// import useDocumentPolling from './useDocumentPolling';

// // Define the API URL from environment variables
// const API_URL = process.env.REACT_APP_BACKEND_API_URL;

// const DocumentResults = ({ document, onClose, onSubjectAssigned }) => {
//   const [selectedSubject, setSelectedSubject] = useState(null);
//   const [subjects, setSubjects] = useState([]);
//   const [assignedSubject, setAssignedSubject] = useState(null); // NEW: Track assigned subject
  
//   // Use the polling hook
//   const { 
//     status, 
//     summary, 
//     classification, 
//     error, 
//     isProcessing, 
//     isComplete 
//   } = useDocumentPolling(document?.id, 'processing');

//   // Fetch subjects when component mounts
//   React.useEffect(() => {
//     fetchSubjects();
//   }, []);

//   // NEW: Fetch assigned subject when classification is available
//   React.useEffect(() => {
//     if (classification?.subject_id) {
//       fetchAssignedSubject(classification.subject_id);
//     }
//   }, [classification]);

//   const fetchSubjects = async () => {
//     try {
//       const response = await fetch(`${API_URL}/subjects`);
//       if (response.ok) {
//         const data = await response.json();
//         setSubjects(data);
//       }
//     } catch (error) {
//       console.error('Failed to fetch subjects:', error);
//     }
//   };

//   // NEW: Function to fetch the assigned subject details
//   const fetchAssignedSubject = async (subjectId) => {
//     try {
//       const response = await fetch(`${API_URL}/subjects/${subjectId}`);
//       if (response.ok) {
//         const subjectData = await response.json();
//         setAssignedSubject(subjectData);
//         console.log('✅ Fetched assigned subject:', subjectData.subject_name);
//       }
//     } catch (error) {
//       console.error('Failed to fetch assigned subject:', error);
//     }
//   };

//   const assignToSubject = async (subject) => {
//     if (!document?.id) return;
    
//     try {
//       const response = await fetch(`${API_URL}/documents/${document.id}/assign-subject?subject_id=${subject.id}&confidence=1.0&auto_assigned=false`, {
//         method: 'POST',
//       });

//       if (response.ok) {
//         setAssignedSubject(subject); // Update local state immediately
//         onSubjectAssigned(subject);
//         onClose();
//       }
//     } catch (error) {
//       console.error('Failed to assign subject:', error);
//     }
//   };

//   // NEW: Function to get display subject and confidence
//   const getDisplayClassification = () => {
//     if (assignedSubject) {
//       // Document is assigned to a subject
//       return {
//         subject: assignedSubject.subject_name,
//         confidence: classification?.subject_confidence || classification?.confidence || 0,
//         source: 'assigned'
//       };
//     } else if (classification?.primary_topic && classification.primary_topic !== 'manual_assignment') {
//       // AI classification available
//       return {
//         subject: classification.primary_topic,
//         confidence: classification.confidence || 0,
//         source: 'ai'
//       };
//     } else {
//       // No classification
//       return {
//         subject: 'Unknown',
//         confidence: 0,
//         source: 'none'
//       };
//     }
//   };

//   const displayClassification = getDisplayClassification();

//   return (
//     <div style={{
//       position: 'fixed',
//       top: 0,
//       left: 0,
//       right: 0,
//       bottom: 0,
//       background: 'rgba(0,0,0,0.5)',
//       display: 'flex',
//       alignItems: 'center',
//       justifyContent: 'center',
//       zIndex: 1000
//     }}>
//       <div className="card-base" style={{
//         padding: '30px',
//         maxWidth: '600px',
//         width: '90%',
//         maxHeight: '80vh',
//         overflow: 'auto'
//       }}>
//         <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
//           <h3 style={{ margin: 0 }}>Document Processing Results</h3>
//           <button onClick={onClose} style={{ 
//             background: 'none', 
//             border: 'none', 
//             fontSize: '24px', 
//             cursor: 'pointer' 
//           }}>×</button>
//         </div>

//         {/* Document Info */}
//         <div style={{ marginBottom: '20px' }}>
//           <h4>📄 {document?.filename || 'Uploaded Document'}</h4>
//         </div>

//         {/* Processing Status */}
//         <div style={{ marginBottom: '20px' }}>
//           <h4>Processing Status:</h4>
//           <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
//             <span>{isProcessing ? '🔄' : isComplete ? '✅' : '❌'}</span>
//             <span>{
//               isProcessing ? 'Processing...' : 
//               isComplete ? 'Complete!' : 
//               error ? `Error: ${error}` : 'Unknown status'
//             }</span>
//           </div>
//         </div>

//         {/* Summary Section */}
//         <div style={{ marginBottom: '20px' }}>
//           <h4>📝 Summary:</h4>
//           <div style={{ 
//             background: '#f8f9fa', 
//             padding: '15px', 
//             borderRadius: '8px',
//             minHeight: '60px'
//           }}>
//             {isProcessing ? (
//               <div style={{ color: '#6b7280' }}>🔄 Generating summary...</div>
//             ) : summary?.summary_text ? (
//               <div>{summary.summary_text}</div>
//             ) : (
//               <div style={{ color: '#ef4444' }}>❌ Summary not available</div>
//             )}
//           </div>
//         </div>

//         {/* Classification Section - FIXED */}
//         <div style={{ marginBottom: '20px' }}>
//           <h4>🏷️ Classification:</h4>
//           <div style={{ 
//             background: '#f8f9fa', 
//             padding: '15px', 
//             borderRadius: '8px',
//             minHeight: '60px'
//           }}>
//             {isProcessing ? (
//               <div style={{ color: '#6b7280' }}>🔄 Classifying document...</div>
//             ) : classification ? (
//               <div>
//                 <div><strong>Subject:</strong> {displayClassification.subject}</div>
//                 <div><strong>Confidence:</strong> {(displayClassification.confidence * 100).toFixed(1)}%</div>
//                 {classification.tags && classification.tags.length > 0 && (
//                   <div><strong>Tags:</strong> {classification.tags.join(', ')}</div>
//                 )}
//                 {displayClassification.source === 'assigned' && (
//                   <div style={{ fontSize: '12px', color: '#10b981', marginTop: '5px' }}>
//                     ✅ Assigned to subject
//                   </div>
//                 )}
//               </div>
//             ) : (
//               <div style={{ color: '#ef4444' }}>❌ Classification not available</div>
//             )}
//           </div>
//         </div>

//         {/* Subject Assignment */}
//         {isComplete && (
//           <div style={{ marginBottom: '20px' }}>
//             <h4>📁 Assign to Subject:</h4>
//             <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '10px' }}>
//               {subjects.map(subject => (
//                 <button
//                   key={subject.id}
//                   onClick={() => assignToSubject(subject)}
//                   style={{
//                     padding: '10px',
//                     border: '1px solid #d1d5db',
//                     borderRadius: '6px',
//                     background: (classification?.subject_id === subject.id || assignedSubject?.id === subject.id) ? '#3b82f6' : 'white',
//                     color: (classification?.subject_id === subject.id || assignedSubject?.id === subject.id) ? 'white' : '#374151',
//                     cursor: 'pointer'
//                   }}
//                 >
//                   {subject.subject_name}
//                 </button>
//               ))}
//             </div>
//           </div>
//         )}

//         {/* Action Buttons */}
//         <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
//           {isProcessing && (
//             <button
//               onClick={() => window.location.reload()}
//               style={{
//                 padding: '10px 20px',
//                 background: '#6b7280',
//                 color: 'white',
//                 border: 'none',
//                 borderRadius: '6px',
//                 cursor: 'pointer'
//               }}
//             >
//               Refresh Page
//             </button>
//           )}
//           <button
//             onClick={onClose}
//             style={{
//               padding: '10px 20px',
//               background: '#374151',
//               color: 'white',
//               border: 'none',
//               borderRadius: '6px',
//               cursor: 'pointer'
//             }}
//           >
//             Close
//           </button>
//         </div>
//       </div>
//     </div>
//   );
// };

// export default DocumentResults;
import React, { useState } from 'react';
import useDocumentPolling from './useDocumentPolling';

const DocumentResults = ({ document, onClose, onSubjectAssigned }) => {
  const [selectedSubject, setSelectedSubject] = useState(null);
  const [subjects, setSubjects] = useState([]);
  const [assignedSubject, setAssignedSubject] = useState(null); // NEW: Track assigned subject
  
  // Use the polling hook
  const { 
    status, 
    summary, 
    classification, 
    error, 
    isProcessing, 
    isComplete 
  } = useDocumentPolling(document?.id, 'processing');

  // Fetch subjects when component mounts
  React.useEffect(() => {
    fetchSubjects();
  }, []);

  // NEW: Fetch assigned subject when classification is available
  React.useEffect(() => {
    if (classification?.subject_id) {
      fetchAssignedSubject(classification.subject_id);
    }
  }, [classification]);

  const fetchSubjects = async () => {
    try {
      const response = await fetch('http://localhost:8000/subjects');
      if (response.ok) {
        const data = await response.json();
        setSubjects(data);
      }
    } catch (error) {
      console.error('Failed to fetch subjects:', error);
    }
  };

  // NEW: Function to fetch the assigned subject details
  const fetchAssignedSubject = async (subjectId) => {
    try {
      const response = await fetch(`http://localhost:8000/subjects/${subjectId}`);
      if (response.ok) {
        const subjectData = await response.json();
        setAssignedSubject(subjectData);
        console.log('✅ Fetched assigned subject:', subjectData.subject_name);
      }
    } catch (error) {
      console.error('Failed to fetch assigned subject:', error);
    }
  };

  const assignToSubject = async (subject) => {
    if (!document?.id) return;
    
    try {
      const response = await fetch(`http://localhost:8000/documents/${document.id}/assign-subject?subject_id=${subject.id}&confidence=1.0&auto_assigned=false`, {
        method: 'POST',
      });

      if (response.ok) {
        setAssignedSubject(subject); // Update local state immediately
        onSubjectAssigned(subject);
        onClose();
      }
    } catch (error) {
      console.error('Failed to assign subject:', error);
    }
  };

  // NEW: Function to get display subject and confidence
  const getDisplayClassification = () => {
    if (assignedSubject) {
      // Document is assigned to a subject
      return {
        subject: assignedSubject.subject_name,
        confidence: classification?.subject_confidence || classification?.confidence || 0,
        source: 'assigned'
      };
    } else if (classification?.primary_topic && classification.primary_topic !== 'manual_assignment') {
      // AI classification available
      return {
        subject: classification.primary_topic,
        confidence: classification.confidence || 0,
        source: 'ai'
      };
    } else {
      // No classification
      return {
        subject: 'Unknown',
        confidence: 0,
        source: 'none'
      };
    }
  };

  const displayClassification = getDisplayClassification();

  return (
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
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h3 style={{ margin: 0 }}>Document Processing Results</h3>
          <button onClick={onClose} style={{ 
            background: 'none', 
            border: 'none', 
            fontSize: '24px', 
            cursor: 'pointer' 
          }}>×</button>
        </div>

        {/* Document Info */}
        <div style={{ marginBottom: '20px' }}>
          <h4>📄 {document?.filename || 'Uploaded Document'}</h4>
        </div>

        {/* Processing Status */}
        <div style={{ marginBottom: '20px' }}>
          <h4>Processing Status:</h4>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span>{isProcessing ? '🔄' : isComplete ? '✅' : '❌'}</span>
            <span>{
              isProcessing ? 'Processing...' : 
              isComplete ? 'Complete!' : 
              error ? `Error: ${error}` : 'Unknown status'
            }</span>
          </div>
        </div>

        {/* Summary Section */}
        <div style={{ marginBottom: '20px' }}>
          <h4>📝 Summary:</h4>
          <div style={{ 
            background: '#f8f9fa', 
            padding: '15px', 
            borderRadius: '8px',
            minHeight: '60px'
          }}>
            {isProcessing ? (
              <div style={{ color: '#6b7280' }}>🔄 Generating summary...</div>
            ) : summary?.summary_text ? (
              <div>{summary.summary_text}</div>
            ) : (
              <div style={{ color: '#ef4444' }}>❌ Summary not available</div>
            )}
          </div>
        </div>

        {/* Classification Section - FIXED */}
        <div style={{ marginBottom: '20px' }}>
          <h4>🏷️ Classification:</h4>
          <div style={{ 
            background: '#f8f9fa', 
            padding: '15px', 
            borderRadius: '8px',
            minHeight: '60px'
          }}>
            {isProcessing ? (
              <div style={{ color: '#6b7280' }}>🔄 Classifying document...</div>
            ) : classification ? (
              <div>
                <div><strong>Subject:</strong> {displayClassification.subject}</div>
                <div><strong>Confidence:</strong> {(displayClassification.confidence * 100).toFixed(1)}%</div>
                {classification.tags && classification.tags.length > 0 && (
                  <div><strong>Tags:</strong> {classification.tags.join(', ')}</div>
                )}
                {displayClassification.source === 'assigned' && (
                  <div style={{ fontSize: '12px', color: '#10b981', marginTop: '5px' }}>
                    ✅ Assigned to subject
                  </div>
                )}
              </div>
            ) : (
              <div style={{ color: '#ef4444' }}>❌ Classification not available</div>
            )}
          </div>
        </div>

        {/* Subject Assignment */}
        {isComplete && (
          <div style={{ marginBottom: '20px' }}>
            <h4>📁 Assign to Subject:</h4>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '10px' }}>
              {subjects.map(subject => (
                <button
                  key={subject.id}
                  onClick={() => assignToSubject(subject)}
                  style={{
                    padding: '10px',
                    border: '1px solid #d1d5db',
                    borderRadius: '6px',
                    background: (classification?.subject_id === subject.id || assignedSubject?.id === subject.id) ? '#3b82f6' : 'white',
                    color: (classification?.subject_id === subject.id || assignedSubject?.id === subject.id) ? 'white' : '#374151',
                    cursor: 'pointer'
                  }}
                >
                  {subject.subject_name}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
          {isProcessing && (
            <button
              onClick={() => window.location.reload()}
              style={{
                padding: '10px 20px',
                background: '#6b7280',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer'
              }}
            >
              Refresh Page
            </button>
          )}
          <button
            onClick={onClose}
            style={{
              padding: '10px 20px',
              background: '#374151',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer'
            }}
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default DocumentResults;
