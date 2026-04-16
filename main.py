import requests
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

def get_disposal_list():
    """爬取網頁版資料並篩選近兩天公布標的"""
    url = "https://www.twse.com.tw/rwd/zh/announcement/punish?response=json"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    today = datetime.now() - relativedelta(years=1911)
    yesterday = today - timedelta(days=1)   # 調整為昨天，確保抓到最新資料
    target_dates = [today.strftime('%Y%m/%d')[1:], yesterday.strftime('%Y/%m/%d')[1:]]
    
    try:
        response = requests.get(url, headers=headers, timeout=30, verify=False)
        json_data = response.json()
        
        if 'data' not in json_data or not json_data['data']:
            return None

        # print(json_data)
        # print(json_data['data'][0])
        # 欄位索引：0:公布日期, 1:證券代號, 2:證券名稱, 3:起迄時間, 4:累計處置條件, 5:處置措施
        df = pd.DataFrame(json_data['data'])
        # print(df.iloc[0])
        print(target_dates)
        recent_df = df[df[1].isin(target_dates)].copy()
        
        if recent_df.empty:
            return None 

        # 建立 HTML 表格內容
        html_content = """
        <table border="1" style="border-collapse: collapse; width: 100%; font-family: sans-serif;">
            <tr style="background-color: #f2f2f2;">
                <th>公布日期</th><th>代號</th><th>名稱</th><th>起迄時間</th><th>處置條件</th><th>處置措施</th>
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
        html_content.replace('\n', '')
        return html_content
    except Exception as e:
        print(f"抓取失敗: {e}")
        return None

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
    data_html = get_disposal_list()
    print(data_html if data_html else "近兩日無新公布處置股。")
    send_email(data_html)