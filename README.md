Team Attendance Tracker

This script parses a chat log (e.g. WhatsApp, Slack etc) to track attendance of team members based on their greeting messages. It generates a summary CSV report of the attendance for the month.
Features

    Parses whatsapp chat log file and extracts date and member name from each line
    Identifies common morning greeting messages to mark member as present for the day
    Supports multiple chat formats like WhatsApp, Telegram etc
    Stores attendance records for each member in an optimized data structure
    Generates a summary CSV report with name and attendance percentage
    Easy to extend with new features like emailing reports, plotting graphs etc

Usage

    python LB_attendance.py <chat_logfile>

This will parse the given logfile and generate attendance-<month>.csv summary report in the current directory.

The script accepts the following optional arguments:
    
      -h, --help            show this help message and exit
      -f FILE, --file FILE  Path to chat log file
      -o OUTPUT, --output OUTPUT  
                            Output report file path
Example:

    python LB_attendance.py -f chat.txt -o report.csv

Dependencies

    Python 3.x
    Pandas
    Calendar

Notes

    Currently configured for a 31 day month. Can be extended to handle variable lengths
    Greeting matches are case-insensitive but exact member name match is required
    Only parses WhatsApp and Slack style formats currently

License

This project is open source and available under the MIT License.
Credits

This script was created by Satish Basavaraju 
