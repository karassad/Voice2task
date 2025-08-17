from datetime import datetime, timedelta

now = datetime.now()
today_date = now.strftime('%Y-%m-%d')
today_date1 = now.strftime('%y-%M-%D')
print(now)
print(today_date)
print(today_date1)
print(now.strftime('%y'))
print((now + timedelta(1)).weekday())