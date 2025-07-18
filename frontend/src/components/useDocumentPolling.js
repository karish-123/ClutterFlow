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
    
    try {
      // Check summary status
      const summaryResponse = await fetch(`http://localhost:8000/documents/${documentId}/summary`);
      if (summaryResponse.ok) {
        const summaryData = await summaryResponse.json();
        setSummary(summaryData);
      }

      // Check classification status
      const classResponse = await fetch(`http://localhost:8000/documents/${documentId}/classification`);
      if (classResponse.ok) {
        const classData = await classResponse.json();
        setClassification(classData);
      }

      // If both are complete, stop polling
      if (summaryResponse.ok && classResponse.ok) {
        setStatus('complete');
        stopPolling();
      }
    } catch (err) {
      console.error('Error checking document status:', err);
      setError('Failed to check status');
    }
  };

  const startPolling = () => {
    if (intervalRef.current) return; // Already polling
    
    intervalRef.current = setInterval(checkDocumentStatus, 2000); // Check every 2 seconds
    checkDocumentStatus(); // Check immediately
  };

  const stopPolling = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  };

  useEffect(() => {
    if (documentId && status === 'processing') {
      startPolling();
    }

    return () => stopPolling(); // Cleanup on unmount
  }, [documentId, status]);

  // Auto-stop polling after 2 minutes to prevent infinite loops
  useEffect(() => {
    const timeout = setTimeout(() => {
      if (status === 'processing') {
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