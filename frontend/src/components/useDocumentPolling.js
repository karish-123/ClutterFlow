// Create this as a custom hook: useDocumentPolling.js
import { useState, useEffect, useRef } from 'react';

const useDocumentPolling = (documentId, initialStatus = 'processing') => {
  const [status, setStatus] = useState(initialStatus);
  const [summary, setSummary] = useState(null);
  const [classification, setClassification] = useState(null);
  const [error, setError] = useState(null);
  const intervalRef = useRef(null);

  const checkDocumentStatus = async () => {
    if (!documentId) return;
    
    console.log('🔍 Checking status for document:', documentId);
    
    try {
      // Check summary status
      console.log('📝 Checking summary...');
      const summaryResponse = await fetch(`http://localhost:8000/documents/${documentId}/summary`);
      console.log('📝 Summary response status:', summaryResponse.status);
      
      if (summaryResponse.ok) {
        const summaryData = await summaryResponse.json();
        console.log('📝 Summary data:', summaryData);
        setSummary(summaryData);
      } else {
        console.log('📝 Summary not ready yet');
      }

      // Check classification status
      console.log('🏷️ Checking classification...');
      const classResponse = await fetch(`http://localhost:8000/documents/${documentId}/classification`);
      console.log('🏷️ Classification response status:', classResponse.status);
      
      if (classResponse.ok) {
        const classData = await classResponse.json();
        console.log('🏷️ Classification data:', classData);
        setClassification(classData);
      } else {
        console.log('🏷️ Classification not ready yet');
      }

      // If both are complete, stop polling
      if (summaryResponse.ok && classResponse.ok) {
        console.log('✅ Both summary and classification complete!');
        setStatus('complete');
        stopPolling();
      } else {
        console.log('⏳ Still waiting for processing to complete...');
      }
    } catch (err) {
      console.error('❌ Error checking document status:', err);
      setError('Failed to check status');
    }
  };

  const startPolling = () => {
    if (intervalRef.current) return; // Already polling
    
    console.log('🚀 Starting polling for document:', documentId);
    intervalRef.current = setInterval(checkDocumentStatus, 3000); // Check every 3 seconds
    checkDocumentStatus(); // Check immediately
  };

  const stopPolling = () => {
    if (intervalRef.current) {
      console.log('🛑 Stopping polling for document:', documentId);
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  };

  useEffect(() => {
    console.log('🔄 useEffect triggered - documentId:', documentId, 'status:', status);
    if (documentId && status === 'processing') {
      startPolling();
    }

    return () => stopPolling(); // Cleanup on unmount
  }, [documentId, status]);

  // Auto-stop polling after 2 minutes to prevent infinite loops
  useEffect(() => {
    const timeout = setTimeout(() => {
      if (status === 'processing') {
        console.log('⏰ Polling timeout reached');
        stopPolling();
        setStatus('timeout');
        setError('Processing took too long');
      }
    }, 120000); // 2 minutes

    return () => clearTimeout(timeout);
  }, [status]);

  return {
    status,
    summary,
    classification,
    error,
    isProcessing: status === 'processing',
    isComplete: status === 'complete',
    checkNow: checkDocumentStatus
  };
};

export default useDocumentPolling;



// // src/hooks/useDocumentPolling.js
// import { useState, useEffect, useRef } from 'react';

// // Define the API URL from environment variables
// const API_URL = process.env.REACT_APP_BACKEND_API_URL;

// const useDocumentPolling = (documentId, initialStatus = 'processing') => {
//   const [status, setStatus] = useState(initialStatus);
//   const [summary, setSummary] = useState(null);
//   const [classification, setClassification] = useState(null);
//   const [error, setError] = useState(null);
//   const intervalRef = useRef(null);

//   const checkDocumentStatus = async () => {
//     if (!documentId) return;
    
//     console.log('🔍 Checking status for document:', documentId);
    
//     try {
//       // Check summary status
//       console.log('📝 Checking summary...');
//       const summaryResponse = await fetch(`${API_URL}/documents/${documentId}/summary`);
//       console.log('📝 Summary response status:', summaryResponse.status);
      
//       if (summaryResponse.ok) {
//         const summaryData = await summaryResponse.json();
//         console.log('📝 Summary data:', summaryData);
//         setSummary(summaryData);
//       } else {
//         console.log('📝 Summary not ready yet');
//       }

//       // Check classification status
//       console.log('🏷️ Checking classification...');
//       const classResponse = await fetch(`${API_URL}/documents/${documentId}/classification`);
//       console.log('🏷️ Classification response status:', classResponse.status);
      
//       if (classResponse.ok) {
//         const classData = await classResponse.json();
//         console.log('🏷️ Classification data:', classData);
//         setClassification(classData);
//       } else {
//         console.log('🏷️ Classification not ready yet');
//       }

//       // If both are complete, stop polling
//       if (summaryResponse.ok && classResponse.ok) {
//         console.log('✅ Both summary and classification complete!');
//         setStatus('complete');
//         stopPolling();
//       } else {
//         console.log('⏳ Still waiting for processing to complete...');
//       }
//     } catch (err) {
//       console.error('❌ Error checking document status:', err);
//       setError('Failed to check status');
//     }
//   };

//   const startPolling = () => {
//     if (intervalRef.current) return; // Already polling
    
//     console.log('🚀 Starting polling for document:', documentId);
//     intervalRef.current = setInterval(checkDocumentStatus, 3000); // Check every 3 seconds
//     checkDocumentStatus(); // Check immediately
//   };

//   const stopPolling = () => {
//     if (intervalRef.current) {
//       console.log('🛑 Stopping polling for document:', documentId);
//       clearInterval(intervalRef.current);
//       intervalRef.current = null;
//     }
//   };

//   useEffect(() => {
//     console.log('🔄 useEffect triggered - documentId:', documentId, 'status:', status);
//     if (documentId && status === 'processing') {
//       startPolling();
//     }

//     return () => stopPolling(); // Cleanup on unmount
//   }, [documentId, status]);

//   // Auto-stop polling after 2 minutes to prevent infinite loops
//   useEffect(() => {
//     const timeout = setTimeout(() => {
//       if (status === 'processing') {
//         console.log('⏰ Polling timeout reached');
//         stopPolling();
//         setStatus('timeout');
//         setError('Processing took too long');
//       }
//     }, 120000); // 2 minutes

//     return () => clearTimeout(timeout);
//   }, [status]);

//   return {
//     status,
//     summary,
//     classification,
//     error,
//     isProcessing: status === 'processing',
//     isComplete: status === 'complete',
//     checkNow: checkDocumentStatus
//   };
// };

// export default useDocumentPolling;
