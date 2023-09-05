import re
import matplotlib.pyplot as plt
from collections import defaultdict
import calendar
import datetime
import math
import numpy as np
import pandas as pd
from xlsxwriter import Workbook


LB_COURT_FEE = "2000"
rank_tbl = []
month_mapping = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December"
}

  
def flatten_dict(d):
    flattened_dict = {}
    for key, value in d.items():
        if isinstance(value, defaultdict):
            flattened_dict[key] = flatten_dict(dict(value))
        else:
            flattened_dict[key] = value
    return flattened_dict

def apply_rounding_based_on_percentage(percentage):
    value = 0.7
    if 0 <= (percentage * 100.0) <= 100:
        if value >= (percentage):
            return math.ceil(percentage * 100.00)
        else:
            return math.floor(percentage * 100.00)
    else:
        raise ValueError("Percentage should be between 0 and 100.")

def calculate_attendance_percentage(attendance, total_classes):
    return (attendance / total_classes) * 100

def calculate_value_score(attendance_percentage, fees_paid):
    #rank = (attendance_percentage / 100) * (fees_paid /int(LB_COURT_FEE))
    rank_range = apply_rounding_based_on_percentage((attendance_percentage / 100) * (fees_paid /int(LB_COURT_FEE)))
    if rank_range >= 80:
        return "Very Regular"
    elif 70 <= rank_range < 90:
        return "Regular"
    elif rank_range < 70:
        return "Low attendance"
    elif rank_range < 50:
        return "Regularly iregular"     
    return "None"

def dataframe_to_excel(dataframe, excel_file, sheet_name='Sheet1', index=False):
    
    writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')
    dataframe.to_excel(writer, sheet_name=sheet_name, index=index)
    writer.save()
    
def parse_whatsapp_messages(file_path):
    tbl_hdr = ["Name", "atten_per"]
    #attendance = defaultdict(lambda: defaultdict(int))
    Kannada_pattern = r"ಶುಭೋದಯಗಳು, ಶುಭೋದಯ, ಸುಭೋದಯಗಳು"
    # Regular expression pattern to search for Kannada strings
    Kannada_upattern = r"[\u0C80-\u0CFF]+"
    
    attendance = defaultdict(int)
    current_month = None

    with open(file_path, 'r', encoding='utf-8') as file:
        pattern = r'\d{1,2}/(\d{1,2})/\d{2}'
        for line in file:
            # Check for new month
            if re.match(pattern, line):
                current_month = re.findall(pattern, line)[0]
                
            # Check for good morning messages
            #sender = re.findall(r'\d{2}/\d{1,2}/\d{2}, \d{2}:\d{2} - ([^:]+):', line)
            if re.search(r'good\s+morning|gm|suprabhatam|Suprabhatham|Shubodaya|Shubodhaya|Gud\s+morning|Gud\s+Mrng|Good\s+morning', line, re.IGNORECASE):
                sender_match = re.match(r'\d{1,2}/\d{1,2}/\d{2}, \d{2}:\d{2} - ([^:]+):', line)
                if sender_match:
                    sender = sender_match.group(1)
                    attendance[sender] += 1
      
           
    return attendance, current_month

def plot_attendance(attendance, c_month, my_table):
    member_names = list(attendance.keys())
    message_counts = list(attendance.values())
    
    # Plot attendance
    plt.bar(member_names, message_counts)
    
    current_month = "Attendance of " + month_mapping[int(c_month)] + " " + str(datetime.datetime.now().year)
    # Customize plot
    plt.xlabel('LB Member')
    plt.ylabel('NoOf Days')
    plt.title(current_month)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Add text inside the bars
    for i, value in enumerate(message_counts):
        plt.text(i, value, str(value), ha='center', va='bottom', fontsize=12, fontweight='bold', color='Orange')
     
    plt.bar_label("sat", label_type='center')
    # Display the plot
    plt.show()
    
def plot_graph(dataframe):
    # Group the data by the 'Rank' column and count the occurrences of each rank
    rank_counts = dataframe['Rank'].value_counts()

    # Create a bar plot
    rank_counts.plot(kind='bar', color='skyblue', edgecolor='black')

    # Set plot labels and title
    plt.xlabel('Rank')
    plt.ylabel('Count')
    plt.title('Rank Distribution')

    # Show the plot
    plt.tight_layout()
    plt.show()

def main():
    # Example usage
    file_path = 'c:\\Users\skbasava\\Downloads\LBA.txt'  # Replace with the path to your WhatsApp chat text file
    attendance, month = parse_whatsapp_messages(file_path)
        
    # Use monthrange to get the number of days in the month
    _, num_days = calendar.monthrange(datetime.datetime.now().year, int(month))
    
    
    tbl_hdr = ['Name', 'atten_per', 'fees_paid', 'Rank']
    concat_hdr = ['no_of_days']
    
    # Add data rows to the table
    for key in attendance:
        atten_percn = calculate_attendance_percentage(attendance[key], num_days)
        rank = calculate_value_score(atten_percn, 2000)
        if key in ("Gangu", "Dr Ramesh", "Surianna", "Felix uncle", "PUG uncle"):
            rank_tbl.append([key, atten_percn, 1000, rank])
        elif key in ("M.Gowdru", "Revana uncle"):
            rank_tbl.append([key, atten_percn, 0, "NA"])
        else:
            rank_tbl.append([key, atten_percn, 2000, rank])
    # Create a Pandas DataFrame       
    df = pd.DataFrame(rank_tbl, columns=tbl_hdr)
    values = list(attendance.values())
    data_df = pd.DataFrame(values, columns=concat_hdr)
    attend_data = pd.concat([df, data_df], axis=1)
    
    dataframe_to_excel(attend_data, 'LB_attendenace_result.xlsx', sheet_name='LBA', index=False)
   
    
if __name__ == "__main__":
    main()