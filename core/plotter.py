
from itertools import cycle

import matplotlib
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.figure import Figure

from core.load_config import load_yaml
from core.logger import setup_logging
from core.parser import ParserLog

parser=ParserLog()
logger=setup_logging()
matplotlib.use('Agg')
class DrawChart(object):
    def __init__(self):
        self.config=load_yaml()

    def maker_graph(self,df_limit_by_phase,groups,phase,mode="defaut",title=""):
        self.mode=mode
        self.phase=phase
        self.title=title
        self.min_freq=df_limit_by_phase["freq"].min()

        #self.max_freq=df_limit_by_phase["freq"].max()
        ##
        

        if self.mode == "default":
            df_limit_by_phase["low_limit"] = pd.to_numeric(df_limit_by_phase["low_limit"], errors="coerce")
            df_limit_by_phase["high_limit"] = pd.to_numeric(df_limit_by_phase["high_limit"], errors="coerce")
            df_limit_by_phase["low_limit2"] = pd.to_numeric(df_limit_by_phase["low_limit2"], errors="coerce")
            df_limit_by_phase["high_limit2"] = pd.to_numeric(df_limit_by_phase["high_limit2"], errors="coerce")
            df_limit_by_phase.replace([np.inf, -np.inf], np.nan, inplace=True)
            ##
            self.freq_limit=df_limit_by_phase["freq"]
            self.usl=df_limit_by_phase['high_limit']
            self.lsl=df_limit_by_phase['low_limit']
            self.usl2=df_limit_by_phase['high_limit2']
            self.lsl2=df_limit_by_phase['low_limit2']

            self.freq_data=df_limit_by_phase["freq"]
            self.max_freq=df_limit_by_phase["freq"].max()
            #config plot 
            
            

            self.y_min=self.config["plot_config"][phase]["min"]
            self.y_max=self.config["plot_config"][phase]["max"]
            self.y_step=self.config["plot_config"][phase]["step"]
            
            if "fr_norm" or "seal_chirp" in phase:
                self.y_extend=self.y_step
            else:
                self.y_extend=self.y_step/2
        
           
        elif self.mode == "correlation":
            df_limit_by_phase["low_limit"] = pd.to_numeric(df_limit_by_phase["low_limit"], errors="coerce")
            df_limit_by_phase["high_limit"] = pd.to_numeric(df_limit_by_phase["high_limit"], errors="coerce")
            
            df_limit_by_phase.replace([np.inf, -np.inf], np.nan, inplace=True)
            ##
            self.freq_limit=df_limit_by_phase["freq"]
            self.usl=df_limit_by_phase['high_limit']
            self.lsl=df_limit_by_phase['low_limit']
            

            self.freq_data=df_limit_by_phase["freq"]
            self.max_freq=df_limit_by_phase["freq"].max()

            self.y_extend=0
            self.y_min=self.config["plot_config_correlation"][phase]["min"]
            self.y_max=self.config["plot_config_correlation"][phase]["max"]
            self.y_step=self.config["plot_config_correlation"][phase]["step"]
            self.title="- Correlation"
            if "fr_norm" or "seal_chirp" in phase:
                self.y_extend=self.y_step
            else:
                self.y_extend=self.y_step/2

        fig=self.__draw(groups=groups)    
            
        return fig

        



    def __draw(self, groups):
        fig = Figure(figsize=(9, 7), dpi=100)
        fig.patch.set_facecolor("#e6e6e6")
        ax = fig.add_subplot(111)

        ax.set_xlim(self.min_freq-(self.min_freq/5), self.max_freq+(self.max_freq/2))
        ax.set_ylim(self.y_min - self.y_extend, self.y_max + self.y_extend)
        ax.set_yticks(np.arange(self.y_min, self.y_max + self.y_extend, self.y_step))

        fig.suptitle(f"{self.phase} {self.title}")
        if self.mode == "default":
            ax.plot(self.freq_limit, self.usl, color="red", linewidth=1.5,label="limit")
            ax.plot(self.freq_limit, self.lsl, color="red", linewidth=1.5)
            ax.plot(self.freq_limit, self.usl2, color="red", linewidth=1.2,linestyle="--")
            ax.plot(self.freq_limit, self.lsl2, color="red", linewidth=1.2,linestyle="--")
        elif self.mode == "correlation":
            ax.plot(self.freq_limit, self.usl, color="red", linewidth=1.5,label="limit")
            ax.plot(self.freq_limit, self.lsl, color="red", linewidth=1.5)

        color_cycle = cycle(plt.rcParams["axes.prop_cycle"].by_key()["color"])
        
        color_map = {}   # key -> color

        for key, group in groups:
            df_T = group.T.reset_index().rename(columns={"index": "measurement"})
            value_df = parser.df_phase_freq(df_T)

            x = value_df["freq"].to_numpy()
            values_y = value_df.iloc[:, 2:].apply(pd.to_numeric, errors="coerce")

            
            if key not in color_map:
                color_map[key] = next(color_cycle)
                first = True
            else:
                first = False

            for col in values_y.columns:
                ax.plot(
                    x,
                    values_y[col].to_numpy(),
                    linewidth=1.5,
                    color=color_map[key],
                    label=key if first else "_nolegend_"
                )
                first = False

        ax.axhline(y=0, color="#000000", linewidth=1, linestyle="--")
        ax.set_xscale("log")
        ax.set_xlabel("Frequency (Hz)")
        ax.grid(True, which="both", linestyle="--", linewidth=0.5)
        ax.legend()

        return fig

if __name__ == "__main__":
    draw=DrawChart()
    
    limit_df=pd.read_csv("limit.csv")
    data_df=pd.read_csv("sum.csv")
    draw.maker_graph(limit_df,data_df,"mic-1_fr")
    

