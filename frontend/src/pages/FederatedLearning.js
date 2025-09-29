import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { 
  Play, 
  Pause, 
  Square, 
  Users, 
  TrendingUp, 
  Clock,
  CheckCircle,
  AlertCircle,
  Loader
} from 'lucide-react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { toast } from 'react-toastify';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const FLContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
`;

const Header = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: ${props => props.theme.spacing.xl};
`;

const PageTitle = styled.h1`
  font-size: 2rem;
  font-weight: 700;
  color: ${props => props.theme.colors.text};
`;

const ControlPanel = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.md};
`;

const Button = styled.button`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  padding: ${props => props.theme.spacing.md} ${props => props.theme.spacing.lg};
  border: none;
  border-radius: ${props => props.theme.borderRadius};
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  
  ${props => {
    switch (props.variant) {
      case 'primary':
        return `
          background-color: ${props.theme.colors.primary};
          color: white;
          &:hover {
            background-color: ${props.theme.colors.primary}dd;
          }
        `;
      case 'secondary':
        return `
          background-color: ${props.theme.colors.secondary};
          color: white;
          &:hover {
            background-color: ${props.theme.colors.secondary}dd;
          }
        `;
      case 'danger':
        return `
          background-color: ${props.theme.colors.error};
          color: white;
          &:hover {
            background-color: ${props.theme.colors.error}dd;
          }
        `;
      default:
        return `
          background-color: ${props.theme.colors.surface};
          color: ${props.theme.colors.text};
          border: 1px solid ${props.theme.colors.border};
          &:hover {
            background-color: ${props.theme.colors.background};
          }
        `;
    }
  }}

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const StatusCard = styled.div`
  background: ${props => props.theme.colors.surface};
  padding: ${props => props.theme.spacing.xl};
  border-radius: ${props => props.theme.borderRadius};
  box-shadow: ${props => props.theme.shadows.md};
  border: 1px solid ${props => props.theme.colors.border};
  margin-bottom: ${props => props.theme.spacing.xl};
`;

const StatusGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: ${props => props.theme.spacing.lg};
  margin-bottom: ${props => props.theme.spacing.xl};
`;

const StatusItem = styled.div`
  text-align: center;
`;

const StatusValue = styled.div`
  font-size: 2rem;
  font-weight: 700;
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.xs};
`;

const StatusLabel = styled.div`
  font-size: 0.875rem;
  color: ${props => props.theme.colors.textSecondary};
  text-transform: uppercase;
  letter-spacing: 0.05em;
`;

const ProgressBar = styled.div`
  width: 100%;
  height: 8px;
  background-color: ${props => props.theme.colors.border};
  border-radius: 4px;
  overflow: hidden;
  margin: ${props => props.theme.spacing.md} 0;
`;

const ProgressFill = styled.div`
  height: 100%;
  background: linear-gradient(90deg, ${props => props.theme.colors.primary}, ${props => props.theme.colors.secondary});
  width: ${props => (props.progress / props.total) * 100}%;
  transition: width 0.3s ease;
`;

const ClientsSection = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: ${props => props.theme.spacing.lg};
  margin-bottom: ${props => props.theme.spacing.xl};
`;

const ClientCard = styled.div`
  background: ${props => props.theme.colors.surface};
  padding: ${props => props.theme.spacing.lg};
  border-radius: ${props => props.theme.borderRadius};
  box-shadow: ${props => props.theme.shadows.md};
  border: 1px solid ${props => props.theme.colors.border};
`;

const ClientHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: ${props => props.theme.spacing.md};
`;

const ClientName = styled.h3`
  font-size: 1.125rem;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
`;

const ClientStatus = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.xs};
  font-size: 0.875rem;
  color: ${props => {
    switch (props.status) {
      case 'active':
        return props.theme.colors.success;
      case 'training':
        return props.theme.colors.warning;
      case 'error':
        return props.theme.colors.error;
      default:
        return props.theme.colors.textSecondary;
    }
  }};
`;

const ClientMetrics = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: ${props => props.theme.spacing.md};
`;

const Metric = styled.div`
  text-align: center;
`;

const MetricValue = styled.div`
  font-size: 1.5rem;
  font-weight: 700;
  color: ${props => props.theme.colors.text};
`;

const MetricLabel = styled.div`
  font-size: 0.75rem;
  color: ${props => props.theme.colors.textSecondary};
  text-transform: uppercase;
  letter-spacing: 0.05em;
`;

const ChartCard = styled.div`
  background: ${props => props.theme.colors.surface};
  padding: ${props => props.theme.spacing.xl};
  border-radius: ${props => props.theme.borderRadius};
  box-shadow: ${props => props.theme.shadows.md};
  border: 1px solid ${props => props.theme.colors.border};
`;

const ChartTitle = styled.h3`
  font-size: 1.25rem;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.lg};
`;

function FederatedLearning({ onProgressUpdate }) {
  const [flStatus, setFlStatus] = useState({
    round: 0,
    totalRounds: 0,
    status: 'idle',
    accuracy: 0,
    clients: []
  });
  const [isRunning, setIsRunning] = useState(false);
  const [roundHistory, setRoundHistory] = useState([]);

  useEffect(() => {
    fetchFlProgress();
    const interval = setInterval(fetchFlProgress, 2000);
    return () => clearInterval(interval);
  }, []);

  const fetchFlProgress = async () => {
    try {
      const response = await fetch('/api/fl-progress');
      if (response.ok) {
        const data = await response.json();
        setFlStatus(data);
        onProgressUpdate(data);
        
        // Update round history for chart
        if (data.round > 0 && data.accuracy > 0) {
          setRoundHistory(prev => {
            const newHistory = [...prev];
            if (newHistory.length === 0 || newHistory[newHistory.length - 1].round !== data.round) {
              newHistory.push({
                round: data.round,
                accuracy: data.accuracy,
                timestamp: data.timestamp
              });
            }
            return newHistory;
          });
        }
      }
    } catch (error) {
      console.error('Error fetching FL progress:', error);
    }
  };

  const startFederatedLearning = async () => {
    try {
      setIsRunning(true);
      const response = await fetch('/api/start-fl', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          rounds: 5,
          clients: ['client_1', 'client_2', 'client_3']
        }),
      });

      if (response.ok) {
        toast.success('Federated learning started successfully!');
        setRoundHistory([]);
      } else {
        toast.error('Failed to start federated learning');
      }
    } catch (error) {
      toast.error('Error starting federated learning');
      console.error('Error:', error);
    } finally {
      setIsRunning(false);
    }
  };

  const stopFederatedLearning = () => {
    // In a real implementation, this would call a stop endpoint
    toast.info('Federated learning stopped');
  };

  // Chart data for accuracy progression
  const accuracyChartData = {
    labels: roundHistory.map(item => `Round ${item.round}`),
    datasets: [
      {
        label: 'Global Accuracy',
        data: roundHistory.map(item => item.accuracy),
        borderColor: '#2563eb',
        backgroundColor: '#2563eb20',
        tension: 0.4,
        fill: true,
      },
    ],
  };

  const accuracyChartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: false,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        ticks: {
          callback: function(value) {
            return value + '%';
          }
        }
      },
    },
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active':
      case 'running':
        return <Loader size={16} className="animate-spin" />;
      case 'completed':
        return <CheckCircle size={16} />;
      case 'error':
        return <AlertCircle size={16} />;
      default:
        return <Clock size={16} />;
    }
  };

  const getClientStatus = (clientId) => {
    const client = flStatus.clients.find(c => c.id === clientId);
    return client ? client.status : 'pending';
  };

  const getClientAccuracy = (clientId) => {
    const client = flStatus.clients.find(c => c.id === clientId);
    return client ? client.accuracy : 0;
  };

  const getClientSamples = (clientId) => {
    const client = flStatus.clients.find(c => c.id === clientId);
    return client ? client.samples : 0;
  };

  return (
    <FLContainer>
      <Header>
        <PageTitle>Federated Learning</PageTitle>
        <ControlPanel>
          <Button
            variant="primary"
            onClick={startFederatedLearning}
            disabled={isRunning || flStatus.status === 'running'}
          >
            <Play size={20} />
            Start FL
          </Button>
          <Button
            variant="secondary"
            onClick={stopFederatedLearning}
            disabled={flStatus.status === 'idle'}
          >
            <Pause size={20} />
            Pause
          </Button>
          <Button
            variant="danger"
            onClick={stopFederatedLearning}
            disabled={flStatus.status === 'idle'}
          >
            <Square size={20} />
            Stop
          </Button>
        </ControlPanel>
      </Header>

      <StatusCard>
        <StatusGrid>
          <StatusItem>
            <StatusValue>{flStatus.round}</StatusValue>
            <StatusLabel>Current Round</StatusLabel>
          </StatusItem>
          <StatusItem>
            <StatusValue>{flStatus.totalRounds}</StatusValue>
            <StatusLabel>Total Rounds</StatusLabel>
          </StatusItem>
          <StatusItem>
            <StatusValue>{flStatus.accuracy.toFixed(1)}%</StatusValue>
            <StatusLabel>Global Accuracy</StatusLabel>
          </StatusItem>
          <StatusItem>
            <StatusValue>{flStatus.clients.length}</StatusValue>
            <StatusLabel>Active Clients</StatusLabel>
          </StatusItem>
        </StatusGrid>

        {flStatus.totalRounds > 0 && (
          <ProgressBar>
            <ProgressFill 
              progress={flStatus.round} 
              total={flStatus.totalRounds} 
            />
          </ProgressBar>
        )}

        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: '0.5rem',
          marginTop: '1rem',
          fontSize: '0.875rem',
          color: '#64748b'
        }}>
          Status: {flStatus.status}
          {getStatusIcon(flStatus.status)}
        </div>
      </StatusCard>

      <ClientsSection>
        {['client_1', 'client_2', 'client_3'].map(clientId => (
          <ClientCard key={clientId}>
            <ClientHeader>
              <ClientName>{clientId.replace('_', ' ').toUpperCase()}</ClientName>
              <ClientStatus status={getClientStatus(clientId)}>
                {getStatusIcon(getClientStatus(clientId))}
                {getClientStatus(clientId)}
              </ClientStatus>
            </ClientHeader>
            <ClientMetrics>
              <Metric>
                <MetricValue>{getClientAccuracy(clientId).toFixed(1)}%</MetricValue>
                <MetricLabel>Accuracy</MetricLabel>
              </Metric>
              <Metric>
                <MetricValue>{getClientSamples(clientId)}</MetricValue>
                <MetricLabel>Samples</MetricLabel>
              </Metric>
            </ClientMetrics>
          </ClientCard>
        ))}
      </ClientsSection>

      {roundHistory.length > 0 && (
        <ChartCard>
          <ChartTitle>Accuracy Progression</ChartTitle>
          <Line data={accuracyChartData} options={accuracyChartOptions} />
        </ChartCard>
      )}
    </FLContainer>
  );
}

export default FederatedLearning;
