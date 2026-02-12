import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# DB接続
conn = sqlite3.connect(r"C:\Users\seigo\private_apps\02_kanekoayano_app\app\data\app.db")

# データ読み込み
df = pd.read_sql_query("SELECT * FROM table_name", conn)

df.head()
