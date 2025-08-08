import pandas as pd
from pathlib import Path
import logging
import re
from typing import List, Tuple, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExcelProcessor:
    def __init__(self, input_file):
        self.excel_file = pd.ExcelFile(input_file)
    
    def calculate_trigger_value(self, tag_name):
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

    def remove_duplicates(self, entries: List[Tuple[int, str, str]]) -> List[Tuple[int, str, str]]:
        """Remove duplicate entries based on tag names.
        For duplicates:
        - Keep entry with description over entry without description
        - If neither has description, keep only one instance
        """
        # Group entries by tag name
        tag_groups: Dict[str, List[Tuple[int, str, str]]] = {}
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

    def process_section(self, df, start_col, tag_col_offset=4, desc_col_offset=6):
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

    def process_cpu_tab(self, tab_name):
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
            
            # Create output sheets
            with pd.ExcelWriter(f'{tab_name}_Faults.xlsx') as writer:
                fb_df.to_excel(writer, sheet_name='Faults', index=False)
                mb_df.to_excel(writer, sheet_name='Manual Interventions', index=False)
                wb_df.to_excel(writer, sheet_name='Warnings', index=False)
            
            # Print some statistics
            print(f"\n{tab_name} Statistics:")
            print(f"Fault bits: {len(fb_df)} entries")
            print(f"Manual Intervention bits: {len(mb_df)} entries")
            print(f"Warning bits: {len(wb_df)} entries")
            
            print("\nSample entries from each section:")
            print("\nFaults:")
            print(fb_df.head())
            print("\nManual Interventions:")
            print(mb_df.head())
            print("\nWarnings:")
            print(wb_df.head())
            
            return fb_df, mb_df, wb_df
            
        except Exception as e:
            logger.error(f"Error processing tab {tab_name}: {str(e)}")
            raise

# Process CPU05 and CPU06
processor = ExcelProcessor('Alarm List Template.xlsx')

# Process the tabs
for cpu in ['CPU05', 'CPU06']:
    processor.process_cpu_tab(cpu)

# Test trigger value calculation
test_tags = ['FB1[0].5', 'FB1[53].30', 'MB1[1].0', 'WB1[2].15']
print("\nTrigger Value Calculation Tests:")
for tag in test_tags:
    trigger = processor.calculate_trigger_value(tag)
    print(f"{tag} -> {trigger}")