import React from 'react';
import styled from 'styled-components';
import { Menu, Shield, Activity, Wifi, WifiOff } from 'lucide-react';

const HeaderContainer = styled.header`
  background: ${props => props.theme.colors.surface};
  border-bottom: 1px solid ${props => props.theme.colors.border};
  padding: ${props => props.theme.spacing.md} ${props => props.theme.spacing.xl};
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: ${props => props.theme.shadows.sm};
  position: sticky;
  top: 0;
  z-index: 100;
`;

const LeftSection = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.md};
`;

const MenuButton = styled.button`
  display: none;
  background: none;
  border: none;
  cursor: pointer;
  padding: ${props => props.theme.spacing.sm};
  border-radius: ${props => props.theme.borderRadius};
  color: ${props => props.theme.colors.text};
  
  &:hover {
    background-color: ${props => props.theme.colors.background};
  }

  @media (max-width: 768px) {
    display: block;
  }
`;

const Title = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  font-size: 1.5rem;
  font-weight: 700;
  color: ${props => props.theme.colors.text};
`;

const RightSection = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.lg};
`;

const StatusIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  border-radius: ${props => props.theme.borderRadius};
  background-color: ${props => {
    if (props.status === 'loaded') return props.theme.colors.success;
    if (props.status === 'training') return props.theme.colors.warning;
    return props.theme.colors.error;
  }};
  color: white;
  font-size: 0.875rem;
  font-weight: 500;
`;

const StatusText = styled.span`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.xs};
`;

const AccuracyBadge = styled.div`
  background-color: ${props => props.theme.colors.primary};
  color: white;
  padding: ${props => props.theme.spacing.xs} ${props => props.theme.spacing.sm};
  border-radius: ${props => props.theme.borderRadius};
  font-size: 0.75rem;
  font-weight: 600;
`;

const FLProgress = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  background-color: ${props => props.theme.colors.background};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius};
  font-size: 0.875rem;
`;

const ProgressBar = styled.div`
  width: 100px;
  height: 4px;
  background-color: ${props => props.theme.colors.border};
  border-radius: 2px;
  overflow: hidden;
`;

const ProgressFill = styled.div`
  height: 100%;
  background-color: ${props => props.theme.colors.primary};
  width: ${props => (props.progress / props.total) * 100}%;
  transition: width 0.3s ease;
`;

function Header({ onMenuClick, modelStatus, flProgress }) {
  const getModelStatusColor = () => {
    if (modelStatus.loaded && !modelStatus.training) return 'loaded';
    if (modelStatus.training) return 'training';
    return 'error';
  };

  const getModelStatusText = () => {
    if (modelStatus.loaded && !modelStatus.training) return 'Model Ready';
    if (modelStatus.training) return 'Training';
    return 'Model Offline';
  };

  const getModelStatusIcon = () => {
    if (modelStatus.loaded && !modelStatus.training) return <Shield size={16} />;
    if (modelStatus.training) return <Activity size={16} />;
    return <WifiOff size={16} />;
  };

  return (
    <HeaderContainer>
      <LeftSection>
        <MenuButton onClick={onMenuClick}>
          <Menu size={20} />
        </MenuButton>
        <Title>
          <Shield size={24} />
          AI-Driven IDS
        </Title>
      </LeftSection>

      <RightSection>
        {flProgress.status !== 'idle' && (
          <FLProgress>
            <Wifi size={16} />
            <span>FL Round {flProgress.round}/{flProgress.totalRounds}</span>
            <ProgressBar>
              <ProgressFill 
                progress={flProgress.round} 
                total={flProgress.totalRounds} 
              />
            </ProgressBar>
            <span>{flProgress.accuracy.toFixed(1)}%</span>
          </FLProgress>
        )}

        <StatusIndicator status={getModelStatusColor()}>
          <StatusText>
            {getModelStatusIcon()}
            {getModelStatusText()}
          </StatusText>
        </StatusIndicator>

        {modelStatus.accuracy > 0 && (
          <AccuracyBadge>
            {modelStatus.accuracy.toFixed(1)}% Acc
          </AccuracyBadge>
        )}
      </RightSection>
    </HeaderContainer>
  );
}

export default Header;
