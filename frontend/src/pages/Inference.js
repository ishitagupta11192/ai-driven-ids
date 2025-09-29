import React, { useState, useCallback } from 'react';
import styled from 'styled-components';
import { useDropzone } from 'react-dropzone';
import { 
  Upload, 
  FileText, 
  Brain, 
  AlertTriangle, 
  CheckCircle,
  Download,
  Trash2,
  Play
} from 'lucide-react';
import { toast } from 'react-toastify';

const InferenceContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
`;

const Header = styled.div`
  margin-bottom: ${props => props.theme.spacing.xl};
`;

const Title = styled.h1`
  font-size: 2rem;
  font-weight: 700;
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.sm};
`;

const Subtitle = styled.p`
  color: ${props => props.theme.colors.textSecondary};
  font-size: 1.125rem;
`;

const UploadSection = styled.div`
  background: ${props => props.theme.colors.surface};
  border: 2px dashed ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius};
  padding: ${props => props.theme.spacing.xxl};
  text-align: center;
  margin-bottom: ${props => props.theme.spacing.xl};
  transition: all 0.2s ease;
  cursor: pointer;

  &:hover {
    border-color: ${props => props.theme.colors.primary};
    background-color: ${props => props.theme.colors.primary}05;
  }

  &.drag-active {
    border-color: ${props => props.theme.colors.primary};
    background-color: ${props => props.theme.colors.primary}10;
  }
`;

const UploadIcon = styled.div`
  width: 64px;
  height: 64px;
  margin: 0 auto ${props => props.theme.spacing.lg};
  color: ${props => props.theme.colors.primary};
`;

const UploadText = styled.div`
  font-size: 1.125rem;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.sm};
`;

const UploadSubtext = styled.div`
  color: ${props => props.theme.colors.textSecondary};
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const FileInput = styled.input`
  display: none;
`;

const Button = styled.button`
  display: inline-flex;
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
          background-color: ${props.theme.colors.surface};
          color: ${props.theme.colors.text};
          border: 1px solid ${props.theme.colors.border};
          &:hover {
            background-color: ${props.theme.colors.background};
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

const ResultsSection = styled.div`
  background: ${props => props.theme.colors.surface};
  border-radius: ${props => props.theme.borderRadius};
  box-shadow: ${props => props.theme.shadows.md};
  border: 1px solid ${props => props.theme.colors.border};
  overflow: hidden;
`;

const ResultsHeader = styled.div`
  padding: ${props => props.theme.spacing.lg};
  border-bottom: 1px solid ${props => props.theme.colors.border};
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const ResultsTitle = styled.h3`
  font-size: 1.25rem;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
`;

const ResultsStats = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.lg};
  font-size: 0.875rem;
  color: ${props => props.theme.colors.textSecondary};
`;

const ResultsTable = styled.div`
  overflow-x: auto;
`;

const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
`;

const TableHeader = styled.thead`
  background-color: ${props => props.theme.colors.background};
`;

const TableRow = styled.tr`
  border-bottom: 1px solid ${props => props.theme.colors.border};
  
  &:hover {
    background-color: ${props => props.theme.colors.background};
  }
`;

const TableHeaderCell = styled.th`
  padding: ${props => props.theme.spacing.md};
  text-align: left;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
`;

const TableCell = styled.td`
  padding: ${props => props.theme.spacing.md};
  color: ${props => props.theme.colors.text};
`;

const PredictionBadge = styled.span`
  display: inline-flex;
  align-items: center;
  gap: ${props => props.theme.spacing.xs};
  padding: ${props => props.theme.spacing.xs} ${props => props.theme.spacing.sm};
  border-radius: ${props => props.theme.borderRadius};
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  
  ${props => {
    switch (props.type) {
      case 'normal':
        return `
          background-color: ${props.theme.colors.success}20;
          color: ${props.theme.colors.success};
        `;
      case 'dos':
        return `
          background-color: ${props.theme.colors.error}20;
          color: ${props.theme.colors.error};
        `;
      case 'probe':
        return `
          background-color: ${props.theme.colors.warning}20;
          color: ${props.theme.colors.warning};
        `;
      case 'r2l':
        return `
          background-color: #8b5cf620;
          color: #8b5cf6;
        `;
      case 'u2r':
        return `
          background-color: #ec489920;
          color: #ec4899;
        `;
      default:
        return `
          background-color: ${props.theme.colors.textSecondary}20;
          color: ${props.theme.colors.textSecondary};
        `;
    }
  }}
`;

const ConfidenceBar = styled.div`
  width: 100%;
  height: 8px;
  background-color: ${props => props.theme.colors.border};
  border-radius: 4px;
  overflow: hidden;
`;

const ConfidenceFill = styled.div`
  height: 100%;
  background: linear-gradient(90deg, ${props => props.theme.colors.error}, ${props => props.theme.colors.warning}, ${props => props.theme.colors.success});
  width: ${props => props.confidence * 100}%;
  transition: width 0.3s ease;
`;

const LoadingSpinner = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  padding: ${props => props.theme.spacing.xxl};
  color: ${props => props.theme.colors.textSecondary};
`;

function Inference() {
  const [uploadedFile, setUploadedFile] = useState(null);
  const [results, setResults] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file) {
      setUploadedFile(file);
      setResults(null);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.ms-excel': ['.csv']
    },
    multiple: false
  });

  const processFile = async () => {
    if (!uploadedFile) return;

    setIsProcessing(true);
    try {
      const formData = new FormData();
      formData.append('file', uploadedFile);

      const response = await fetch('/api/upload-csv', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setResults(data);
        toast.success('File processed successfully!');
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Failed to process file');
      }
    } catch (error) {
      toast.error('Error processing file');
      console.error('Error:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const clearResults = () => {
    setResults(null);
    setUploadedFile(null);
  };

  const downloadResults = () => {
    if (!results) return;

    const csvContent = [
      ['Sample', 'Prediction', 'Confidence', 'Timestamp'],
      ...results.results.map((result, index) => [
        index + 1,
        result.prediction,
        (result.confidence * 100).toFixed(2) + '%',
        result.timestamp || new Date().toISOString()
      ])
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'inference_results.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const getPredictionIcon = (prediction) => {
    switch (prediction) {
      case 'normal':
        return <CheckCircle size={12} />;
      case 'dos':
      case 'probe':
      case 'r2l':
      case 'u2r':
        return <AlertTriangle size={12} />;
      default:
        return <Brain size={12} />;
    }
  };

  return (
    <InferenceContainer>
      <Header>
        <Title>Network Flow Inference</Title>
        <Subtitle>
          Upload CSV files containing network flow data for real-time intrusion detection
        </Subtitle>
      </Header>

      <UploadSection
        {...getRootProps()}
        className={isDragActive ? 'drag-active' : ''}
      >
        <input {...getInputProps()} />
        <UploadIcon>
          <Upload size={64} />
        </UploadIcon>
        <UploadText>
          {isDragActive ? 'Drop the CSV file here' : 'Drag & drop a CSV file here'}
        </UploadText>
        <UploadSubtext>
          or click to select a file
        </UploadSubtext>
        <Button variant="secondary">
          <FileText size={20} />
          Choose File
        </Button>
      </UploadSection>

      {uploadedFile && (
        <div style={{ 
          display: 'flex', 
          gap: '1rem', 
          marginBottom: '2rem',
          alignItems: 'center'
        }}>
          <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: '0.5rem',
            flex: 1,
            padding: '1rem',
            backgroundColor: '#f8fafc',
            borderRadius: '0.5rem',
            border: '1px solid #e2e8f0'
          }}>
            <FileText size={20} color="#64748b" />
            <span style={{ fontWeight: '500' }}>{uploadedFile.name}</span>
            <span style={{ color: '#64748b', fontSize: '0.875rem' }}>
              ({(uploadedFile.size / 1024).toFixed(1)} KB)
            </span>
          </div>
          <Button
            variant="primary"
            onClick={processFile}
            disabled={isProcessing}
          >
            <Play size={20} />
            {isProcessing ? 'Processing...' : 'Process'}
          </Button>
          <Button
            variant="secondary"
            onClick={clearResults}
          >
            <Trash2 size={20} />
            Clear
          </Button>
        </div>
      )}

      {isProcessing && (
        <LoadingSpinner>
          <Brain size={32} className="animate-spin" />
          <span style={{ marginLeft: '1rem' }}>Processing network flow data...</span>
        </LoadingSpinner>
      )}

      {results && (
        <ResultsSection>
          <ResultsHeader>
            <ResultsTitle>Inference Results</ResultsTitle>
            <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
              <ResultsStats>
                <span>Total: {results.total_samples}</span>
                <span>Attacks: {results.attack_samples}</span>
                <span>Normal: {results.normal_samples}</span>
                <span>Attack Rate: {(results.attack_rate * 100).toFixed(1)}%</span>
              </ResultsStats>
              <Button variant="secondary" onClick={downloadResults}>
                <Download size={20} />
                Download
              </Button>
            </div>
          </ResultsHeader>

          <ResultsTable>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHeaderCell>Sample</TableHeaderCell>
                  <TableHeaderCell>Prediction</TableHeaderCell>
                  <TableHeaderCell>Confidence</TableHeaderCell>
                  <TableHeaderCell>Duration</TableHeaderCell>
                  <TableHeaderCell>Protocol</TableHeaderCell>
                  <TableHeaderCell>Service</TableHeaderCell>
                </TableRow>
              </TableHeader>
              <tbody>
                {results.results.slice(0, 50).map((result, index) => (
                  <TableRow key={index}>
                    <TableCell>{index + 1}</TableCell>
                    <TableCell>
                      <PredictionBadge type={result.prediction}>
                        {getPredictionIcon(result.prediction)}
                        {result.prediction}
                      </PredictionBadge>
                    </TableCell>
                    <TableCell>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <ConfidenceBar>
                          <ConfidenceFill confidence={result.confidence} />
                        </ConfidenceBar>
                        <span style={{ fontSize: '0.875rem', minWidth: '3rem' }}>
                          {(result.confidence * 100).toFixed(1)}%
                        </span>
                      </div>
                    </TableCell>
                    <TableCell>{result.duration?.toFixed(2) || 'N/A'}</TableCell>
                    <TableCell>{result.protocol_type || 'N/A'}</TableCell>
                    <TableCell>{result.service || 'N/A'}</TableCell>
                  </TableRow>
                ))}
              </tbody>
            </Table>
          </ResultsTable>

          {results.results.length > 50 && (
            <div style={{ 
              padding: '1rem', 
              textAlign: 'center', 
              color: '#64748b',
              borderTop: '1px solid #e2e8f0'
            }}>
              Showing first 50 results of {results.results.length} total
            </div>
          )}
        </ResultsSection>
      )}
    </InferenceContainer>
  );
}

export default Inference;
