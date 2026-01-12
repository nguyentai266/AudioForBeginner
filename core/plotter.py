
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.figure import Figure


class AudioMakeGraph(object):
    def __init__(self):
        pass
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
        

        df_graph=data_df[data_df["phase"]==phase].copy()
        #df_graph.to_csv(f"phase/{phase}.csv")
        self.freq=df_graph["freq"]
        
        values = df_graph.iloc[:, 2:]
        
        values.to_csv(f"phase/{phase}.csv")
        fig=self.__plotter(values)
        

        return fig

        


            
    def __plotter(self,values):
        fig = Figure(figsize=(7, 2.6), dpi=100)
        fig.patch.set_facecolor("#e6e6e6")
        ax = fig.add_subplot(111)
        ax.set_xlim(80,self.max_freq)
        #ax.set_ylim(40, 120) # Thiết lập dải hiển thị từ -60dB đến 60dB
        ax.set_yticks(np.arange(30, 130, 20)) # Cứ 10 đơn vị vẽ 1 vạch chia
        
        fig.suptitle(self.phase)    
        ax.plot(self.high_df["freq"],self.high_df["high_limit"], color="red", linewidth=2, label="high_limit")
        ax.plot(self.low_df["freq"],self.low_df["low_limit"], color="red", linewidth=2, label="low_limit")

        for col in values.columns.tolist():
            values[col] = values[col].apply(pd.to_numeric, errors='coerce')
            ax.plot(self.freq,values[col],linewidth=1)
        #ax.plot(self.freq,self.value,color="red", linewidth=2)
        
        

        ax.set_xscale("log")
        
        ax.set_title(f"Frequency Response - DUT ")
        ax.set_xlabel("Frequency (Hz)")
        ax.set_ylabel("Level (dB)")
        ax.grid(True, which="both", linestyle="--", linewidth=0.5)
        ax.legend() 
        return fig
    
if __name__ == "__main__":
    draw=AudioMakeGraph()
    
    limit_df=pd.read_csv("limit.csv")
    data_df=pd.read_csv("sum.csv")
    draw.maker_graph(limit_df,data_df,"mic-1_fr")
    

