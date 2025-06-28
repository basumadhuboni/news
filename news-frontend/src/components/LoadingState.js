import React from 'react';
import styled, { keyframes } from 'styled-components';
import { ClipLoader } from 'react-spinners';

const shimmer = keyframes`
  0% {
    background-position: -200px 0;
  }
  100% {
    background-position: 200px 0;
  }
`;

const SkeletonCard = styled.div`
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  padding: 16px;
  margin: 16px 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const SkeletonLine = styled.div`
  height: 20px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200px 100%;
  animation: ${shimmer} 1.5s infinite linear;
  border-radius: 4px;
`;

const SkeletonSources = styled.div`
  display: flex;
  align-items: center;
`;

const SkeletonCircle = styled.div`
  width: 24px;
  height: 24px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200px 100%;
  animation: ${shimmer} 1.5s infinite linear;
  border-radius: 50%;
  margin-left: -8px;
  &:first-child {
    margin-left: 0;
  }
`;

const SpinnerContainer = styled.div`
  display: flex;
  justify-content: center;
  margin: 32px 0;
`;

const LoadingState = () => {
  return (
    <>
      <SpinnerContainer>
        <ClipLoader color="#007bff" size={40} />
      </SpinnerContainer>
      {[...Array(3)].map((_, index) => (
        <SkeletonCard key={index}>
          <SkeletonLine style={{ width: '60%' }} />
          <SkeletonLine style={{ width: '80%' }} />
          <SkeletonSources>
            <SkeletonCircle />
            <SkeletonCircle />
          </SkeletonSources>
        </SkeletonCard>
      ))}
    </>
  );
};

export default LoadingState;