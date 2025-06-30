import React from 'react';
import { Link } from 'react-router-dom';

const NewsCard = ({ title, description, sources }) => {
  return (
    <div className="news-card">
      <h3>{title}</h3>
      <p>{description}</p>
      <div className="source-container">
        {sources && sources.length > 0 ? (
          sources.map((source, index) => (
            <a
              key={index}
              href={source.url}
              target="_blank"
              rel="noopener noreferrer"
              className="source-button"
            >
              <img
                src={source.icon}
                alt={source.name}
                className="source-icon"
                onError={(e) => { e.target.src = 'https://placehold.co/24x24'; }}
              />
              {source.name}
            </a>
          ))
        ) : (
          <span>No sources available</span>
        )}
      </div>
      <div className="button-container">
        {sources.map((source, index) => (
          <a
            key={index}
            href={source.url}
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-primary"
            style={{ marginRight: '10px' }}
          >
            Read More ({source.name})
          </a>
        ))}
        <Link
          to={`/summary/${encodeURIComponent(sources[0]?.url || '#')}`}
          className="btn btn-secondary"
        >
          Summarization
        </Link>
      </div>
    </div>
  );
};

export default NewsCard;