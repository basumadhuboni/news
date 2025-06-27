import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';

function ArticleSummary() {
  const { url } = useParams();
  const decodedUrl = decodeURIComponent(url);
  const [summary, setSummary] = useState(null);
  const [translatedSummary, setTranslatedSummary] = useState(null);
  const [selectedLanguage, setSelectedLanguage] = useState('');
  const [loadingSummary, setLoadingSummary] = useState(true);
  const [loadingTranslation, setLoadingTranslation] = useState(false);

  const languages = [
    { code: 'spanish', name: 'Spanish' },
    { code: 'french', name: 'French' },
    { code: 'german', name: 'German' },
    { code: 'hindi', name: 'Hindi' },
    { code: 'chinese (simplified)', name: 'Chinese (Simplified)' },
  ];

  useEffect(() => {
    const fetchSummary = async () => {
      setLoadingSummary(true);
      try {
        const query = `Summarize this article: ${decodedUrl}`;
        const res = await fetch('http://localhost:8000/query', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ input: query }),
        });
        if (!res.ok) {
          const errorData = await res.json();
          throw new Error(errorData.detail || `HTTP error! status: ${res.status}`);
        }
        const data = await res.json();
        setSummary(data.output);
      } catch (err) {
        setSummary(`❌ Error: ${err.message || 'Failed to fetch summary'}`);
      }
      setLoadingSummary(false);
    };
    fetchSummary();
  }, [decodedUrl]);

  const handleLanguageChange = async (langCode) => {
    setSelectedLanguage(langCode);
    if (!summary || langCode === '') {
      setTranslatedSummary(null);
      return;
    }
    setLoadingTranslation(true);
    try {
      const query = `Translate this text to ${langCode}: ${summary}`;
      const res = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ input: query }),
      });
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || `HTTP error! status: ${res.status}`);
      }
      const data = await res.json();
      setTranslatedSummary(data.output);
    } catch (err) {
      setTranslatedSummary(`❌ Error: ${err.message || 'Failed to translate'}`);
    }
    setLoadingTranslation(false);
  };

  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <h2>🧠 Article Summary</h2>
      {loadingSummary ? (
        <p>Loading summary...</p>
      ) : (
        <div style={{ marginTop: '2rem', whiteSpace: 'pre-line' }}>
          <h3>🔍 English Summary:</h3>
          <p>{summary}</p>
          <select
            value={selectedLanguage}
            onChange={(e) => handleLanguageChange(e.target.value)}
            style={{ margin: '1rem 0', padding: '0.5rem' }}
          >
            <option value="">Select Language</option>
            {languages.map((lang) => (
              <option key={lang.code} value={lang.code}>
                {lang.name}
              </option>
            ))}
          </select>
          {loadingTranslation && <p>Translating...</p>}
          {translatedSummary && (
            <div style={{ marginTop: '1rem' }}>
              <h3>🔍 Translated Summary ({languages.find(lang => lang.code === selectedLanguage).name}):</h3>
              <p>{translatedSummary}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default ArticleSummary;