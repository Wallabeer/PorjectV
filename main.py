import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import pandas as pd
import os
import yagmail
import urllib3
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
import json
load_dotenv()

# 解決證交所 SSL 驗證問題
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_session_with_retry():
    session = requests.Session()
    
    # 定義重試規則
    retry_strategy = Retry(
        total=5,                # 總共重試次數
        backoff_factor=1,       # 等待間隔：1s, 2s, 4s, 8s, 16s (指數型增長)
        status_forcelist=[429, 500, 502, 503, 504], # 遇到這些 HTTP 狀態碼才重試
        allowed_methods=["GET"] # 哪些請求方法要重試
    )
    
    # 將重試規則綁定到 adapter
    adapter = HTTPAdapter(max_retries=retry_strategy)
    
    # 讓 session 在處理 http:// 和 https:// 時都使用這個規則
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    
    return session

def getData(session, url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}    
    # 建立帶有重試機制的 session
    session = get_session_with_retry()
    
    try:
        # 這裡的 get 只要失敗，就會自動依照規則重試，直到 5 次都失敗才拋出錯誤
        response = session.get(url, headers=headers, timeout=10, verify=False)
        return response.json()
    except Exception as e:
        print(f"最終請求失敗: {e}")
        return None

def toHTMLTable(jsonData, path, fields, filterDate=False):
    if path:
        jsonData = jsonData[path][0]
    df = pd.DataFrame(jsonData['data'])
    colNames = [jsonData['fields'][field] for field in fields]
    df = df.iloc[:, fields]
    # df.columns = colNames
    
    if filterDate:
        # Get ROC year and month/day
        now = datetime.now()
        roc_year = now.year - 1911
        today_str = f"{roc_year}/{now.strftime('%m/%d')}"
        yesterday = now - timedelta(days=1)
        yest_roc_year = yesterday.year - 1911
        yest_str = f"{yest_roc_year}/{yesterday.strftime('%m/%d')}"
        
        target_dates = [today_str, yest_str]
        print(target_dates)
        # Using .str.contains or exact match is safer
        df = df[df[1].isin(target_dates)]
    
    if df.empty:
        return None 
    
    df.columns = colNames
    styler = df.style.set_table_attributes(
        'border="1" style="border-collapse: collapse; width: 100%; font-family: sans-serif;"'
    )

    # 設定 Header 樣式 (tr)
    styler.set_table_styles([
        {'selector': 'thead tr', 'props': [('background-color', '#f2f2f2')]},
        {'selector': 'th', 'props': [('padding', '8px'), ('text-align', 'left')]}
    ])

    # 設定單元格樣式 (td)
    styler.set_properties(**{'padding': '8px'})
    html_content = styler.hide(axis="index").to_html()
    return html_content.replace('\n', '')

def send_email(content):
    if not content:
        print("近兩日無新公布處置股，不寄送郵件。")
        return

    user = os.getenv('GMAIL_USER')
    password = os.getenv('GMAIL_PASSWORD')
    target = os.getenv('RECEIVER_EMAIL').split(';')

    subject = f"【台股警訊】新進處置/注意股彙整 ({datetime.now().strftime('%Y/%m/%d')})"
    
    try:
        yag = yagmail.SMTP(user, password)
        yag.send(to=target, subject=subject, contents=content)
        print("Email 寄送成功！")
    except Exception as e:
        print(f"Email 寄送失敗: {e}")

def main():
    configs = json.loads(os.getenv('SRC'))
    html = ''
    
    # One session for all requests - efficient!
    with get_session_with_retry() as session:
        for config in configs['source']:
            print(f"-- fetching {config['name']} --")
            
            # Pass the session here
            data = getData(session, config['url'])
            
            if data and data.get('stat') == 'OK': # Check TWSE success status
                isFilter = config.get('filter') == 'True'
                html_table = toHTMLTable(data, config['path'], config['fields'], isFilter)
                
                html += f"<h2>{config['name']}</h2>"
                html += html_table if html_table else "<p>近期無新處置資料。</p>"
            else:
                html += f"<h2>{config['name']}</h2><p>無法取得資料或目前無資料。</p>"
    
    send_email(html)

if __name__ == "__main__":
    main()