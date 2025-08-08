import React from 'react';
import {
  Box,
  Paper,
  FormGroup,
  FormControlLabel,
  Checkbox,
  Typography,
  Button,
} from '@mui/material';

interface CPUSelectionProps {
  availableCPUs: string[];
  selectedCPUs: string[];
  onSelectionChange: (selected: string[]) => void;
}

export const CPUSelection: React.FC<CPUSelectionProps> = ({
  availableCPUs,
  selectedCPUs,
  onSelectionChange,
}) => {
  const handleSelectAll = () => {
    onSelectionChange(availableCPUs);
  };

  const handleSelectNone = () => {
    onSelectionChange([]);
  };

  const handleToggleCPU = (cpu: string) => {
    const newSelection = selectedCPUs.includes(cpu)
      ? selectedCPUs.filter(selected => selected !== cpu)
      : [...selectedCPUs, cpu];
    onSelectionChange(newSelection);
  };

  return (
    <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h6">Select CPUs to Process</Typography>
        <Box>
          <Button
            size="small"
            onClick={handleSelectAll}
            sx={{ mr: 1 }}
          >
            Select All
          </Button>
          <Button
            size="small"
            onClick={handleSelectNone}
          >
            Clear
          </Button>
        </Box>
      </Box>
      <FormGroup sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(120px, 1fr))', gap: 1 }}>
        {availableCPUs.map(cpu => (
          <FormControlLabel
            key={cpu}
            control={
              <Checkbox
                checked={selectedCPUs.includes(cpu)}
                onChange={() => handleToggleCPU(cpu)}
              />
            }
            label={cpu}
          />
        ))}
      </FormGroup>
    </Paper>
  );
};