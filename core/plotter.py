
import json
import os

import numpy as np
import pandas as pd
import yaml
from matplotlib import pyplot as plt
from matplotlib.figure import Figure


class AudioMakeGraph(object):
    def __init__(self):
        
        config_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),"config.yaml")
        self.config=self.load_config(config_path)

    def load_config(self,file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            # Sử dụng safe_load để đảm bảo an toàn bảo mật
            config = yaml.safe_load(file)
        return config

    def maker_graph(self,limit_df,data_df,phase):
        self.phase=phase
        limit_df_by_phase=limit_df[limit_df["phase"]==phase].copy()
        self.max_freq=limit_df_by_phase["freq"].max()
        limit_df_by_phase["low_limit"] = pd.to_numeric(limit_df_by_phase["low_limit"], errors="coerce")
        limit_df_by_phase["high_limit"] = pd.to_numeric(limit_df_by_phase["high_limit"], errors="coerce")
        limit_df_by_phase.replace([np.inf, -np.inf], np.nan, inplace=True)
        high_df=limit_df_by_phase[["freq","high_limit"]]
        low_df=limit_df_by_phase[["freq","low_limit"]]
        self.high_df=high_df.dropna(subset=["high_limit"])
        self.low_df=low_df.dropna(subset=["low_limit"])
        #config plot 
        self.y_min=self.config["plot_config"][phase]["min"]
        self.y_max=self.config["plot_config"][phase]["max"]
        self.y_step=self.config["plot_config"][phase]["step"]
        if "fr_norm" or "seal_chirp" in phase:
            self.y_extend=self.y_step
        else:
            self.y_extend=self.y_step/2

        df_graph=data_df[data_df["phase"]==phase].copy()
        #df_graph.to_csv(f"phase/{phase}.csv")
        self.freq=df_graph["freq"]
        
        values = df_graph.iloc[:, 2:]
        
        #values.to_csv(f"phase/{phase}.csv")
        fig=self.__plotter(values)
        

        return fig

        


            
    def __plotter(self,values):
        fig = Figure(figsize=(7, 5), dpi=100)
        fig.patch.set_facecolor("#e6e6e6")
        ax = fig.add_subplot(111)
        ax.set_xlim(90,self.max_freq)
        ax.set_ylim(self.y_min-self.y_extend,self.y_max+self.y_extend) # Thiết lập dải hiển thị từ -60dB đến 60dB
        ax.set_yticks(np.arange(self.y_min,self.y_max+self.y_extend, self.y_step)) 
        
        fig.suptitle(self.phase)    
        ax.plot(self.high_df["freq"],self.high_df["high_limit"], color="red", linewidth=2, label="high_limit")
        ax.plot(self.low_df["freq"],self.low_df["low_limit"], color="red", linewidth=2, label="low_limit")

        for col in values.columns.tolist():
            values[col] = values[col].apply(pd.to_numeric, errors='coerce')
            ax.plot(self.freq,values[col],linewidth=1)
        #ax.plot(self.freq,self.value,color="red", linewidth=2)
        
        
        ax.axhline(y=0,color="#000000",linewidth=1,linestyle="--")
        ax.set_xscale("log")
        
        #ax.set_title(f"Frequency Response - DUT ")
        ax.set_xlabel("Frequency (Hz)")
        #ax.set_ylabel("Level (dB)")
        ax.grid(True, which="both", linestyle="--", linewidth=0.5)
        ax.legend()
        #fig.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.15)
        fig.tight_layout() 
        return fig
    
if __name__ == "__main__":
    draw=AudioMakeGraph()
    
    limit_df=pd.read_csv("limit.csv")
    data_df=pd.read_csv("sum.csv")
    draw.maker_graph(limit_df,data_df,"mic-1_fr")
    

