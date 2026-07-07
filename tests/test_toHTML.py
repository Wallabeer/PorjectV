import json
import sys
from src.html_utils import toHTMLTable
from unittest.mock import patch
from datetime import datetime

if __name__ == "__main__":
    with open("data/market1_test.json", encoding="utf-8") as f:
        jsonData = json.load(f)
    path = "tables"
    fields = [1, 2, 3, 4, 5]
    filterByDate = False
    filterByDue = True
    with patch("src.html_utils.datetime") as mock_datetime:
        mock_datetime.now.return_value = datetime(2026, 7, 1)
        mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
        html = toHTMLTable(jsonData, path, fields, filterByDate, filterByDue)
    print(html if html else "No data returned.")
