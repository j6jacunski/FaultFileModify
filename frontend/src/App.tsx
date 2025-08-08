import React, { useState } from 'react';
import { Container, CssBaseline, ThemeProvider, createTheme, Button } from '@mui/material';
import { FileUpload } from './components/FileUpload';
import { CPUSelection } from './components/CPUSelection';
import { ProcessingStatus } from './components/ProcessingStatus';
import { FilePreview } from './components/FilePreview';
import { uploadFile, getAvailableCPUs, processFile, getPreview, getProgress } from './services/api';

const theme = createTheme({
  palette: {
    mode: 'light',
  },
});

function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [availableCPUs, setAvailableCPUs] = useState<string[]>([]);
  const [selectedCPUs, setSelectedCPUs] = useState<string[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | undefined>();
  const [downloadUrls, setDownloadUrls] = useState<{ [cpu: string]: string }>();
  const [zipFileUrl, setZipFileUrl] = useState<string>('');
  const [previewData, setPreviewData] = useState<any>({});
  const [selectedPreviewCPU, setSelectedPreviewCPU] = useState<string>('');
  const [progressData, setProgressData] = useState<any>(null);
  const [currentJobId, setCurrentJobId] = useState<string>('');

  const handleFileSelect = async (file: File) => {
    setSelectedFile(file);
    setError(undefined);
    setDownloadUrls(undefined);
    setZipFileUrl('');
    setProgressData(null);
    setCurrentJobId('');

    // Upload file and get available CPUs
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const uploadResponse = await uploadFile(file);
      const cpus = await getAvailableCPUs(uploadResponse.filename);
      setAvailableCPUs(cpus);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload file');
    }
  };

  const handleProcess = async () => {
    if (!selectedFile || selectedCPUs.length === 0) return;

    setIsProcessing(true);
    setError(undefined);
    setDownloadUrls(undefined);
    setZipFileUrl('');
    setProgressData(null);
    setCurrentJobId('');

    try {
      const response = await processFile(selectedFile.name, selectedCPUs);
      
      // Store job ID and start progress tracking
      setCurrentJobId(response.job_id);
      
      // Poll for progress updates
      const pollProgress = async () => {
        try {
          const progress = await getProgress(response.job_id);
          setProgressData(progress);
          
          if (progress.status === 'completed') {
            // Processing completed, get final results
            setDownloadUrls(response.individual_files);
            setZipFileUrl(response.zip_file);
            
            // Get preview data for processed files
            const previews: { [cpu: string]: any } = {};
            for (const cpu of selectedCPUs) {
              const previewData = await getPreview(selectedFile.name, cpu);
              previews[cpu] = previewData;
            }
            setPreviewData(previews);
            setSelectedPreviewCPU(selectedCPUs[0]);
            setIsProcessing(false);
          } else if (progress.status === 'error') {
            setError(progress.error || 'An error occurred during processing');
            setIsProcessing(false);
          } else {
            // Continue polling
            setTimeout(pollProgress, 500);
          }
        } catch (err) {
          setError(err instanceof Error ? err.message : 'Failed to get progress');
          setIsProcessing(false);
        }
      };
      
      // Start polling
      pollProgress();
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      setIsProcessing(false);
    }
  };

  const handleDownload = (cpu: string) => {
    if (downloadUrls && downloadUrls[cpu]) {
      // Create a download link and trigger it
      const link = document.createElement('a');
      const filename = downloadUrls[cpu]; // Backend now returns just the filename
      link.href = `/download/${filename}`;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const handleDownloadAll = () => {
    if (zipFileUrl) {
      // Create a download link and trigger it
      const link = document.createElement('a');
      link.href = `/download/${zipFileUrl}`;
      link.download = zipFileUrl;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <FileUpload onFileSelect={handleFileSelect} />
        
        {availableCPUs.length > 0 && (
          <>
            <CPUSelection
              availableCPUs={availableCPUs}
              selectedCPUs={selectedCPUs}
              onSelectionChange={setSelectedCPUs}
            />
            <Button
              variant="contained"
              color="primary"
              disabled={selectedCPUs.length === 0 || isProcessing}
              onClick={handleProcess}
              sx={{ mb: 3 }}
            >
              Process Selected CPUs
            </Button>
          </>
        )}

        <ProcessingStatus
          isProcessing={isProcessing}
          error={error}
          downloadUrls={downloadUrls}
          zipFileUrl={zipFileUrl}
          progressData={progressData}
          onDownload={handleDownload}
          onDownloadAll={handleDownloadAll}
        />

        {Object.keys(previewData).length > 0 && (
                  <FilePreview
          previewData={previewData}
          selectedCPU={selectedPreviewCPU}
          onCPUChange={setSelectedPreviewCPU}
        />
        )}
      </Container>
    </ThemeProvider>
  );
}

export default App;