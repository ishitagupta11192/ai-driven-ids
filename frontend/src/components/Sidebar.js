import React from 'react';
import { NavLink } from 'react-router-dom';
import styled from 'styled-components';
import { 
  Home, 
  Brain, 
  Network, 
  BarChart3, 
  Settings, 
  X,
  Activity,
  Shield
} from 'lucide-react';

const SidebarContainer = styled.aside`
  position: fixed;
  top: 0;
  left: 0;
  width: 250px;
  height: 100vh;
  background: ${props => props.theme.colors.surface};
  border-right: 1px solid ${props => props.theme.colors.border};
  transform: ${props => props.isOpen ? 'translateX(0)' : 'translateX(-100%)'};
  transition: transform 0.3s ease;
  z-index: 200;
  overflow-y: auto;

  @media (min-width: 769px) {
    transform: translateX(0);
  }
`;

const SidebarHeader = styled.div`
  padding: ${props => props.theme.spacing.xl};
  border-bottom: 1px solid ${props => props.theme.colors.border};
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const CloseButton = styled.button`
  display: block;
  background: none;
  border: none;
  cursor: pointer;
  padding: ${props => props.theme.spacing.sm};
  border-radius: ${props => props.theme.borderRadius};
  color: ${props => props.theme.colors.text};
  
  &:hover {
    background-color: ${props => props.theme.colors.background};
  }

  @media (min-width: 769px) {
    display: none;
  }
`;

const Logo = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  font-size: 1.25rem;
  font-weight: 700;
  color: ${props => props.theme.colors.text};
`;

const Navigation = styled.nav`
  padding: ${props => props.theme.spacing.md} 0;
`;

const NavItem = styled(NavLink)`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.md};
  padding: ${props => props.theme.spacing.md} ${props => props.theme.spacing.xl};
  color: ${props => props.theme.colors.textSecondary};
  text-decoration: none;
  transition: all 0.2s ease;
  border-left: 3px solid transparent;

  &:hover {
    background-color: ${props => props.theme.colors.background};
    color: ${props => props.theme.colors.text};
  }

  &.active {
    background-color: ${props => props.theme.colors.primary}10;
    color: ${props => props.theme.colors.primary};
    border-left-color: ${props => props.theme.colors.primary};
  }
`;

const StatusSection = styled.div`
  padding: ${props => props.theme.spacing.xl};
  border-top: 1px solid ${props => props.theme.colors.border};
  margin-top: auto;
`;

const StatusTitle = styled.h3`
  font-size: 0.875rem;
  font-weight: 600;
  color: ${props => props.theme.colors.textSecondary};
  margin-bottom: ${props => props.theme.spacing.md};
  text-transform: uppercase;
  letter-spacing: 0.05em;
`;

const StatusItem = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: ${props => props.theme.spacing.sm} 0;
  font-size: 0.875rem;
`;

const StatusLabel = styled.span`
  color: ${props => props.theme.colors.textSecondary};
`;

const StatusValue = styled.span`
  color: ${props => props.theme.colors.text};
  font-weight: 500;
`;

const StatusIndicator = styled.div`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: ${props => {
    if (props.status === 'loaded') return props.theme.colors.success;
    if (props.status === 'training') return props.theme.colors.warning;
    return props.theme.colors.error;
  }};
`;

const FLStatus = styled.div`
  margin-top: ${props => props.theme.spacing.md};
  padding: ${props => props.theme.spacing.md};
  background-color: ${props => props.theme.colors.background};
  border-radius: ${props => props.theme.borderRadius};
  border: 1px solid ${props => props.theme.colors.border};
`;

const FLTitle = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  font-size: 0.875rem;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.sm};
`;

const FLProgress = styled.div`
  font-size: 0.75rem;
  color: ${props => props.theme.colors.textSecondary};
`;

const Overlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 150;
  display: ${props => props.isOpen ? 'block' : 'none'};

  @media (min-width: 769px) {
    display: none;
  }
`;

function Sidebar({ isOpen, onClose, modelStatus, flProgress }) {
  const getModelStatus = () => {
    if (modelStatus.loaded && !modelStatus.training) return 'loaded';
    if (modelStatus.training) return 'training';
    return 'error';
  };

  const getModelStatusText = () => {
    if (modelStatus.loaded && !modelStatus.training) return 'Ready';
    if (modelStatus.training) return 'Training';
    return 'Offline';
  };

  return (
    <>
      <Overlay isOpen={isOpen} onClick={onClose} />
      <SidebarContainer isOpen={isOpen}>
        <SidebarHeader>
          <Logo>
            <Shield size={24} />
            IDS
          </Logo>
          <CloseButton onClick={onClose}>
            <X size={20} />
          </CloseButton>
        </SidebarHeader>

        <Navigation>
          <NavItem to="/" end>
            <Home size={20} />
            Dashboard
          </NavItem>
          <NavItem to="/inference">
            <Brain size={20} />
            Inference
          </NavItem>
          <NavItem to="/federated-learning">
            <Network size={20} />
            Federated Learning
          </NavItem>
          <NavItem to="/model-status">
            <Activity size={20} />
            Model Status
          </NavItem>
          <NavItem to="/metrics">
            <BarChart3 size={20} />
            Metrics
          </NavItem>
        </Navigation>

        <StatusSection>
          <StatusTitle>System Status</StatusTitle>
          
          <StatusItem>
            <StatusLabel>Model</StatusLabel>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <StatusIndicator status={getModelStatus()} />
              <StatusValue>{getModelStatusText()}</StatusValue>
            </div>
          </StatusItem>

          {modelStatus.accuracy > 0 && (
            <StatusItem>
              <StatusLabel>Accuracy</StatusLabel>
              <StatusValue>{modelStatus.accuracy.toFixed(1)}%</StatusValue>
            </StatusItem>
          )}

          {modelStatus.lastUpdated && (
            <StatusItem>
              <StatusLabel>Last Updated</StatusLabel>
              <StatusValue>
                {new Date(modelStatus.lastUpdated).toLocaleTimeString()}
              </StatusValue>
            </StatusItem>
          )}

          {flProgress.status !== 'idle' && (
            <FLStatus>
              <FLTitle>
                <Network size={16} />
                Federated Learning
              </FLTitle>
              <FLProgress>
                Round {flProgress.round} of {flProgress.totalRounds}
                <br />
                Status: {flProgress.status}
                <br />
                Accuracy: {flProgress.accuracy.toFixed(1)}%
              </FLProgress>
            </FLStatus>
          )}
        </StatusSection>
      </SidebarContainer>
    </>
  );
}

export default Sidebar;
