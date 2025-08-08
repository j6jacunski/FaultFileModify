import React from 'react';
import { useDropzone } from 'react-dropzone';
import { Box, Paper, Typography, Button } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
}

export const FileUpload: React.FC<FileUploadProps> = ({ onFileSelect }) => {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel.sheet.macroEnabled.12': ['.xlsm']
    },
    multiple: false,
    onDrop: (files: File[]) => {
      if (files.length > 0) {
        onFileSelect(files[0]);
      }
    }
  });

  return (
    <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
      <Box
        {...getRootProps()}
        sx={{
          border: '2px dashed',
          borderColor: isDragActive ? 'primary.main' : 'grey.300',
          borderRadius: 1,
          p: 3,
          textAlign: 'center',
          cursor: 'pointer',
          '&:hover': {
            borderColor: 'primary.main',
            bgcolor: 'grey.50'
          }
        }}
      >
        <input {...getInputProps()} />
        <CloudUploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
        <Typography variant="h6" gutterBottom>
          Drag & Drop Excel File
        </Typography>
        <Typography variant="body2" color="textSecondary">
          or click to select file
        </Typography>
        <Typography variant="caption" display="block" color="textSecondary" sx={{ mt: 1 }}>
          Supported formats: .xlsx, .xlsm
        </Typography>
      </Box>
    </Paper>
  );
};