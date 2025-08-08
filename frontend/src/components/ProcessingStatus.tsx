import React from 'react';
import {
  Box,
  Paper,
  Typography,
  CircularProgress,
  Button,
  Alert,
} from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';

interface ProcessingStatusProps {
  isProcessing: boolean;
  error?: string;
  downloadUrls?: { [cpu: string]: string };
  zipFileUrl?: string;
  progressData?: any;
  onDownload: (cpu: string) => void;
  onDownloadAll: () => void;
}

export const ProcessingStatus: React.FC<ProcessingStatusProps> = ({
  isProcessing,
  error,
  downloadUrls,
  zipFileUrl,
  progressData,
  onDownload,
  onDownloadAll,
}) => {
  if (!isProcessing && !error && !downloadUrls) {
    return null;
  }

  return (
    <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
      {isProcessing && (
        <Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <CircularProgress size={24} />
            <Typography variant="h6">Processing Excel file...</Typography>
          </Box>
          
          {progressData && (
            <Box sx={{ ml: 4 }}>
              {/* Progress Bar */}
              <Box sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2" color="text.secondary">
                    {progressData.current_step}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {progressData.progress} / {progressData.total_steps}
                  </Typography>
                </Box>
                <Box sx={{ width: '100%', bgcolor: 'grey.200', borderRadius: 1, overflow: 'hidden' }}>
                  <Box
                    sx={{
                      width: `${(progressData.progress / progressData.total_steps) * 100}%`,
                      height: 8,
                      bgcolor: 'primary.main',
                      transition: 'width 0.3s ease-in-out'
                    }}
                  />
                </Box>
              </Box>
              
              {/* Current CPU being processed */}
              {progressData.current_cpu && (
                <Typography variant="body2" color="primary" sx={{ mb: 1 }}>
                  Currently processing: <strong>{progressData.current_cpu}</strong>
                </Typography>
              )}
              
              {/* Completed CPUs */}
              {progressData.completed_cpus && progressData.completed_cpus.length > 0 && (
                <Box sx={{ mb: 1 }}>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                    Completed: {progressData.completed_cpus.join(', ')}
                  </Typography>
                </Box>
              )}
              
              {/* Estimated time remaining */}
              {progressData.progress > 0 && progressData.progress < progressData.total_steps && (
                <Typography variant="caption" color="text.secondary">
                  Estimated time remaining: {Math.ceil((progressData.total_steps - progressData.progress) * 0.5)} seconds
                </Typography>
              )}
            </Box>
          )}
        </Box>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {downloadUrls && Object.keys(downloadUrls).length > 0 && (
        <Box>
          <Typography variant="h6" gutterBottom>
            Processed Files
          </Typography>
          
          {/* Download All Button */}
          {zipFileUrl && Object.keys(downloadUrls).length > 1 && (
            <Box sx={{ mb: 2 }}>
              <Button
                variant="contained"
                color="primary"
                startIcon={<DownloadIcon />}
                onClick={onDownloadAll}
                sx={{ mb: 2 }}
              >
                Download All Files (ZIP)
              </Button>
            </Box>
          )}
          
          {/* Individual Download Buttons */}
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {Object.entries(downloadUrls).map(([cpu, url]) => (
              <Button
                key={cpu}
                variant="outlined"
                startIcon={<DownloadIcon />}
                onClick={() => onDownload(cpu)}
              >
                {cpu}
              </Button>
            ))}
          </Box>
        </Box>
      )}
    </Paper>
  );
};