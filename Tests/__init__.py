"important for running(different packages)"

"{"
# for running tests from packages
"1. import sys"
"2.import os"
# הקסם: הוספת התיקייה "אחת למעלה" לנתיב החיפוש של פייתון
"3.sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))"\
"}"