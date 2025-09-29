import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import styled, { ThemeProvider, createGlobalStyle } from 'styled-components';

// Components
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Inference from './pages/Inference';
import FederatedLearning from './pages/FederatedLearning';
import ModelStatus from './pages/ModelStatus';
import Metrics from './pages/Metrics';

// Theme
const theme = {
  colors: {
    primary: '#2563eb',
    secondary: '#64748b',
    success: '#10b981',
    warning: '#f59e0b',
    error: '#ef4444',
    background: '#f8fafc',
    surface: '#ffffff',
    text: '#1e293b',
    textSecondary: '#64748b',
    border: '#e2e8f0',
  },
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem',
    xxl: '3rem',
  },
  borderRadius: '0.5rem',
  shadows: {
    sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
    md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
    lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
  },
};

const GlobalStyle = createGlobalStyle`
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
      'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
      sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    background-color: ${props => props.theme.colors.background};
    color: ${props => props.theme.colors.text};
    line-height: 1.6;
  }

  code {
    font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
      monospace;
  }

  .toast-container {
    font-size: 14px;
  }
`;

const AppContainer = styled.div`
  display: flex;
  min-height: 100vh;
`;

const MainContent = styled.main`
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-left: 250px;
  transition: margin-left 0.3s ease;

  @media (max-width: 768px) {
    margin-left: 0;
  }
`;

const ContentArea = styled.div`
  flex: 1;
  padding: ${props => props.theme.spacing.xl};
  background-color: ${props => props.theme.colors.background};
`;

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [modelStatus, setModelStatus] = useState({
    loaded: false,
    training: false,
    accuracy: 0,
    lastUpdated: null
  });
  const [flProgress, setFlProgress] = useState({
    round: 0,
    totalRounds: 0,
    status: 'idle',
    accuracy: 0
  });

  // Fetch model status on app load
  useEffect(() => {
    fetchModelStatus();
    fetchFlProgress();
    
    // Set up polling for real-time updates
    const interval = setInterval(() => {
      fetchModelStatus();
      fetchFlProgress();
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const fetchModelStatus = async () => {
    try {
      const response = await fetch('/api/model-status');
      if (response.ok) {
        const data = await response.json();
        setModelStatus(data);
      }
    } catch (error) {
      console.error('Error fetching model status:', error);
    }
  };

  const fetchFlProgress = async () => {
    try {
      const response = await fetch('/api/fl-progress');
      if (response.ok) {
        const data = await response.json();
        setFlProgress(data);
      }
    } catch (error) {
      console.error('Error fetching FL progress:', error);
    }
  };

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <ThemeProvider theme={theme}>
      <GlobalStyle />
      <Router>
        <AppContainer>
          <Sidebar 
            isOpen={sidebarOpen} 
            onClose={() => setSidebarOpen(false)}
            modelStatus={modelStatus}
            flProgress={flProgress}
          />
          <MainContent>
            <Header 
              onMenuClick={toggleSidebar}
              modelStatus={modelStatus}
              flProgress={flProgress}
            />
            <ContentArea>
              <Routes>
                <Route path="/" element={<Dashboard modelStatus={modelStatus} flProgress={flProgress} />} />
                <Route path="/inference" element={<Inference />} />
                <Route path="/federated-learning" element={<FederatedLearning onProgressUpdate={setFlProgress} />} />
                <Route path="/model-status" element={<ModelStatus modelStatus={modelStatus} />} />
                <Route path="/metrics" element={<Metrics />} />
              </Routes>
            </ContentArea>
          </MainContent>
        </AppContainer>
        <ToastContainer
          position="top-right"
          autoClose={5000}
          hideProgressBar={false}
          newestOnTop={false}
          closeOnClick
          rtl={false}
          pauseOnFocusLoss
          draggable
          pauseOnHover
        />
      </Router>
    </ThemeProvider>
  );
}

export default App;
