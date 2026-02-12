import datetime
import re

from matplotlib.backends.backend_pdf import PdfPages

from core.correlation import AudioCorrelation
from core.load_config import load_yaml
from core.parser import ParserLog
from core.plotter import DrawChart

config = load_yaml()
parser = ParserLog()
correlation= AudioCorrelation()
plotter= DrawChart()

def export_pdf(path,figures):
    if not figures:
        print("error")
    else:
        with PdfPages(path) as pdf:
            for fig in figures:
                fig.set_size_inches(12,6)
                fig.tight_layout()
                pdf.savefig(fig,bbox_inches='tight',pad_inches=0.1)

if __name__ =="__main__":
    now=datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    path="input_source/"
    try:
        df_limit,df_data=parser.summary_data(path,mode="audio_sort")
        df_avg,correl_df,limit_correl=correlation.correlation(dataFrame_limit=df_limit,dataFrame_raw=df_data,limit_correl_config=config["limit_correl"])
        figures=[]
        phases = df_limit["phase"].unique()
        for phase in phases:
            df_phase_filter=df_avg.filter(regex=rf"^({re.escape(phase)}_\d+(\.\d+)?|station_id)$").copy()
            limit_df_by_phase=df_limit[df_limit["phase"]==phase].copy()
            groups_data=parser.group_data(df_phase_filter,groupBy="station_id")
            fig = plotter.maker_graph(
                df_limit_by_phase=limit_df_by_phase,
                groups=groups_data,
                phase=phase,
                mode="default",
                title="- Average")
            figures.append(fig)
            
            df_phase_correl_filter=correl_df.filter(regex=rf"^({re.escape(phase)}_\d+(\.\d+)?|station_id)$").copy()
            df_phase_correl_limit=limit_correl[limit_correl["phase"]==phase].copy()
            groups_data_correl=parser.group_data(df_phase_correl_filter,groupBy="station_id")
            fig_correl = plotter.maker_graph(
                df_limit_by_phase=df_phase_correl_limit,
                groups=groups_data_correl,
                phase=phase,
                mode="correlation")
            figures.append(fig_correl)

        file=f"Output/correlation_audio{now}.pdf"
        export_pdf(figures=figures,path=file)
        #df_data.to_csv(f"Raw_data_{now}.csv")
        print("Completed")
    except Exception as e:
        print("error data")
        print(e)

