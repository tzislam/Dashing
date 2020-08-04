from bs4 import BeautifulSoup
import csv
from collections import defaultdict

html = open("knl_events.html").read()
soup = BeautifulSoup(html, features="lxml")
table = soup.find("table")

output_rows = []
event_map = defaultdict()
for table_row in table.findAll('tr'):
    columns = table_row.findAll('td')
    key = ""
    val = ""
    flag=0
    for column in columns:
        a=column.text.split('=')
        for v in a:
            if v != "OFFCORE_RESPONSE:request" and v != "ALL_REQUESTS: response":
                if flag == 0:
                    key = v
                    flag = 1
                    print("++ key=", key)
                else:
                    val = v
                    print("++ Val=", val)
            else:
                flag = 0
                print("--", v)
        key = key.strip("\n'\"")
        val = val.strip("\n'\"")
        event_map[key] = val

for data in event_map.items():
    print (data)
        
csv_columns = ['Event', 'Desc']
csv_file="knl_event_desc.csv"
try:
    with open(csv_file, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(csv_columns)
        for key, value in event_map.items():
            writer.writerow([key, value])
except IOError:
    print("I/O error") 
