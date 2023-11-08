import re
from datetime import datetime
import calendar
import numpy as np
import pandas as pd
import argparse


DATE_PATTERN = re.compile(r'\d{1,2}/(\d{1,2})/\d{2}')
ANDROID_PATTERN = re.compile(r'\d{1,2}/\d{1,2}/\d{2}, \d{2}:\d{2} - ([^:]+):')
APPLE_PATTERN = re.compile(r'\[\d{1,2}/\d{1,2}/\d{1,2}, \d{1,2}:\d{1,2}:\d{1,2} [AP]M\] ([^:]+):')
MORNING_REGEX = re.compile(r'good\s+morning|gm|suprabhatam|Suprabhatham|Shubodaya|Shubodhaya|Gud\s+morning|Gud\s+Mrng|Good\s+morning', re.IGNORECASE)


class AttendanceTracker:

    def __init__(self):
        self.members = {}

    def get_or_create_member(self, name):
        if name not in self.members:
            self.members[name] = LB_Member(name)
        return self.members[name]

    def parse_messages(self, file_path):
        # Parse file and mark attendance
        date_format = '%d/%m/%y'
        with open(file_path) as f:
            for line in f:
                # Extract date from line    
                match = DATE_PATTERN.search(line)
                if match:
                    date = datetime.strptime(match.group(), '%d/%m/%y')
                    day = date.day

                if MORNING_REGEX.search(line):
                    match = ANDROID_PATTERN.match(line)
                    if not match:
                        match = APPLE_PATTERN.match(line)
                    if match:
                        name = match.group(1)
                        member = self.get_or_create_member(name)
                        member.mark_present(day, date.month)
        return date.month
        

    def generate_report(self, month, output_name): 
        # Generate attendance report for given month
        days = calendar.monthrange(datetime.now().year, month)[1]  
        
        data = []
        tbl_hdr = ['Name', 'no_of_days', 'atten_percentage']
        for member in self.members.values():
            attendance = member.get_attendance()
            percentage = attendance / days * 100
            data.append([member.name, attendance,percentage])
        # Generate DataFrame and output report
        df = pd.DataFrame(data, columns=tbl_hdr)
        df.to_csv(output_name)


class LB_Member:

    def __init__(self, name):
        self.name = name
        self.attendance = 0

    def mark_present(self, day, month):

        max_days = calendar.monthrange(datetime.now().year, month)[1]
        if 1 <= day <= max_days:
            # Shift 1 to the left by (day - 1) positions and use bitwise OR to mark the day as present
            self.attendance |= 1 << (day - 1)
        else:
            print("Invalid day, should be between 1 and 31")

    def get_attendance(self):
       # Return attendance count
       # Convert the attendance integer to a 32-character binary string
        return bin(self.attendance)[2:].zfill(32).count('1')

def main(file_path, output_path):
    tracker = AttendanceTracker()
    month = tracker.parse_messages(file_path)
    tracker.generate_report(month,output_path)

if __name__ == "__main__":

    #create a argparser
    parser = argparse.ArgumentParser(description='Attendance tracker')

    parser.add_argument("-f", "--file_path",required=True, help="Path to chat log file")
    parser.add_argument("-o", "--output", required=True, help="Output report file path")
    args = parser.parse_args()
    main(args.file_path, args.output)