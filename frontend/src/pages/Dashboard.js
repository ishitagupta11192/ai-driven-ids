import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { 
  Activity, 
  Shield, 
  AlertTriangle, 
  TrendingUp,
  Users,
  Clock,
  Brain,
  Network
} from 'lucide-react';
import { Line, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const DashboardContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
`;

const WelcomeSection = styled.div`
  background: linear-gradient(135deg, ${props => props.theme.colors.primary} 0%, ${props => props.theme.colors.secondary} 100%);
  color: white;
  padding: ${props => props.theme.spacing.xxl};
  border-radius: ${props => props.theme.borderRadius};
  margin-bottom: ${props => props.theme.spacing.xl};
  box-shadow: ${props => props.theme.shadows.lg};
`;

const WelcomeTitle = styled.h1`
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: ${props => props.theme.spacing.sm};
`;

const WelcomeSubtitle = styled.p`
  font-size: 1.125rem;
  opacity: 0.9;
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const StatusGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: ${props => props.theme.spacing.lg};
  margin-bottom: ${props => props.theme.spacing.xl};
`;

const StatusCard = styled.div`
  background: ${props => props.theme.colors.surface};
  padding: ${props => props.theme.spacing.xl};
  border-radius: ${props => props.theme.borderRadius};
  box-shadow: ${props => props.theme.shadows.md};
  border: 1px solid ${props => props.theme.colors.border};
  transition: transform 0.2s ease, box-shadow 0.2s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: ${props => props.theme.shadows.lg};
  }
`;

const StatusCardHeader = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.md};
  margin-bottom: ${props => props.theme.spacing.md};
`;

const StatusIcon = styled.div`
  width: 48px;
  height: 48px;
  border-radius: ${props => props.theme.borderRadius};
  background-color: ${props => props.color}20;
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${props => props.color};
`;

const StatusInfo = styled.div`
  flex: 1;
`;

const StatusTitle = styled.h3`
  font-size: 0.875rem;
  font-weight: 600;
  color: ${props => props.theme.colors.textSecondary};
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: ${props => props.theme.spacing.xs};
`;

const StatusValue = styled.div`
  font-size: 2rem;
  font-weight: 700;
  color: ${props => props.theme.colors.text};
`;

const StatusChange = styled.div`
  font-size: 0.875rem;
  color: ${props => props.positive ? props.theme.colors.success : props.theme.colors.error};
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.xs};
  margin-top: ${props => props.theme.spacing.sm};
`;

const ChartsSection = styled.div`
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: ${props => props.theme.spacing.xl};
  margin-bottom: ${props => props.theme.spacing.xl};

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
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

const RecentActivity = styled.div`
  background: ${props => props.theme.colors.surface};
  padding: ${props => props.theme.spacing.xl};
  border-radius: ${props => props.theme.borderRadius};
  box-shadow: ${props => props.theme.shadows.md};
  border: 1px solid ${props => props.theme.colors.border};
`;

const ActivityItem = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.md};
  padding: ${props => props.theme.spacing.md} 0;
  border-bottom: 1px solid ${props => props.theme.colors.border};

  &:last-child {
    border-bottom: none;
  }
`;

const ActivityIcon = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: ${props => props.color}20;
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${props => props.color};
`;

const ActivityContent = styled.div`
  flex: 1;
`;

const ActivityTitle = styled.div`
  font-weight: 600;
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.xs};
`;

const ActivityTime = styled.div`
  font-size: 0.875rem;
  color: ${props => props.theme.colors.textSecondary};
`;

function Dashboard({ modelStatus, flProgress }) {
  const [recentAlerts, setRecentAlerts] = useState([]);
  const [detectionStats, setDetectionStats] = useState({
    total: 0,
    attacks: 0,
    normal: 0,
    accuracy: 0
  });

  useEffect(() => {
    // Simulate recent alerts
    const alerts = [
      { type: 'attack', message: 'DoS attack detected', time: '2 minutes ago', severity: 'high' },
      { type: 'normal', message: 'Normal traffic flow', time: '5 minutes ago', severity: 'low' },
      { type: 'attack', message: 'Probe attempt detected', time: '8 minutes ago', severity: 'medium' },
      { type: 'normal', message: 'Regular HTTP request', time: '12 minutes ago', severity: 'low' },
      { type: 'attack', message: 'Privilege escalation attempt', time: '15 minutes ago', severity: 'high' },
    ];
    setRecentAlerts(alerts);

    // Simulate detection stats
    setDetectionStats({
      total: 1247,
      attacks: 89,
      normal: 1158,
      accuracy: modelStatus.accuracy || 94.2
    });
  }, [modelStatus.accuracy]);

  // Chart data for detection trends
  const detectionTrendData = {
    labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
    datasets: [
      {
        label: 'Normal Traffic',
        data: [120, 95, 150, 180, 200, 160],
        borderColor: '#10b981',
        backgroundColor: '#10b98120',
        tension: 0.4,
      },
      {
        label: 'Attack Traffic',
        data: [5, 3, 8, 12, 15, 9],
        borderColor: '#ef4444',
        backgroundColor: '#ef444420',
        tension: 0.4,
      },
    ],
  };

  const detectionTrendOptions = {
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
      },
    },
  };

  // Chart data for attack types
  const attackTypesData = {
    labels: ['Normal', 'DoS', 'Probe', 'R2L', 'U2R'],
    datasets: [
      {
        data: [1158, 45, 28, 12, 4],
        backgroundColor: [
          '#10b981',
          '#ef4444',
          '#f59e0b',
          '#8b5cf6',
          '#ec4899',
        ],
        borderWidth: 0,
      },
    ],
  };

  const attackTypesOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'bottom',
      },
    },
  };

  const getActivityIcon = (type) => {
    switch (type) {
      case 'attack':
        return <AlertTriangle size={20} />;
      case 'normal':
        return <Shield size={20} />;
      default:
        return <Activity size={20} />;
    }
  };

  const getActivityColor = (severity) => {
    switch (severity) {
      case 'high':
        return '#ef4444';
      case 'medium':
        return '#f59e0b';
      case 'low':
        return '#10b981';
      default:
        return '#64748b';
    }
  };

  return (
    <DashboardContainer>
      <WelcomeSection>
        <WelcomeTitle>AI-Driven IDS Dashboard</WelcomeTitle>
        <WelcomeSubtitle>
          Real-time network intrusion detection with hybrid deep learning and federated learning
        </WelcomeSubtitle>
      </WelcomeSection>

      <StatusGrid>
        <StatusCard>
          <StatusCardHeader>
            <StatusIcon color="#10b981">
              <Shield size={24} />
            </StatusIcon>
            <StatusInfo>
              <StatusTitle>Model Status</StatusTitle>
              <StatusValue>
                {modelStatus.loaded ? 'Active' : 'Offline'}
              </StatusValue>
            </StatusInfo>
          </StatusCardHeader>
          <StatusChange positive={modelStatus.loaded}>
            <TrendingUp size={16} />
            {modelStatus.accuracy.toFixed(1)}% accuracy
          </StatusChange>
        </StatusCard>

        <StatusCard>
          <StatusCardHeader>
            <StatusIcon color="#2563eb">
              <Activity size={24} />
            </StatusIcon>
            <StatusInfo>
              <StatusTitle>Total Detections</StatusTitle>
              <StatusValue>{detectionStats.total}</StatusValue>
            </StatusInfo>
          </StatusCardHeader>
          <StatusChange positive>
            <TrendingUp size={16} />
            +12% from yesterday
          </StatusChange>
        </StatusCard>

        <StatusCard>
          <StatusCardHeader>
            <StatusIcon color="#ef4444">
              <AlertTriangle size={24} />
            </StatusIcon>
            <StatusInfo>
              <StatusTitle>Threats Detected</StatusTitle>
              <StatusValue>{detectionStats.attacks}</StatusValue>
            </StatusInfo>
          </StatusCardHeader>
          <StatusChange positive={false}>
            <TrendingUp size={16} />
            {((detectionStats.attacks / detectionStats.total) * 100).toFixed(1)}% of traffic
          </StatusChange>
        </StatusCard>

        <StatusCard>
          <StatusCardHeader>
            <StatusIcon color="#8b5cf6">
              <Network size={24} />
            </StatusIcon>
            <StatusInfo>
              <StatusTitle>FL Status</StatusTitle>
              <StatusValue>
                {flProgress.status === 'idle' ? 'Idle' : 'Active'}
              </StatusValue>
            </StatusInfo>
          </StatusCardHeader>
          <StatusChange positive={flProgress.status !== 'idle'}>
            <Clock size={16} />
            Round {flProgress.round}/{flProgress.totalRounds}
          </StatusChange>
        </StatusCard>
      </StatusGrid>

      <ChartsSection>
        <ChartCard>
          <ChartTitle>Detection Trends (24h)</ChartTitle>
          <Line data={detectionTrendData} options={detectionTrendOptions} />
        </ChartCard>

        <ChartCard>
          <ChartTitle>Traffic Distribution</ChartTitle>
          <Doughnut data={attackTypesData} options={attackTypesOptions} />
        </ChartCard>
      </ChartsSection>

      <RecentActivity>
        <ChartTitle>Recent Activity</ChartTitle>
        {recentAlerts.map((alert, index) => (
          <ActivityItem key={index}>
            <ActivityIcon color={getActivityColor(alert.severity)}>
              {getActivityIcon(alert.type)}
            </ActivityIcon>
            <ActivityContent>
              <ActivityTitle>{alert.message}</ActivityTitle>
              <ActivityTime>{alert.time}</ActivityTime>
            </ActivityContent>
          </ActivityItem>
        ))}
      </RecentActivity>
    </DashboardContainer>
  );
}

export default Dashboard;
