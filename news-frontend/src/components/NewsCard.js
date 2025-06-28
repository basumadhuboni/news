import React from 'react';
import { Link } from 'react-router-dom';

const NewsCard = ({ title, description, sources, url }) => {
  return (
    <div className="news-card">
      <h3>{title}</h3>
      <p>{description}</p>
      <div className="source-container">
        {sources && sources.length > 0 ? (
          sources.map((source, index) => (
            <a
              key={index}
              href={Array.isArray(url) ? url[index] : url}
              target="_blank"
              rel="noopener noreferrer"
              className="source-button"
            >
              <img
                src={source.icon}
                alt={source.name}
                className="source-icon"
                onError={(e) => { e.target.src = 'https://via.placeholder.com/24'; }}
              />
              {source.name}
            </a>
          ))
        ) : (
          <span>No sources available</span>
        )}
      </div>
      <div className="button-container">
        {Array.isArray(url) ? (
          url.map((singleUrl, index) => (
            <a
              key={index}
              href={singleUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-primary"
              style={{ marginRight: '10px' }}
            >
              Read More ({sources[index]?.name || 'Source'})
            </a>
          ))
        ) : (
          <a
            href={url || '#'}
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-primary"
          >
            Read More
          </a>
        )}
        <Link
          to={`/summary/${encodeURIComponent(url && !Array.isArray(url) ? url : (Array.isArray(url) && url.length > 0 ? url[0] : '#'))}`}
          className="btn btn-secondary"
        >
          Summarization
        </Link>
      </div>
    </div>
  );
};

export default NewsCard;