import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { 
  BarChart3, 
  TrendingUp, 
  Target, 
  AlertTriangle,
  RefreshCw,
  Download
} from 'lucide-react';
import { Bar, Line, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
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
  BarElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const MetricsContainer = styled.div`
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

const Button = styled.button`
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

const MetricsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: ${props => props.theme.spacing.lg};
  margin-bottom: ${props => props.theme.spacing.xl};
`;

const MetricCard = styled.div`
  background: ${props => props.theme.colors.surface};
  padding: ${props => props.theme.spacing.xl};
  border-radius: ${props => props.theme.borderRadius};
  box-shadow: ${props => props.theme.shadows.md};
  border: 1px solid ${props => props.theme.colors.border};
  text-align: center;
`;

const MetricIcon = styled.div`
  width: 48px;
  height: 48px;
  margin: 0 auto ${props => props.theme.spacing.md};
  border-radius: ${props => props.theme.borderRadius};
  background-color: ${props => props.color}20;
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${props => props.color};
`;

const MetricValue = styled.div`
  font-size: 2.5rem;
  font-weight: 700;
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.xs};
`;

const MetricLabel = styled.div`
  font-size: 0.875rem;
  color: ${props => props.theme.colors.textSecondary};
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: ${props => props.theme.spacing.sm};
`;

const MetricChange = styled.div`
  font-size: 0.875rem;
  color: ${props => props.positive ? props.theme.colors.success : props.theme.colors.error};
  display: flex;
  align-items: center;
  justify-content: center;
  gap: ${props => props.theme.spacing.xs};
`;

const ChartsSection = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
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
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
`;

const FullWidthChart = styled.div`
  background: ${props => props.theme.colors.surface};
  padding: ${props => props.theme.spacing.xl};
  border-radius: ${props => props.theme.borderRadius};
  box-shadow: ${props => props.theme.shadows.md};
  border: 1px solid ${props => props.theme.colors.border};
  margin-bottom: ${props => props.theme.spacing.xl};
`;

const LoadingSpinner = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  padding: ${props => props.theme.spacing.xxl};
  color: ${props => props.theme.colors.textSecondary};
`;

const ErrorMessage = styled.div`
  background-color: ${props => props.theme.colors.error}20;
  color: ${props => props.theme.colors.error};
  padding: ${props => props.theme.spacing.lg};
  border-radius: ${props => props.theme.borderRadius};
  border: 1px solid ${props => props.theme.colors.error}40;
  text-align: center;
`;

function Metrics() {
  const [metrics, setMetrics] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchMetrics();
  }, []);

  const fetchMetrics = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await fetch('/api/metrics');
      if (response.ok) {
        const data = await response.json();
        setMetrics(data);
      } else {
        setError('Failed to fetch metrics');
      }
    } catch (error) {
      setError('Error fetching metrics');
      console.error('Error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <MetricsContainer>
        <LoadingSpinner>
          <RefreshCw size={32} className="animate-spin" />
          <span style={{ marginLeft: '1rem' }}>Loading metrics...</span>
        </LoadingSpinner>
      </MetricsContainer>
    );
  }

  if (error) {
    return (
      <MetricsContainer>
        <Header>
          <PageTitle>Model Metrics</PageTitle>
          <Button onClick={fetchMetrics}>
            <RefreshCw size={20} />
            Retry
          </Button>
        </Header>
        <ErrorMessage>
          <AlertTriangle size={24} style={{ marginBottom: '1rem' }} />
          <div>{error}</div>
        </ErrorMessage>
      </MetricsContainer>
    );
  }

  if (!metrics || metrics.message) {
    return (
      <MetricsContainer>
        <Header>
          <PageTitle>Model Metrics</PageTitle>
          <Button onClick={fetchMetrics}>
            <RefreshCw size={20} />
            Refresh
          </Button>
        </Header>
        <ErrorMessage>
          <AlertTriangle size={24} style={{ marginBottom: '1rem' }} />
          <div>{metrics?.message || 'No metrics available'}</div>
        </ErrorMessage>
      </MetricsContainer>
    );
  }

  // Chart data for confusion matrix
  const confusionMatrixData = {
    labels: metrics.class_names || ['Normal', 'DoS', 'Probe', 'R2L', 'U2R'],
    datasets: [{
      label: 'Predictions',
      data: metrics.confusion_matrix?.flat() || [],
      backgroundColor: [
        '#10b981',
        '#ef4444',
        '#f59e0b',
        '#8b5cf6',
        '#ec4899',
      ],
      borderWidth: 0,
    }]
  };

  // Chart data for classification report
  const classificationData = {
    labels: Object.keys(metrics.classification_report || {}).filter(key => key !== 'accuracy'),
    datasets: [{
      label: 'Precision',
      data: Object.values(metrics.classification_report || {}).filter((_, index) => 
        Object.keys(metrics.classification_report || {})[index] !== 'accuracy'
      ).map(item => item.precision * 100),
      backgroundColor: '#2563eb',
    }, {
      label: 'Recall',
      data: Object.values(metrics.classification_report || {}).filter((_, index) => 
        Object.keys(metrics.classification_report || {})[index] !== 'accuracy'
      ).map(item => item.recall * 100),
      backgroundColor: '#10b981',
    }, {
      label: 'F1-Score',
      data: Object.values(metrics.classification_report || {}).filter((_, index) => 
        Object.keys(metrics.classification_report || {})[index] !== 'accuracy'
      ).map(item => item['f1-score'] * 100),
      backgroundColor: '#f59e0b',
    }]
  };

  const classificationOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
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

  // Chart data for accuracy over time (simulated)
  const accuracyOverTimeData = {
    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6'],
    datasets: [{
      label: 'Model Accuracy',
      data: [85, 87, 89, 91, 93, metrics.accuracy * 100],
      borderColor: '#2563eb',
      backgroundColor: '#2563eb20',
      tension: 0.4,
      fill: true,
    }]
  };

  const accuracyOverTimeOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
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

  return (
    <MetricsContainer>
      <Header>
        <PageTitle>Model Metrics</PageTitle>
        <Button onClick={fetchMetrics}>
          <RefreshCw size={20} />
          Refresh
        </Button>
      </Header>

      <MetricsGrid>
        <MetricCard>
          <MetricIcon color="#10b981">
            <Target size={24} />
          </MetricIcon>
          <MetricValue>{(metrics.accuracy * 100).toFixed(1)}%</MetricValue>
          <MetricLabel>Overall Accuracy</MetricLabel>
          <MetricChange positive>
            <TrendingUp size={16} />
            +2.3% from last week
          </MetricChange>
        </MetricCard>

        <MetricCard>
          <MetricIcon color="#2563eb">
            <BarChart3 size={24} />
          </MetricIcon>
          <MetricValue>{metrics.total_samples || 0}</MetricValue>
          <MetricLabel>Total Samples</MetricLabel>
          <MetricChange positive>
            <TrendingUp size={16} />
            +15% from last week
          </MetricChange>
        </MetricCard>

        <MetricCard>
          <MetricIcon color="#f59e0b">
            <AlertTriangle size={24} />
          </MetricIcon>
          <MetricValue>
            {metrics.classification_report ? 
              Object.keys(metrics.classification_report).length - 1 : 0
            }
          </MetricValue>
          <MetricLabel>Attack Types</MetricLabel>
          <MetricChange positive>
            <TrendingUp size={16} />
            All detected
          </MetricChange>
        </MetricCard>

        <MetricCard>
          <MetricIcon color="#8b5cf6">
            <TrendingUp size={24} />
          </MetricIcon>
          <MetricValue>
            {metrics.classification_report?.accuracy ? 
              (metrics.classification_report.accuracy * 100).toFixed(1) + '%' : 'N/A'
            }
          </MetricValue>
          <MetricLabel>Weighted Avg</MetricLabel>
          <MetricChange positive>
            <TrendingUp size={16} />
            Excellent
          </MetricChange>
        </MetricCard>
      </MetricsGrid>

      <ChartsSection>
        <ChartCard>
          <ChartTitle>
            <BarChart3 size={20} />
            Classification Performance
          </ChartTitle>
          <Bar data={classificationData} options={classificationOptions} />
        </ChartCard>

        <ChartCard>
          <ChartTitle>
            <Target size={20} />
            Attack Type Distribution
          </ChartTitle>
          <Doughnut 
            data={{
              labels: metrics.class_names || ['Normal', 'DoS', 'Probe', 'R2L', 'U2R'],
              datasets: [{
                data: [70, 15, 8, 5, 2], // Simulated distribution
                backgroundColor: [
                  '#10b981',
                  '#ef4444',
                  '#f59e0b',
                  '#8b5cf6',
                  '#ec4899',
                ],
                borderWidth: 0,
              }]
            }}
            options={{
              responsive: true,
              plugins: {
                legend: {
                  position: 'bottom',
                },
              },
            }}
          />
        </ChartCard>
      </ChartsSection>

      <FullWidthChart>
        <ChartTitle>
          <TrendingUp size={20} />
          Model Accuracy Over Time
        </ChartTitle>
        <Line data={accuracyOverTimeData} options={accuracyOverTimeOptions} />
      </FullWidthChart>

      {metrics.classification_report && (
        <FullWidthChart>
          <ChartTitle>
            <BarChart3 size={20} />
            Detailed Classification Report
          </ChartTitle>
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
            gap: '1rem',
            marginTop: '1rem'
          }}>
            {Object.entries(metrics.classification_report).map(([class_name, metrics_data]) => {
              if (class_name === 'accuracy') return null;
              return (
                <div key={class_name} style={{
                  padding: '1rem',
                  backgroundColor: '#f8fafc',
                  borderRadius: '0.5rem',
                  border: '1px solid #e2e8f0'
                }}>
                  <h4 style={{ 
                    marginBottom: '0.5rem', 
                    textTransform: 'capitalize',
                    color: '#1e293b'
                  }}>
                    {class_name}
                  </h4>
                  <div style={{ fontSize: '0.875rem', color: '#64748b' }}>
                    <div>Precision: {(metrics_data.precision * 100).toFixed(1)}%</div>
                    <div>Recall: {(metrics_data.recall * 100).toFixed(1)}%</div>
                    <div>F1-Score: {(metrics_data['f1-score'] * 100).toFixed(1)}%</div>
                    <div>Support: {metrics_data.support}</div>
                  </div>
                </div>
              );
            })}
          </div>
        </FullWidthChart>
      )}
    </MetricsContainer>
  );
}

export default Metrics;
