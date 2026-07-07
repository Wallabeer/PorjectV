import os
from dotenv import load_dotenv
import json
from data_utils import get_session_with_retry, getData
from html_utils import toHTMLTable
from email_utils import send_email

load_dotenv()

def main():
    configs = json.loads(os.getenv('SRC'))
    html = ''
    with get_session_with_retry() as session:
        for config in configs['source']:
            print(f"-- fetching {config['name']} --")
            data = getData(session, config['url'])
            if data and data.get('stat').casefold() == 'OK'.casefold():
                isFilterByDate = config.get('filterbyDate')
                isFilterByDue = config.get('filterByDue')
                html_table = toHTMLTable(data, config['path'], config['fields'], isFilterByDate, isFilterByDue)
                html += f"<h2>{config['name']}</h2>"
                html += html_table if html_table else "<p>近期無新處置資料。</p>"
            else:
                html += f"<h2>{config['name']}</h2><p>無法取得資料或目前無資料。</p>"
    send_email(html)

if __name__ == "__main__":
    main()
