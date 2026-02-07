import pandas as pd

path="limit.csv"

df=pd.read_csv(path)

df_T=df.transpose()

df_1 = df_T.reset_index().rename(columns={"index": "measurement"})

df_1.columns = df_1.iloc[0]

# xoá 2 hàng đầu (header cũ + header mới vừa dùng)
df_1 = df_1.iloc[1:].reset_index(drop=True)

print(df_1)