import pandas as pd
from pathlib import Path
import logging
import re
from typing import List, Dict, Any
import zipfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExcelProcessor:
    def __init__(self, input_file: Path):
        """Initialize the Excel processor with input file path."""
        self.input_file = input_file
        self.excel_file = pd.ExcelFile(input_file)
    
    def get_available_cpus(self) -> List[str]:
        """Get list of available CPU tabs in the Excel file."""
        return [sheet for sheet in self.excel_file.sheet_names if sheet.startswith("CPU")]
    
    def calculate_trigger_value(self, tag_name: str) -> int:
        """Calculate trigger value from tag name (e.g., FB1[0].5 -> 6, FB1[53].30 -> 1727)"""
        if not tag_name or pd.isna(tag_name):
            return None
            
        # Extract array number and operand using regex
        match = re.match(r'[FMW]B1\[(\d+)\]\.(\d+)', tag_name)
        if match:
            array_num = int(match.group(1))
            operand = int(match.group(2))
            # Calculate: (array_number * 32) + operand + 1
            return (array_num * 32) + operand + 1
        return None

    def remove_duplicates(self, entries: List[tuple[int, str, str]]) -> List[tuple[int, str, str]]:
        """Remove duplicate entries based on tag names.
        For duplicates:
        - Keep entry with description over entry without description
        - If neither has description, keep only one instance
        """
        # Group entries by tag name
        tag_groups: Dict[str, List[tuple[int, str, str]]] = {}
        for trigger, tag, desc in entries:
            tag_name = tag.split(' ~')[0].strip()
            if tag_name not in tag_groups:
                tag_groups[tag_name] = []
            tag_groups[tag_name].append((trigger, tag, desc))
        
        # Process each group to remove duplicates
        result = []
        for tag_name, group in tag_groups.items():
            if len(group) == 1:
                # No duplicates, keep the entry
                result.append(group[0])
            else:
                # Find entry with description if it exists
                entries_with_desc = [entry for entry in group if entry[2].strip()]
                if entries_with_desc:
                    # Keep the first entry with a description
                    result.append(entries_with_desc[0])
                else:
                    # If no entries have descriptions, keep the first one
                    result.append(group[0])
        
        # Sort by trigger value
        return sorted(result, key=lambda x: x[0])

    def process_section(self, df: pd.DataFrame, start_col: int, tag_col_offset: int = 4, desc_col_offset: int = 6) -> List[tuple[int, str]]:
        """Process a section (FB, MB, or WB) and return tags with trigger values"""
        entries = []
        
        # Get column indices
        tag_col = df.columns[start_col + tag_col_offset]
        desc_col = df.columns[start_col + desc_col_offset]
        
        # Process each row
        for _, row in df.iterrows():
            tag = str(row[tag_col]).strip() if pd.notna(row[tag_col]) else ""
            desc = str(row[desc_col]).strip() if pd.notna(row[desc_col]) else ""
            
            if tag:
                trigger_value = self.calculate_trigger_value(tag)
                if trigger_value is not None:
                    text = f"{tag} ~ {desc}" if desc else f"{tag} ~"
                    entries.append((trigger_value, text, desc))
        
        # Remove duplicates and convert to DataFrame format
        unique_entries = self.remove_duplicates(entries)
        return [(trigger, text) for trigger, text, _ in unique_entries]

    def process_cpu_tab(self, tab_name: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Process a single CPU tab and return formatted DataFrames."""
        try:
            # Read the sheet
            df = pd.read_excel(self.excel_file, sheet_name=tab_name)
            
            # Process each section
            fb_start = 0  # FB section starts at beginning
            mb_start = df.columns.get_loc('New Manual Intervention Map Bit')
            wb_start = df.columns.get_loc('New Warning Map Bit')
            
            # Get results for each section
            fb_results = self.process_section(df, fb_start)
            mb_results = self.process_section(df, mb_start)
            wb_results = self.process_section(df, wb_start)
            
            # Create separate DataFrames for each section
            fb_df = pd.DataFrame(fb_results, columns=['Trigger Value', 'Description'])
            mb_df = pd.DataFrame(mb_results, columns=['Trigger Value', 'Description'])
            wb_df = pd.DataFrame(wb_results, columns=['Trigger Value', 'Description'])
            
            return fb_df, mb_df, wb_df
            
        except Exception as e:
            logger.error(f"Error processing tab {tab_name}: {str(e)}")
            raise

    def process_cpu_tab_to_file(self, tab_name: str, output_dir: Path) -> Path:
        """Process a single CPU tab and save to file, returning the file path."""
        try:
            # Process the CPU tab
            fb_df, mb_df, wb_df = self.process_cpu_tab(tab_name)
            
            # Create output file path
            output_file = output_dir / f"{tab_name}_processed.xlsx"
            
            # Create output sheets
            with pd.ExcelWriter(output_file) as writer:
                fb_df.to_excel(writer, sheet_name='Faults', index=False)
                mb_df.to_excel(writer, sheet_name='Manual Interventions', index=False)
                wb_df.to_excel(writer, sheet_name='Warnings', index=False)
            
            return output_file
            
        except Exception as e:
            logger.error(f"Error processing tab {tab_name} to file: {str(e)}")
            raise

    def calculate_usage_stats(self, tab_name: str) -> Dict[str, Any]:
        """Calculate usage statistics for a CPU tab."""
        df = pd.read_excel(self.excel_file, sheet_name=tab_name)
        
        # Count FB section usage
        fb_total = df['Tag Name'].notna().sum()
        fb_used = df[df['Used'] == 'X']['Tag Name'].count()
        fb_spare = fb_total - fb_used
        
        # Count MB section usage
        mb_start = df.columns.get_loc('New Manual Intervention Map Bit')
        mb_tag_col = df.columns[mb_start + 4]  # Tag Name column
        mb_used_col = df.columns[mb_start + 8]  # Used column
        mb_total = df[mb_tag_col].notna().sum()
        mb_used = df[df[mb_used_col] == 'X'][mb_tag_col].count()
        mb_spare = mb_total - mb_used
        
        # Count WB section usage
        wb_start = df.columns.get_loc('New Warning Map Bit')
        wb_tag_col = df.columns[wb_start + 4]  # Tag Name column
        wb_used_col = df.columns[wb_start + 8]  # Used column
        wb_total = df[wb_tag_col].notna().sum()
        wb_used = df[df[wb_used_col] == 'X'][wb_tag_col].count()
        wb_spare = wb_total - wb_used
        
        return {
            'fault_bits': {
                'total': int(fb_total),
                'used': int(fb_used),
                'spare': int(fb_spare),
                'spare_percentage': float(round((fb_spare / fb_total * 100), 2)) if fb_total > 0 else 0.0
            },
            'manual_intervention_bits': {
                'total': int(mb_total),
                'used': int(mb_used),
                'spare': int(mb_spare),
                'spare_percentage': float(round((mb_spare / mb_total * 100), 2)) if mb_total > 0 else 0.0
            },
            'warning_bits': {
                'total': int(wb_total),
                'used': int(wb_used),
                'spare': int(wb_spare),
                'spare_percentage': float(round((wb_spare / wb_total * 100), 2)) if wb_total > 0 else 0.0
            }
        }

    def preview_cpu_tab(self, tab_name: str) -> Dict[str, Any]:
        """Generate a preview of the CPU tab data."""
        fb_df, mb_df, wb_df = self.process_cpu_tab(tab_name)
        usage_stats = self.calculate_usage_stats(tab_name)
        
        # Convert DataFrames to JSON-serializable format
        def convert_df_to_records(df):
            records = []
            for _, row in df.iterrows():
                record = {}
                for col in df.columns:
                    value = row[col]
                    # Convert numpy types to Python types
                    if hasattr(value, 'item'):
                        record[col] = value.item()
                    else:
                        record[col] = value
                records.append(record)
            return records
        
        return {
            'columns': ['Trigger Value', 'Description'],
            'data': {
                'faults': convert_df_to_records(fb_df),
                'manual_interventions': convert_df_to_records(mb_df),
                'warnings': convert_df_to_records(wb_df)
            },
            'total_rows': {
                'faults': int(len(fb_df)),
                'manual_interventions': int(len(mb_df)),
                'warnings': int(len(wb_df))
            },
            'usage_stats': usage_stats
        }

    def get_section_data(self, tab_name: str, section: str, page: int = 0, page_size: int = 1000) -> Dict[str, Any]:
        """Get paginated data for a specific section."""
        try:
            fb_df, mb_df, wb_df = self.process_cpu_tab(tab_name)
            
            # Select the appropriate DataFrame
            if section == 'faults':
                df = fb_df
            elif section == 'manual_interventions':
                df = mb_df
            elif section == 'warnings':
                df = wb_df
            else:
                raise ValueError(f"Invalid section: {section}")
            
            # Calculate pagination
            total_rows = len(df)
            start_idx = page * page_size
            end_idx = min(start_idx + page_size, total_rows)
            
            # Get the page of data
            page_df = df.iloc[start_idx:end_idx]
            
            # Convert to records
            records = []
            for _, row in page_df.iterrows():
                record = {}
                for col in df.columns:
                    value = row[col]
                    if hasattr(value, 'item'):
                        record[col] = value.item()
                    else:
                        record[col] = value
                records.append(record)
            
            return {
                'data': records,
                'total_rows': total_rows,
                'page': page,
                'page_size': page_size,
                'has_more': end_idx < total_rows
            }
            
        except Exception as e:
            logger.error(f"Error getting section data for {tab_name}/{section}: {str(e)}")
            raise

    def process_selected_cpus(self, selected_cpus: List[str], output_dir: Path) -> Dict[str, Path]:
        """Process selected CPU tabs and save to output files."""
        output_files = {}
        output_dir.mkdir(exist_ok=True)
        
        for cpu in selected_cpus:
            try:
                # Process the CPU tab
                fb_df, mb_df, wb_df = self.process_cpu_tab(cpu)
                
                # Generate output file path
                output_file = output_dir / f"{cpu}_Faults.xlsx"
                
                # Save to Excel file
                with pd.ExcelWriter(output_file) as writer:
                    fb_df.to_excel(writer, sheet_name='Faults', index=False)
                    mb_df.to_excel(writer, sheet_name='Manual Interventions', index=False)
                    wb_df.to_excel(writer, sheet_name='Warnings', index=False)
                
                output_files[cpu] = output_file
                logger.info(f"Successfully processed {cpu} to {output_file}")
                
            except Exception as e:
                logger.error(f"Failed to process {cpu}: {str(e)}")
                continue
        
        return output_files