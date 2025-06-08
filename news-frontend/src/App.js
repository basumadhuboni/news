import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [newsArticles, setNewsArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentCategory, setCurrentCategory] = useState('general');
  const categories = ['general', 'business', 'entertainment', 'health', 'science', 'sports', 'technology'];

  useEffect(() => {
    fetchNews(currentCategory);
  }, []);

  const fetchNews = async (category) => {
    try {
      setLoading(true);
      const url = `http://localhost:8000/news?category=${category}`;
      const response = await axios.get(url);
      if (response.data.news_articles && response.data.news_articles.length > 0) {
        setNewsArticles(response.data.news_articles);
        setError(null);
      } else {
        setNewsArticles([]);
        setError(response.data.error || `No news articles found for category: ${category}.`);
      }
      setLoading(false);
    } catch (err) {
      setError('Failed to connect to backend. Ensure it is running at http://localhost:8000.');
      setLoading(false);
      console.error(err);
    }
  };

  return (
    <div className="container my-4">
      <h1 className="text-center mb-4">Intelligent News</h1>
      <div className="mb-3 text-center">
        {categories.map(category => (
          <button
            key={category}
            className={`btn btn-outline-primary me-2 ${currentCategory === category ? 'active' : ''}`}
            onClick={() => {
              setCurrentCategory(category);
              fetchNews(category);
            }}
          >
            {category.charAt(0).toUpperCase() + category.slice(1)}
          </button>
        ))}
      </div>
      {loading && <p className="text-center text-muted">Loading...</p>}
      {error && <p className="text-center text-danger">{error}</p>}
      
      <h2 className="h4 mb-3">News Articles - {currentCategory.charAt(0).toUpperCase() + currentCategory.slice(1)}</h2>
      {newsArticles.length > 0 ? (
        newsArticles.map((article, index) => (
          <div key={index} className="card mb-3">
            <div className="card-body">
              <h5 className="card-title">{article.title || 'No title available'}</h5>
              <p className="card-text">{article.description || 'No description available'}</p>
              <p className="text-muted small">Source: {article.source || 'Unknown'}</p>
              <a href={article.url} target="_blank" rel="noopener noreferrer" className="btn btn-primary btn-sm">Read more</a>
            </div>
          </div>
        ))
      ) : (
        !loading && !error && <p className="text-center">No news articles found for this category.</p>
      )}
      
      <button
        onClick={() => fetchNews(currentCategory)}
        className="btn btn-primary mt-4"
      >
        Refresh News
      </button>
    </div>
  );
}

export default App;