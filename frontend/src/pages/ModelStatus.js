import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { 
  Activity, 
  Brain, 
  Database, 
  Cpu, 
  MemoryStick,
  Clock,
  CheckCircle,
  AlertCircle,
  RefreshCw
} from 'lucide-react';

const StatusContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
`;

const Header = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: ${props => props.theme.spacing.xl};
`;

const Title = styled.h1`
  font-size: 2rem;
  font-weight: 700;
  color: ${props => props.theme.colors.text};
`;

const RefreshButton = styled.button`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  padding: ${props => props.theme.spacing.md} ${props => props.theme.spacing.lg};
  background-color: ${props => props.theme.colors.primary};
  color: white;
  border: none;
  border-radius: ${props => props.theme.borderRadius};
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background-color: ${props => props.theme.colors.primary}dd;
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const StatusGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: ${props => props.theme.spacing.lg};
  margin-bottom: ${props => props.theme.spacing.xl};
`;

const StatusCard = styled.div`
  background: ${props => props.theme.colors.surface};
  padding: ${props => props.theme.spacing.xl};
  border-radius: ${props => props.theme.borderRadius};
  box-shadow: ${props => props.theme.shadows.md};
  border: 1px solid ${props => props.theme.colors.border};
`;

const CardHeader = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.md};
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const CardIcon = styled.div`
  width: 48px;
  height: 48px;
  border-radius: ${props => props.theme.borderRadius};
  background-color: ${props => props.color}20;
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${props => props.color};
`;

const CardTitle = styled.h3`
  font-size: 1.25rem;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
`;

const StatusItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: ${props => props.theme.spacing.sm} 0;
  border-bottom: 1px solid ${props => props.theme.colors.border};

  &:last-child {
    border-bottom: none;
  }
`;

const StatusLabel = styled.span`
  color: ${props => props.theme.colors.textSecondary};
  font-size: 0.875rem;
`;

const StatusValue = styled.span`
  color: ${props => props.theme.colors.text};
  font-weight: 600;
  font-size: 0.875rem;
`;

const StatusIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.xs};
  padding: ${props => props.theme.spacing.xs} ${props => props.theme.spacing.sm};
  border-radius: ${props => props.theme.borderRadius};
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  
  ${props => {
    switch (props.status) {
      case 'loaded':
        return `
          background-color: ${props.theme.colors.success}20;
          color: ${props.theme.colors.success};
        `;
      case 'training':
        return `
          background-color: ${props.theme.colors.warning}20;
          color: ${props.theme.colors.warning};
        `;
      case 'error':
        return `
          background-color: ${props.theme.colors.error}20;
          color: ${props.theme.colors.error};
        `;
      default:
        return `
          background-color: ${props.theme.colors.textSecondary}20;
          color: ${props.theme.colors.textSecondary};
        `;
    }
  }}
`;

const ModelInfoCard = styled.div`
  background: ${props => props.theme.colors.surface};
  padding: ${props => props.theme.spacing.xl};
  border-radius: ${props => props.theme.borderRadius};
  box-shadow: ${props => props.theme.shadows.md};
  border: 1px solid ${props => props.theme.colors.border};
  margin-bottom: ${props => props.theme.spacing.xl};
`;

const InfoGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: ${props => props.theme.spacing.lg};
`;

const InfoItem = styled.div`
  text-align: center;
`;

const InfoValue = styled.div`
  font-size: 2rem;
  font-weight: 700;
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.xs};
`;

const InfoLabel = styled.div`
  font-size: 0.875rem;
  color: ${props => props.theme.colors.textSecondary};
  text-transform: uppercase;
  letter-spacing: 0.05em;
`;

const LoadingSpinner = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  padding: ${props => props.theme.spacing.xxl};
  color: ${props => props.theme.colors.textSecondary};
`;

function ModelStatus({ modelStatus }) {
  const [detailedStatus, setDetailedStatus] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    fetchDetailedStatus();
  }, []);

  const fetchDetailedStatus = async () => {
    try {
      setIsRefreshing(true);
      const response = await fetch('/api/model-status');
      if (response.ok) {
        const data = await response.json();
        setDetailedStatus(data);
      }
    } catch (error) {
      console.error('Error fetching detailed status:', error);
    } finally {
      setIsRefreshing(false);
    }
  };

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

  const getModelStatusIcon = () => {
    if (modelStatus.loaded && !modelStatus.training) return <CheckCircle size={16} />;
    if (modelStatus.training) return <Activity size={16} />;
    return <AlertCircle size={16} />;
  };

  const formatNumber = (num) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  };

  if (!detailedStatus) {
    return (
      <StatusContainer>
        <LoadingSpinner>
          <RefreshCw size={32} className="animate-spin" />
          <span style={{ marginLeft: '1rem' }}>Loading model status...</span>
        </LoadingSpinner>
      </StatusContainer>
    );
  }

  return (
    <StatusContainer>
      <Header>
        <Title>Model Status</Title>
        <RefreshButton onClick={fetchDetailedStatus} disabled={isRefreshing}>
          <RefreshCw size={20} className={isRefreshing ? 'animate-spin' : ''} />
          Refresh
        </RefreshButton>
      </Header>

      <StatusGrid>
        <StatusCard>
          <CardHeader>
            <CardIcon color="#10b981">
              <Brain size={24} />
            </CardIcon>
            <CardTitle>Model Status</CardTitle>
          </CardHeader>
          <StatusItem>
            <StatusLabel>Status</StatusLabel>
            <StatusIndicator status={getModelStatus()}>
              {getModelStatusIcon()}
              {getModelStatusText()}
            </StatusIndicator>
          </StatusItem>
          <StatusItem>
            <StatusLabel>Accuracy</StatusLabel>
            <StatusValue>{modelStatus.accuracy.toFixed(1)}%</StatusValue>
          </StatusItem>
          <StatusItem>
            <StatusLabel>Last Updated</StatusLabel>
            <StatusValue>
              {modelStatus.lastUpdated 
                ? new Date(modelStatus.lastUpdated).toLocaleString()
                : 'Never'
              }
            </StatusValue>
          </StatusItem>
        </StatusCard>

        <StatusCard>
          <CardHeader>
            <CardIcon color="#2563eb">
              <Cpu size={24} />
            </CardIcon>
            <CardTitle>Model Architecture</CardTitle>
          </CardHeader>
          <StatusItem>
            <StatusLabel>Input Size</StatusLabel>
            <StatusValue>{detailedStatus.model_info?.input_size || 'N/A'}</StatusValue>
          </StatusItem>
          <StatusItem>
            <StatusLabel>Sequence Length</StatusLabel>
            <StatusValue>{detailedStatus.model_info?.sequence_length || 'N/A'}</StatusValue>
          </StatusItem>
          <StatusItem>
            <StatusLabel>Number of Classes</StatusLabel>
            <StatusValue>{detailedStatus.model_info?.n_classes || 'N/A'}</StatusValue>
          </StatusItem>
        </StatusCard>

        <StatusCard>
          <CardHeader>
            <CardIcon color="#8b5cf6">
              <MemoryStick size={24} />
            </CardIcon>
            <CardTitle>Model Parameters</CardTitle>
          </CardHeader>
          <StatusItem>
            <StatusLabel>Total Parameters</StatusLabel>
            <StatusValue>
              {detailedStatus.model_info?.total_parameters 
                ? formatNumber(detailedStatus.model_info.total_parameters)
                : 'N/A'
              }
            </StatusValue>
          </StatusItem>
          <StatusItem>
            <StatusLabel>Trainable Parameters</StatusLabel>
            <StatusValue>
              {detailedStatus.model_info?.trainable_parameters 
                ? formatNumber(detailedStatus.model_info.trainable_parameters)
                : 'N/A'
              }
            </StatusValue>
          </StatusItem>
          <StatusItem>
            <StatusLabel>CNN Filters</StatusLabel>
            <StatusValue>
              {detailedStatus.model_info?.cnn_filters 
                ? detailedStatus.model_info.cnn_filters.join(', ')
                : 'N/A'
              }
            </StatusValue>
          </StatusItem>
        </StatusCard>

        <StatusCard>
          <CardHeader>
            <CardIcon color="#f59e0b">
              <Database size={24} />
            </CardIcon>
            <CardTitle>Training Configuration</CardTitle>
          </CardHeader>
          <StatusItem>
            <StatusLabel>LSTM Hidden Size</StatusLabel>
            <StatusValue>{detailedStatus.model_info?.lstm_hidden || 'N/A'}</StatusValue>
          </StatusItem>
          <StatusItem>
            <StatusLabel>LSTM Layers</StatusLabel>
            <StatusValue>{detailedStatus.model_info?.lstm_layers || 'N/A'}</StatusValue>
          </StatusItem>
          <StatusItem>
            <StatusLabel>Model Type</StatusLabel>
            <StatusValue>Hybrid CNN+LSTM</StatusValue>
          </StatusItem>
        </StatusCard>
      </StatusGrid>

      <ModelInfoCard>
        <CardHeader>
          <CardIcon color="#64748b">
            <Clock size={24} />
          </CardIcon>
          <CardTitle>System Information</CardTitle>
        </CardHeader>
        <InfoGrid>
          <InfoItem>
            <InfoValue>{detailedStatus.loaded ? 'Yes' : 'No'}</InfoValue>
            <InfoLabel>Model Loaded</InfoLabel>
          </InfoItem>
          <InfoItem>
            <InfoValue>{detailedStatus.training ? 'Yes' : 'No'}</InfoValue>
            <InfoLabel>Currently Training</InfoLabel>
          </InfoItem>
          <InfoItem>
            <InfoValue>
              {detailedStatus.last_updated 
                ? new Date(detailedStatus.last_updated).toLocaleDateString()
                : 'N/A'
              }
            </InfoValue>
            <InfoLabel>Last Updated</InfoLabel>
          </InfoItem>
          <InfoItem>
            <InfoValue>
              {detailedStatus.accuracy > 0 
                ? detailedStatus.accuracy.toFixed(1) + '%'
                : 'N/A'
              }
            </InfoValue>
            <InfoLabel>Current Accuracy</InfoLabel>
          </InfoItem>
        </InfoGrid>
      </ModelInfoCard>
    </StatusContainer>
  );
}

export default ModelStatus;
