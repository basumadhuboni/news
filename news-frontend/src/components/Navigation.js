import React from 'react';
import styled from 'styled-components';
import { Link } from 'react-router-dom';
import { FaHome } from 'react-icons/fa';

const NavBar = styled.nav`
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px 0;
  background-color: #ffffff;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
  width: 100%;
  border-radius: 0;
`;

const NavContainer = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  max-width: 1200px;
  padding: 0 32px;
`;

const NavHeader = styled.div`
  display: flex;
  align-items: center;
`;

const NavLink = styled(Link)`
  display: flex;
  align-items: center;
  margin: 0 16px;
  font-size: 16px;
  color: #333;
  text-decoration: none;
  transition: color 0.3s ease;

  &:hover {
    color: #007bff;
  }

  svg {
    margin-right: 8px;
  }
`;

const Logo = styled.div`
  font-size: 20px;
  font-weight: bold;
  color: #007bff;
  margin-right: 16px;
`;

const CategoryContainer = styled.div`
  display: flex;
  align-items: center;
`;

const CategoryButton = styled.button`
  background: none;
  border: none;
  padding: 4px 12px;
  margin: 0 4px;
  font-size: 14px;
  color: #333;
  cursor: pointer;
  transition: color 0.3s ease, background-color 0.3s ease;
  border-radius: 4px;

  &.active {
    background-color: #007bff;
    color: #ffffff;
  }

  &:hover {
    color: #007bff;
    background-color: #f0f0f0;
  }
`;

const Navigation = ({ categories, currentCategory, setCurrentCategory, fetchNews }) => {
  return (
    <NavBar>
      <NavContainer>
        <NavHeader>
          <Logo>News App</Logo>
          <NavLink to="/">
            <FaHome /> Home
          </NavLink>
        </NavHeader>
        <CategoryContainer>
          {categories.map((category) => (
            <CategoryButton
              key={category}
              className={currentCategory === category ? 'active' : ''}
              onClick={() => {
                setCurrentCategory(category);
                fetchNews(category);
              }}
            >
              {category.charAt(0).toUpperCase() + category.slice(1)}
            </CategoryButton>
          ))}
        </CategoryContainer>
      </NavContainer>
    </NavBar>
  );
};

export default Navigation;