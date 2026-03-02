import pandas as pd

from core.load_config import load_yaml
from core.logger import setup_logging
from core.parser import ParserLog

parser=ParserLog()
config=load_yaml()
logger=setup_logging()

import numpy as np


class AudioCorrelation:
    def __init__(self):
        self.df_limit = None
        self.df_raw = None
        self.phases = None


    def correlation(self, dataFrame_limit, dataFrame_raw):
        self.df_limit = dataFrame_limit
        self.df_raw = dataFrame_raw
        self.phases = self.df_limit['phase'].unique().tolist()
        
        # Lọc danh sách cột tần số giữ nguyên thứ tự df_raw
        cols_fr = []
        for c in self.df_raw.columns:
            for p in self.phases:
                if c.startswith(f"{p}_"):
                    remainder = c[len(p)+1:]
                    if remainder and remainder[0].isdigit():
                        cols_fr.append(c)
                        break
        
        if not cols_fr:
            print("Cảnh báo: Không tìm thấy cột tần số khớp định dạng.")
            return None, None, None

        df_numeric = self.df_raw[cols_fr].apply(pd.to_numeric, errors="coerce")
        station_ids = self.df_raw['station_id']

        # 1. Average Group
        avg_group_df = df_numeric.copy()
        avg_group_df['station_id'] = station_ids
        avg_group_df = avg_group_df.groupby('station_id', as_index=False).mean()

        # 2. Gap Group
        avg_total_series = df_numeric.mean()
        gap_vals = avg_group_df[cols_fr].sub(avg_total_series, axis=1)
        gap_group_df = pd.concat([avg_group_df[['station_id']], gap_vals], axis=1).copy()

        # 3. Tạo df_limit_correl dạng dọc với logic NA ngoài dải chốt
        '''df_limit_correl = None
        if limit_correl_config is not None:
            df_limit_correl = self.get_step_limit_df(limit_correl_config, cols_fr)'''

        return avg_group_df, gap_group_df

if __name__ == "__main__":
    path="C:/Users/V1531673/Desktop/AudioForBeginner/raw_log_4cs4"
    df_limit,df_data=parser.summary_data(path,mode="audio_full")
    correl=AudioCorrelation()
    df_correl,df_gap,df_limit_correl=correl.correlation(df_limit,df_data,limit_correl_config=config["limit_correl"])
    df_gap.to_csv("gap.csv")
    df_correl.to_csv("correl.csv")
    df_limit_correl.to_csv("limit_correl.csv")




