import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import axios from 'axios';
import Navigation from './components/Navigation';
import NewsCard from './components/NewsCard';
import LoadingState from './components/LoadingState';
import ArticleSummary from './ArticleSummary';
import './App.css';

const AppContainer = styled.div`
  width: 100%;
  padding: 0;
`;

function App() {
  const [newsArticles, setNewsArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentCategory, setCurrentCategory] = useState('general');
  const categories = ['general', 'business', 'entertainment', 'health', 'science', 'sports', 'technology'];

  useEffect(() => {
    fetchNews(currentCategory);
  }, [currentCategory]);

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

  const newsContent = (
    <>
      {loading ? (
        <LoadingState />
      ) : error ? (
        <p className="text-center text-danger">{error}</p>
      ) : newsArticles.length > 0 ? (
        <>
          <h2 className="h4 mb-3">
            News Articles - {currentCategory.charAt(0).toUpperCase() + currentCategory.slice(1)}
          </h2>
          {newsArticles.map((article, index) => (
            <NewsCard
              key={index}
              title={article.title || 'No title available'}
              description={article.description || 'No description available'}
              sources={article.sources.map(source => ({ name: source.name, icon: source.logo, url: source.url }))}
            />
          ))}
          <button
            onClick={() => fetchNews(currentCategory)}
            className="btn btn-primary mt-4"
          >
            Refresh News
          </button>
        </>
      ) : (
        <p className="text-center">No news articles found for this category.</p>
      )}
    </>
  );

  return (
    <BrowserRouter>
      <AppContainer>
        <Navigation
          categories={categories}
          currentCategory={currentCategory}
          setCurrentCategory={setCurrentCategory}
          fetchNews={fetchNews}
        />
        <Routes>
          <Route path="/" element={newsContent} />
          <Route path="/summary/:url" element={<ArticleSummary />} />
        </Routes>
      </AppContainer>
    </BrowserRouter>
  );
}

export default App;