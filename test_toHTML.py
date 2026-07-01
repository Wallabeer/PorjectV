import json
import sys
from main import toHTMLTable

if __name__ == "__main__":
    with open("market1_test.json", encoding="utf-8") as f:
        jsonData = json.load(f)
    
    # path = ''
    # fields = [1, 2, 3, 4, 5, 6]
    path = "tables"
    fields = [1, 2, 3, 4, 5]
    filterByDate = False
    filterByDue = True
    html = toHTMLTable(jsonData, path, fields, filterByDate, filterByDue)
    print(html if html else "No data returned.")
