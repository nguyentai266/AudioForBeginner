from parser import ParserLog

import pandas as pd

from core.load_config import load_yaml
from core.logger import setup_logging

parser=ParserLog()
config=load_yaml()
logger=setup_logging()

class AudioAnalysis:
    def __init__(self):
        self.df_limit = None
        self.df_raw = None
        self.phases = None

    import pandas as pd

class AudioAnalysis:
    def __init__(self):
        self.df_limit = None
        self.df_raw = None
        self.phases = None

    def correlation(self, dataFrame_limit, dataFrame_raw):
        self.df_limit = dataFrame_limit
        self.df_raw = dataFrame_raw
        
        # 1. Lấy danh sách các phase (ví dụ: ['mic-1_fr', 'mic-2_fr'])
        self.phases = self.df_limit['phase'].unique().tolist()
        
        # 2. Lọc cột theo khớp tuyệt đối phần đầu (Prefix)
        # Chúng ta kiểm tra nếu cột bắt đầu bằng "phase" + "_" và ký tự tiếp theo là số
        cols_fr = []
        for c in self.df_raw.columns:
            for p in self.phases:
                # Kiểm tra: Cột phải bắt đầu bằng phase + "_"
                if c.startswith(f"{p}_"):
                    # Lấy phần còn lại sau phase + "_"
                    remainder = c[len(p)+1:]
                    # Nếu phần còn lại bắt đầu bằng số (ví dụ: 00100.0) thì mới lấy
                    if remainder and remainder[0].isdigit():
                        cols_fr.append(c)
                        break
        
        if not cols_fr:
            print("Cảnh báo: Không tìm thấy cột nào khớp tuyệt đối với định dạng.")
            return None, None

        # 3. Chuẩn bị dữ liệu số và loại bỏ phân mảnh
        df_numeric = self.df_raw[cols_fr].apply(pd.to_numeric, errors="coerce")
        station_ids = self.df_raw['station_id']

        # 4. Tính Trung bình Tổng (Global Average)
        avg_total_series = df_numeric.mean()
        avg_total_df = avg_total_series.to_frame().T
        avg_total_df.insert(0, 'station_id', 'TOTAL_AVG')

        # 5. Tính Trung bình theo từng Nhóm (Group Average)
        df_for_group = df_numeric.copy()
        df_for_group['station_id'] = station_ids
        avg_group_df = df_for_group.groupby('station_id', as_index=False).mean()

        # 6. Tạo DataFrame 1: Summary (Gồm Total và Group Avg)
        summary_df = pd.concat([avg_total_df, avg_group_df], ignore_index=True).copy()

        # 7. Tạo DataFrame 2: Gap (Group Avg - Total Avg)
        group_vals = avg_group_df[cols_fr]
        gap_vals = group_vals.sub(avg_total_series, axis=1)
        gap_df = pd.concat([avg_group_df[['station_id']], gap_vals], axis=1).copy()

        return average_df, gap_df

# --- Cách sử dụng ---
# analyzer = AudioAnalysis()
# df_summary, df_gap = analyzer.correlation(df_limit, df_raw)
#
# print("--- BẢNG GIÁ TRỊ TRUNG BÌNH ---")
# print(df_summary.head())
#
# print("\n--- BẢNG KHOẢNG CÁCH (GAP) ---")
# print(df_gap.head())
if __name__ == "__main__":
    path="C:/Users/nguye/Desktop/AudioForBeginner/raw_log_4cs4"
    df_limit,df_data=parser.summary_data(path,mode="audio_full")
    correl=AudioAnalysis()
    df_correl,df_gap=correl.correlation(df_limit,df_data)
    df_gap.to_csv("gap.csv")
    df_correl.to_csv("correl.csv")




