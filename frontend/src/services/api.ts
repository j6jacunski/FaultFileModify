import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:49490';

const api = axios.create({
  baseURL: API_BASE_URL,
});

export interface UsageStats {
  total: number;
  used: number;
  spare: number;
  spare_percentage: number;
}

export interface PreviewData {
  columns: string[];
  data: any[];
  total_rows: number;
  usage_stats: {
    fault_bits: UsageStats;
    manual_intervention_bits: UsageStats;
    warning_bits: UsageStats;
  };
}

interface AvailableCPUsResponse {
  cpus: string[];
}

interface ProcessResponse {
  job_id: string;
  individual_files: { [cpu: string]: string };
  zip_file: string;
}

interface ProgressResponse {
  status: 'starting' | 'processing' | 'completed' | 'error';
  current_step: string;
  progress: number;
  total_steps: number;
  current_cpu?: string;
  completed_cpus: string[];
  error?: string;
}

interface SectionDataResponse {
  data: any[];
  total_rows: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

interface HistoryResponse {
  history: Array<{
    filename: string;
    date: string;
    selected_cpus: string[];
    input_location: string;
  }>;
}

export const uploadFile = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post<{ filename: string }>('/upload/', formData);
  return response.data;
};

export const getAvailableCPUs = async (filename: string) => {
  const response = await api.get<AvailableCPUsResponse>(`/available-cpus/${filename}`);
  return response.data.cpus;
};

export const getPreview = async (filename: string, cpu: string) => {
  const response = await api.get<PreviewData>(`/preview/${filename}/${cpu}`);
  return response.data;
};

export const processFile = async (filename: string, selectedCPUs: string[]) => {
  const response = await api.post<ProcessResponse>('/process/', {
    filename,
    selected_cpus: selectedCPUs,
  });
  return response.data;
};

export const getProgress = async (jobId: string) => {
  const response = await api.get<ProgressResponse>(`/progress/${jobId}`);
  return response.data;
};

export const getProcessingHistory = async () => {
  const response = await api.get<HistoryResponse>('/history/');
  return response.data.history;
};