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

    def get_step_limit_df(self, limit_config, cols_fr):
        """
        Tạo df_limit theo logic bậc thang.
        Tần số ngoài dải [min_chốt, max_chốt] sẽ trả về NA.
        """
        all_phase_limits = []
        
        for phase_name, spec in limit_config.items():
            phase_specific_cols = [c for c in cols_fr if c.startswith(f"{phase_name}_")]
            if not phase_specific_cols:
                continue
                
            actual_freqs = sorted([float(c.split('_')[-1]) for c in phase_specific_cols])
            df_full = pd.DataFrame({'freq': actual_freqs}).astype('float64')

            # Tạo DF chốt điểm từ YAML
            df_points = pd.DataFrame({
                'freq': spec['freq'],
                'high_limit': spec['usl'],
                'low_limit': spec['lsl']
            }).astype({'freq': 'float64'}).sort_values('freq')

            # Xác định chốt điểm cuối cùng
            max_spec_freq = df_points['freq'].max()
            min_spec_freq = df_points['freq'].min()

            # Merge logic bậc thang
            df_merged = pd.merge_asof(
                df_full, 
                df_points, 
                on='freq', 
                direction='backward'
            )
            
            # CHỈ ffill cho những điểm nằm trong dải [min_spec, max_spec]
            # Những điểm > max_spec_freq sẽ bị set về NaN
            df_merged.loc[df_merged['freq'] > max_spec_freq, ['high_limit', 'low_limit']] = np.nan
            # Những điểm < min_spec_freq cũng sẽ tự động là NaN do direction='backward'
            
            # Thêm cột phase
            df_merged.insert(0, 'phase', phase_name)
            all_phase_limits.append(df_merged)
                
        if not all_phase_limits:
            return pd.DataFrame(columns=['phase', 'freq', 'low_limit', 'high_limit'])
            
        return pd.concat(all_phase_limits, ignore_index=True)

    def correlation(self, dataFrame_limit, dataFrame_raw, limit_correl_config=None):
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
        df_limit_correl = None
        if limit_correl_config is not None:
            df_limit_correl = self.get_step_limit_df(limit_correl_config, cols_fr)

        return avg_group_df, gap_group_df, df_limit_correl

if __name__ == "__main__":
    path="C:/Users/V1531673/Desktop/AudioForBeginner/raw_log_4cs4"
    df_limit,df_data=parser.summary_data(path,mode="audio_full")
    correl=AudioCorrelation()
    df_correl,df_gap,df_limit_correl=correl.correlation(df_limit,df_data,limit_correl_config=config["limit_correl"])
    df_gap.to_csv("gap.csv")
    df_correl.to_csv("correl.csv")
    df_limit_correl.to_csv("limit_correl.csv")




