import React, { useState, useMemo } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tabs,
  Tab,
  Chip,
  TextField,
  InputAdornment,
} from '@mui/material';

interface PreviewData {
  columns: string[];
  data: {
    faults: any[];
    manual_interventions: any[];
    warnings: any[];
  };
  total_rows: {
    faults: number;
    manual_interventions: number;
    warnings: number;
  };
  usage_stats: {
    fault_bits: { total: number; used: number; spare: number; spare_percentage: number };
    manual_intervention_bits: { total: number; used: number; spare: number; spare_percentage: number };
    warning_bits: { total: number; used: number; spare: number; spare_percentage: number };
  };
}

interface FilePreviewProps {
  previewData: { [cpu: string]: PreviewData };
  selectedCPU: string;
  onCPUChange: (cpu: string) => void;
}

export const FilePreview: React.FC<FilePreviewProps> = ({
  previewData,
  selectedCPU,
  onCPUChange,
}) => {
  const [selectedSection, setSelectedSection] = useState('faults');
  const [searchTerm, setSearchTerm] = useState('');

  // Get current data safely
  const currentData = previewData?.[selectedCPU];
  
  // Get data for current section safely
  const sectionData = currentData?.data?.[selectedSection as keyof typeof currentData.data] || [];

  // Filter data based on search term - this must be before any conditional returns
  const filteredData = useMemo(() => {
    if (!searchTerm) return sectionData;
    
    return sectionData.filter(row => 
      Object.values(row).some(value => 
        String(value).toLowerCase().includes(searchTerm.toLowerCase())
      )
    );
  }, [sectionData, searchTerm]);

  // Early return after all hooks
  if (!previewData || Object.keys(previewData).length === 0 || !currentData) {
    return null;
  }

  const UsageStats = ({ stats, title }: { stats: any; title: string }) => (
    <Box sx={{ mb: 2 }}>
      <Typography variant="subtitle2" gutterBottom>
        {title}
      </Typography>
      <Box sx={{ display: 'flex', gap: 3 }}>
        <Typography variant="body2">
          Total: {stats.total}
        </Typography>
        <Typography variant="body2">
          Used: {stats.used}
        </Typography>
        <Typography variant="body2">
          Spare: {stats.spare}
        </Typography>
        <Typography variant="body2">
          Spare %: {stats.spare_percentage.toFixed(1)}%
        </Typography>
      </Box>
    </Box>
  );

  const sections = [
    { key: 'faults', label: 'Faults', total: currentData.total_rows.faults },
    { key: 'manual_interventions', label: 'Manual Interventions', total: currentData.total_rows.manual_interventions },
    { key: 'warnings', label: 'Warnings', total: currentData.total_rows.warnings }
  ];

  const currentSection = sections.find(s => s.key === selectedSection);

  return (
    <Paper elevation={3} sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        File Preview
      </Typography>

      <Tabs
        value={selectedCPU}
        onChange={(_: React.SyntheticEvent, value: string) => onCPUChange(value)}
        sx={{ mb: 3 }}
      >
        {Object.keys(previewData).map(cpu => (
          <Tab key={cpu} label={cpu} value={cpu} />
        ))}
      </Tabs>

      <Box sx={{ mb: 3 }}>
        <UsageStats
          stats={currentData.usage_stats.fault_bits}
          title="Fault Bits"
        />
        <UsageStats
          stats={currentData.usage_stats.manual_intervention_bits}
          title="Manual Intervention Bits"
        />
        <UsageStats
          stats={currentData.usage_stats.warning_bits}
          title="Warning Bits"
        />
      </Box>

      <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Tabs
          value={selectedSection}
          onChange={(_: React.SyntheticEvent, value: string) => setSelectedSection(value)}
        >
          {sections.map(section => (
            <Tab 
              key={section.key} 
              label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  {section.label}
                  <Chip 
                    label={section.total} 
                    size="small" 
                    variant="outlined"
                    sx={{ fontSize: '0.75rem', height: 20 }}
                  />
                </Box>
              } 
              value={section.key} 
            />
          ))}
        </Tabs>

        <TextField
          size="small"
          placeholder="Search in data..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          sx={{ width: 300 }}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                {searchTerm && (
                  <Chip 
                    label={`${filteredData.length} results`} 
                    size="small" 
                    variant="outlined"
                  />
                )}
              </InputAdornment>
            ),
          }}
        />
      </Box>

      <TableContainer sx={{ maxHeight: 600 }}>
        <Table stickyHeader size="small">
          <TableHead>
            <TableRow>
              {currentData.columns.map(column => (
                <TableCell key={column}>{column}</TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredData.map((row, index) => (
              <TableRow key={index}>
                {currentData.columns.map(column => (
                  <TableCell key={column}>{row[column]}</TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Box sx={{ mt: 2 }}>
        <Typography variant="body2" color="text.secondary">
          Showing {filteredData.length} of {currentSection?.total || 0} rows
          {searchTerm && ` (filtered from ${sectionData.length})`}
        </Typography>
      </Box>
    </Paper>
  );
};