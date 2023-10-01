import re
import matplotlib.pyplot as plt
from collections import defaultdict
from datetime import datetime
import calendar
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

LBAttendance_records = {}
class LBAttendance:
    def __init__(self, name):
        self.name = name
        self.attendance = 0  # Initialize attendance as a 32-bit integer with all bits set to 0
    
    def getName(self):
        return self.name
    
    def getValue(self):
        return self.attendance

    def mark_present(self, day):
        if 1 <= day <= 32:
            # Shift 1 to the left by (day - 1) positions and use bitwise OR to mark the day as present
            self.attendance |= 1 << (day - 1)
        else:
            print("Invalid day, should be between 1 and 32")

    def mark_absent(self, day):
        if 1 <= day <= 32:
            # Shift 1 to the left by (day - 1) positions, negate it, and use bitwise AND to mark the day as absent
            self.attendance &= ~(1 << (day - 1))
        else:
            print("Invalid day, should be between 1 and 32")

    def check_attendance(self, day):
        if 1 <= day <= 32:
            # Shift 1 to the left by (day - 1) positions and use bitwise AND to check attendance
            return (self.attendance & (1 << (day - 1))) != 0
        else:
            print("Invalid day, should be between 1 and 32")

    def get_attendance_binary(self):
        # Convert the attendance integer to a 32-character binary string
        return bin(self.attendance)[2:].zfill(32)

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
    writer.close()

# Function to create or retrieve a LBAttendance object for a LB-member
def get_or_create_LBAttendance(LBA_member_name):
    if LBA_member_name not in LBAttendance_records:
        lb_object = LBAttendance(LBA_member_name)
        LBAttendance_records[lb_object.getName()] = lb_object
    return LBAttendance_records[LBA_member_name]
    
def parse_whatsapp_messages(file_path):
    #attendance = defaultdict(int)
    date_format = '%d/%m/%y'
    with open(file_path, 'r', encoding='utf-8') as file:
        date_pattern = r'\d{1,2}/(\d{1,2})/\d{2}'
        #date_pattern = r'\d{2}/(\d{2})/\d{2}'
        for line in file:
            # Check for new month
            match = re.search(date_pattern, line)
            if match:
                dates = match.group()
                date_obj = datetime.strptime(dates, date_format)  
                             
            # Check for good morning messages
            #pattern - Android's chat dump.
            #01/07/23, 05:34 - Bhatta:
            #android_msg_patter = r'\d{1,2}/\d{1,2}/\d{2}, \d{2}:\d{2} - ([^:]+):', line)
            #[01/09/23, 5:33:05 AM] DRK: Good morning
            apple_msg_pattern = r'^\[\d{1,2}\/\d{1,2}\/\d{1,2}, \d{1,2}:\d{1,2}:\d{1,2} [AP]M\] ([^:]+):'
            if re.search(r'good\s+morning|gm|suprabhatam|Suprabhatham|Shubodaya|Shubodhaya|Gud\s+morning|Gud\s+Mrng|Good\s+morning', line, re.IGNORECASE):
                sender_match = re.match(apple_msg_pattern, line)
                if sender_match:
                    sender = sender_match.group(1)
                    la_member = get_or_create_LBAttendance(sender)
                    la_member.mark_present(date_obj.day)
                    #attendance[sender] += 1       
    return date_obj.month

def main():
    # Example usage
    file_path = 'c:\\Users\skbasava\\Downloads\LBA.txt'  # Replace with the path to your WhatsApp chat text file
    month = parse_whatsapp_messages(file_path)
        
    # Use monthrange to get the number of days in the month
    _, num_days = calendar.monthrange(datetime.now().year, int(month))
    
    
    tbl_hdr = ['Name', 'atten_per', 'fees_paid', 'Rank']
    concat_hdr = ['no_of_days']
    
    tolist = []
    # Add data rows to the table
    for key, lb_mem in LBAttendance_records.items():
        binary_string = bin(lb_mem.getValue())
        attendance = binary_string.count('1')
        atten_percn = calculate_attendance_percentage(attendance, num_days)
        rank = calculate_value_score(atten_percn, int(LB_COURT_FEE))
        rank_tbl.append([key, atten_percn, int(LB_COURT_FEE), rank])
        tolist.append(attendance)
    
    # Create a Pandas DataFrame       
    df = pd.DataFrame(rank_tbl, columns=tbl_hdr)
    data_df = pd.DataFrame(tolist, columns=concat_hdr)
    attend_data = pd.concat([df, data_df], axis=1)
    print(attend_data)
    
    dataframe_to_excel(attend_data, 'Sept_LB_attendenace_result.xlsx', sheet_name='LBA', index=False)
   
    
if __name__ == "__main__":
    main()
