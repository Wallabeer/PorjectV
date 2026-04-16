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

# 使用範例
def get_disposal_list():
    url = "https://www.twse.com.tw/rwd/zh/announcement/punish?response=json"
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

def format_data(json_data):
        # 欄位索引：0:公布日期, 1:證券代號, 2:證券名稱, 3:起迄時間, 4:累計處置條件, 5:處置措施
        df = pd.DataFrame(json_data['data'])
        
        today = datetime.now() - relativedelta(years=1911)
        yesterday = today - timedelta(days=1)   # 調整為昨天，確保抓到最新資料
        target_dates = [today.strftime('%Y/%m/%d')[1:], yesterday.strftime('%Y/%m/%d')[1:]]
        print(target_dates)
        recent_df = df[df[1].isin(target_dates)].iloc[:,:7].copy()
        recent_df.sort_values(by=1, inplace=True)
        
        if recent_df.empty:
            return None 

        # 建立 HTML 表格內容
        html_content = """
        <table border="1" style="border-collapse: collapse; width: 100%; font-family: sans-serif;">
            <tr style="background-color: #f2f2f2;">
                <th>公布日期</th><th>證券代號</th><th>證券名稱</th><th>累計</th><th>處置條件</th><th>處置起迄時間</th>
            </tr>
        """
        
        for _, row in recent_df.iterrows():
            html_content += f"""
            <tr>
                <td style="padding: 8px;">{row[1]}</td>
                <td style="padding: 8px;">{row[2]}</td>
                <td style="padding: 8px;">{row[3]}</td>
                <td style="padding: 8px;">{row[4]}</td>
                <td style="padding: 8px; font-size: 0.9em;">{row[5]}</td>
                <td style="padding: 8px; font-size: 0.9em;">{row[6]}</td>
            </tr>
            """
        html_content += "</table>"

        return html_content.replace('\n', '')

def send_email(content):
    if not content:
        print("近兩日無新公布處置股，不寄送郵件。")
        return

    user = os.getenv('GMAIL_USER')
    password = os.getenv('GMAIL_PASSWORD')
    target = os.getenv('RECEIVER_EMAIL')

    subject = f"【台股警訊】新進處置股彙整 ({datetime.now().strftime('%Y/%m/%d')})"
    
    try:
        yag = yagmail.SMTP(user, password)
        yag.send(to=target, subject=subject, contents=content)
        print("Email 寄送成功！")
    except Exception as e:
        print(f"Email 寄送失敗: {e}")

if __name__ == "__main__":
    dataSource = get_disposal_list()
    print(dataSource['title'] if dataSource else "近兩日無新公布處置股。")
    data = format_data(dataSource) if dataSource else None
    send_email(data)