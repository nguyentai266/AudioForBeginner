

import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def plot_fr(csv_path, title="dut_comp"):
    df = pd.read_csv(csv_path, header=None)

    # Lấy dòng bắt đầu bằng mic-1_fr
    fr_rows = df[df[0].str.contains("mic-1_fr", na=False)]

    # Tách tần số từ tên dòng
    freqs = fr_rows[0].str.extract(r"mic-1_fr_(\d+\.\d+)")[0].astype(float)

    # Lấy dữ liệu đo (20 cột)
    data = fr_rows.iloc[:, 1:21].astype(float)

    # Trung bình các DUT
    mean = data.mean(axis=1)

    # Tạo limit giả (để giống hình)
    upper = mean + 3
    lower = mean - 3

    # Vẽ
    fig = plt.figure(figsize=(10, 4))
    ax = fig.add_subplot(111)

    for i in range(data.shape[1]):
        ax.plot(freqs, data.iloc[:, i], linewidth=1)

    # Vẽ limit
    ax.plot(freqs, upper, color="red", linewidth=2)
    ax.plot(freqs, lower, color="red", linewidth=2, label="limits")

    # Trục log
    ax.set_xscale("log")
    ax.set_xlim(100, 22400)

    # Tick đẹp
    ax.set_xticks(
        np.logspace(start=2,stop=4,num=10),
        ["",r"$10^2$", r"$10^3$", r"$10^4$"]
    )

    ax.set_xlabel("freq[Hz]")
    ax.set_ylabel("Amplitude (dB)")
    ax.set_title(title)

    ax.grid(True, which="both", alpha=0.5)
    ax.legend()

    plt.tight_layout()
    plt.show()



# 1. Đọc file
df = pd.read_csv("sum.csv")

# 2. Lọc các cột FR mic
fr_cols = [c for c in df.columns if c.startswith("mic-1_fr")]

# 3. Chuyển wide -> long
df_long = df.melt(
    id_vars=["log_id"],
    value_vars=fr_cols,
    var_name="measurement",
    value_name="value"
)

# 4. Tách tần số
df_long["freq"] = df_long["measurement"].str.extract(r"_(\d+\.\d+)$").astype(float)

# 5. Vẽ
plt.figure(figsize=(10, 4))

for uid, g in df_long.groupby("log_id"):
    plt.plot(g["freq"], g["value"], linewidth=1)

plt.xscale("log")
plt.xlim(100, 22400)

plt.xticks(
    [100, 1000, 10000],
    [r"$10^2$", r"$10^3$", r"$10^4$"]
)

plt.xlabel("Frequency (Hz)")
plt.ylabel("Amplitude (dB)")
plt.title("Mic FR Comparison")
plt.grid(True, which="both", alpha=0.5)

plt.show()
