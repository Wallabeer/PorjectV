import pandas as pd
from datetime import datetime, timedelta

def toHTMLTable(jsonData, path, fields, filterByDate=False, filterByDue=False):
    if path:
        jsonData = jsonData[path][0]
    df = pd.DataFrame(jsonData['data'])
    colNames = [jsonData['fields'][field] for field in fields]
    df = df.iloc[:, fields]
    df.columns = pd.RangeIndex(len(df.columns))
    if filterByDate:
        now = datetime.now()
        roc_year = now.year - 1911
        today_str = f"{roc_year}/{now.strftime('%m/%d')}"
        yesterday = now - timedelta(days=1)
        yest_roc_year = yesterday.year - 1911
        yest_str = f"{yest_roc_year}/{yesterday.strftime('%m/%d')}"
        target_dates = [today_str, yest_str]
        print(target_dates)
        df = df[df[0].isin(target_dates)].sort_values(by=0, ascending=False)
    if filterByDue:
        df = df.loc[df.groupby(1)[0].idxmax()]
        def parse_roc_date(date_str):
            y, m, d = date_str.split('/')
            return datetime(int(y) + 1911, int(m), int(d))
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        due_col = df.columns[-1]
        def get_due_date(val):
            try:
                end = val.replace('～','~').split('~')[-1].strip()
                return parse_roc_date(end).date()
            except:
                return None
        df['到期日'] = df[due_col].apply(get_due_date)
        df_tomorrow = df[df['到期日'] == today].copy()
        df_after = df[df['到期日'] == tomorrow].copy()
        df = pd.concat([df_tomorrow, df_after]).sort_values(by='到期日')
        colNames.append('到期日')
    if df.empty:
        return None
    df.columns = colNames
    styler = df.style.set_table_attributes(
        'border="1" style="border-collapse: collapse; width: 100%; font-family: sans-serif;"'
    )
    styler.set_table_styles([
        {'selector': 'thead tr', 'props': [('background-color', '#f2f2f2')]},
        {'selector': 'th', 'props': [('padding', '8px'), ('text-align', 'left')]}
    ])
    styler.set_properties(**{'padding': '8px'})
    html_content = styler.hide(axis="index").to_html()
    return html_content.replace('\n', '')
