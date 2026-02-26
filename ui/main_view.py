import os
import re
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tksheet import Sheet

from core.correlation import AudioCorrelation
from core.load_config import load_yaml
from core.logger import setup_logging
from core.parser import ParserLog
from core.plotter import DrawChart

config=load_yaml()
TITLE_FONT=("Calibri",22,'bold')
CONTENT_FONT=("Calibri",18,'bold')
LABLE_FONT=("Calibri",14,'bold')
BG_COLOR="#00A2E8"
correl=AudioCorrelation()
parser=ParserLog()
plotter=DrawChart()
logger=setup_logging()
class MainView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        logger.info('Start Application')
        MainTabView=ctk.CTkTabview(self,anchor="nw",fg_color=BG_COLOR,text_color="black",text_color_disabled="black")
        MainTabView.pack(fill='both',expand=True)
        MainTabView._segmented_button.configure(font=TITLE_FONT)

        homeTab=MainTabView.add("Home")
        #toolTab=MainTabView.add("Tool")
        _HomeTabView(homeTab).pack(fill="both",expand=True)
        #_ToolTabView(toolTab).pack(fill="both",expand=True)
        
        

class _HomeTabView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        #variable
        self.check_from_dir=ctk.IntVar(value=1)
        self.check_from_file=ctk.IntVar(value=0)
        self.check_draw_by_dut=ctk.IntVar(value=0)
        self.check_draw_by_station=ctk.IntVar(value=1)
        self.check_dut_compare=ctk.IntVar(value=1)
        self.check_correlation=ctk.IntVar(value=0)
        self.check_grr=ctk.IntVar(value=0)
        self.check_masterchef_mode=ctk.IntVar(value=0)
        self.check_drawing_or_not=ctk.IntVar(value=1) 
        self.list_dut=[""]
        self.list_station=[""]
        self.list_phase=[""]
        self.list_freq=[""]


        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        sidebar=ctk.CTkFrame(self,fg_color=BG_COLOR,corner_radius=5)
        sidebar.grid(row=0, column=0, sticky="nsew",pady=2,padx=2)
        content = ctk.CTkFrame(self,corner_radius=5)
        content.grid(row=0, column=1, sticky="nsew",pady=2,padx=(0,2))
        self._content_view(content)
        self._side_bar_view(sidebar)

        self.path_input=""
        self.path_output=""

        self.df_data_raw=None
        self.df_limit_raw=None

        self.df_limit_correlation=None
        self.df_data_correlation=None

        self.index_sorted=None
        self.can_refresh=False

        

    def _content_view(self,master):
        search_frame=ctk.CTkFrame(master,fg_color=BG_COLOR)
        search_frame.pack(padx=0,pady=0,fill="both")
        search_frame.grid_columnconfigure(1,weight=1)
        search_frame.grid_rowconfigure(0,weight=1)
        combo_width=280
        btn_width=250
        combo_color_text="#FFFFFF"
        self.label_notice=ctk.CTkLabel(search_frame, text="CÓ LÀM THÌ MỚI CÓ ĂN",anchor="center",font=TITLE_FONT,text_color="#FFFFFF")
        self.label_notice.grid(row=0,column=1,columnspan=8,sticky="ew")
        #search_UI
        ctk.CTkLabel(search_frame,text="Station ID",font=CONTENT_FONT,text_color=combo_color_text).grid(row=1,column=0,sticky="nsew",padx=10,pady=10)
        self.CBBstation=ctk.CTkComboBox(search_frame,width=combo_width,height=30,values=self.list_station,font=CONTENT_FONT)
        self.CBBstation.grid(row=1,column=1,sticky="nsew",pady=10)

        ctk.CTkLabel(search_frame,text="Device SN",font=CONTENT_FONT,text_color=combo_color_text).grid(row=1,column=2,sticky="nsew",padx=10,pady=10)
        self.CBBdut_id=ctk.CTkComboBox(search_frame,width=combo_width,height=30,values=self.list_dut,font=CONTENT_FONT)
        self.CBBdut_id.grid(row=1,column=3,sticky="nsew",pady=10)

        ctk.CTkLabel(search_frame,text="Phase Selected",font=CONTENT_FONT,text_color=combo_color_text).grid(row=1,column=4,sticky="nsew",padx=10,pady=10)
        self.CBBphase=ctk.CTkComboBox(search_frame,width=combo_width,height=30,values=self.list_phase,font=CONTENT_FONT)
        self.CBBphase.grid(row=1,column=5,sticky="nsew",pady=10)

        
        

        self.search_btn=ctk.CTkButton(search_frame,width=btn_width,text="Search",font=CONTENT_FONT,fg_color="#63FF1D",text_color="#030352",command=self.search,)
        self.search_btn.grid(row=1,column=6,sticky="nsew",padx=10,pady=10)

        tabview=ctk.CTkTabview(master,anchor="nw",fg_color=BG_COLOR,text_color="black",text_color_disabled="black")
        tabview.pack(fill='both',expand=True)
        tabview._segmented_button.configure(font=CONTENT_FONT)
        graph_tab = tabview.add("Graph")
        table_tab = tabview.add("Table")
        

        self.graph=_GraphTab(graph_tab)
        self.graph.pack(fill="both", expand=True)
        self.table=_TableTab(table_tab)
        self.table.pack(fill="both", expand=True)
        
        
    def _side_bar_view(self,master):

        
        self.sideBarFrame=ctk.CTkFrame(master,fg_color=BG_COLOR)
        self.sideBarFrame.pack(fill='both',expand=True)
        self.sideBarFrame.columnconfigure(1,weight=1)
        self.sideBarFrame.rowconfigure(20,weight=1)

        ctk.CTkLabel(self.sideBarFrame, text="Menu", font=TITLE_FONT,fg_color=BG_COLOR,).grid(row=0,column=0,columnspan=3,sticky="",pady=5)
        ctk.CTkLabel(self.sideBarFrame,text="From",font=CONTENT_FONT,fg_color=BG_COLOR).grid(row=1,column=0,columnspan=3,pady=5,sticky='w')
        
        ctk.CTkCheckBox(self.sideBarFrame,text="Folder",font=LABLE_FONT,corner_radius=5,variable=self.check_from_dir,command=lambda:self.check_logic_source(1)).grid(row=2,column=0,sticky="w")
        ctk.CTkCheckBox(self.sideBarFrame,text="File",font=LABLE_FONT,corner_radius=5,variable=self.check_from_file,command=lambda:self.check_logic_source(2)).grid(row=3,column=0,sticky="w")

        ctk.CTkLabel(self.sideBarFrame,text="Input",font=LABLE_FONT,fg_color=BG_COLOR).grid(row=4,column=0,padx=0,pady=0,sticky='w')
        #input
        self.entry_input=ctk.CTkEntry(self.sideBarFrame,placeholder_text="Input folder CSV log or CSV file")
        self.entry_input.grid(column=0,row=5,sticky="nesw",columnspan=2)
        self.entry_input.bind("<Return>", self.masterchef)
        self.btn_input_path=ctk.CTkButton(self.sideBarFrame,height=25,width=30,corner_radius=5, text="...",command=self.select_file_or_dir)
        self.btn_input_path.grid(column=2,row=5,padx=2,sticky="esn")
        
        #1 mode
        #2 drawing
        ctk.CTkLabel(self.sideBarFrame,text="Drawing",font=CONTENT_FONT,fg_color=BG_COLOR).grid(row=7,column=0,padx=0,pady=0,sticky="w")
        ctk.CTkCheckBox(self.sideBarFrame,text="Yes/No",font=LABLE_FONT,corner_radius=5,variable=self.check_drawing_or_not).grid(row=8,column=0,sticky="w")
        ctk.CTkCheckBox(self.sideBarFrame,text="By Station",font=LABLE_FONT,corner_radius=5,variable=self.check_draw_by_station,command=lambda:self.check_logic_draw(1)).grid(row=9,column=0,sticky="w")
        ctk.CTkCheckBox(self.sideBarFrame,text="By Device",font=LABLE_FONT,corner_radius=5,variable=self.check_draw_by_dut,command=lambda:self.check_logic_draw(2)).grid(row=10,column=0,sticky="w")

        #3 device compare
        ctk.CTkLabel(self.sideBarFrame, text="Mode", font=CONTENT_FONT,fg_color=BG_COLOR,).grid(row=11,column=0,columnspan=3,sticky="w",pady=0)

        ctk.CTkCheckBox(self.sideBarFrame,text="Device Compare",font=LABLE_FONT,corner_radius=5,variable=self.check_dut_compare,command=lambda:self.check_logic_mode(1)).grid(row=12,column=0,sticky="w")
        #4 by dut or by station
        #ctk.CTkLabel(self.sideBarFrame,text="Graph By", font=CONTENT_FONT,fg_color=BG_COLOR).grid(row=10,column=0,columnspan=3,sticky="w",pady=10)
        
        #5 corelation
        ctk.CTkCheckBox(self.sideBarFrame,text="Correlation",font=LABLE_FONT,corner_radius=5,variable=self.check_correlation,command=lambda:self.check_logic_mode(2)).grid(row=13,column=0,sticky="w")
        #6 grr
        ctk.CTkCheckBox(self.sideBarFrame,text="GRR",font=LABLE_FONT,corner_radius=5,variable=self.check_grr,command=lambda:self.check_logic_mode(3)).grid(row=14,column=0,sticky="w")
        
        
        
        
        

        

        self.btn_run=ctk.CTkButton(self.sideBarFrame,text="Run",font=CONTENT_FONT,fg_color="#63FF1D",text_color="#030352",command=lambda:self.run_analyze())
        self.btn_run.grid(row=15,column=0,columnspan=3,sticky="",pady=10)

        self.btn_refresh=ctk.CTkButton(self.sideBarFrame,text="Refresh",font=CONTENT_FONT,fg_color="#63FF1D",text_color="#030352",command=lambda:self.refresh())
        self.btn_refresh.grid(row=16,column=0,columnspan=3,sticky="",pady=10)

        self.btn_export_csv=ctk.CTkButton(self.sideBarFrame,text="Export CSV",font=CONTENT_FONT,fg_color="#63FF1D",text_color="#030352",command=lambda:self.export_csv())
        self.btn_export_csv.grid(row=17,column=0,columnspan=3,sticky="",pady=10)
        self.btn_export_pdf=ctk.CTkButton(self.sideBarFrame,text="Export PDF",font=CONTENT_FONT,fg_color="#63FF1D",text_color="#030352",command=lambda:self.export_pdf())
        self.btn_export_pdf.grid(row=18,column=0,columnspan=3,sticky="",pady=10)




        self.masterchef_frame=ctk.CTkFrame(self.sideBarFrame,fg_color=BG_COLOR)
        self.masterchef_frame.grid_forget()
        self.btn_chef=ctk.CTkButton(self.masterchef_frame,text="Nấu Ăn",font=CONTENT_FONT,fg_color="#63FF1D",text_color="#030352",command=lambda:self.chef())
        self.btn_chef.grid(row=0,column=0)

    def refresh(self):
        if self.can_refresh == True:

            self.df_sorted=self.table.get_data_from_sheet()

            self.df_sorted.index = self.index_sorted
            self.df_data_raw.update(self.df_sorted)
            self.table.make_table(self.df_data_raw)
            self.logic_running_analysis()
            messagebox.showinfo(title="Completed",message="Refresh OK")
        else:
            return
        #messagebox.showwarning(title="Warning",message="Chưa phát triển, hãy dùng những cái có sẵn")

    def export_csv(self):
        path=filedialog.asksaveasfilename(title="Summary csv data",defaultextension=".csv",filetypes=[("CSV files", "*.csv")])
        self.df_data_raw.to_csv(path,index=False)  
        messagebox.showinfo(title="Notice",message=f"Export CSV file complete.")
    def export_pdf(self):
        path=filedialog.asksaveasfilename(title="Summary PDF Data",defaultextension=".pdf",filetypes=[("PDF files", "*.pdf")])
        self.graph.export_pdf(path)
        messagebox.showinfo(title="Notice",message=f"Export PDF file complete.")

    def chef(self):
        summary_file=filedialog.askopenfilename(title="Select csv summary file",filetypes=[("CSV files", "*.csv")])
        output_folder=filedialog.askdirectory(title="Select output log folder",initialdir="/")
        parser.update_log_files_by_row(summary_file,output_folder)
        messagebox.showwarning(title="Warning",message="Đã nấu xong món")
        
        
    def mode_draw(self):
        if self.check_draw_by_dut.get() == 1:
            self.draw_by="dut_id"
        if self.check_draw_by_station.get() == 1:
            self.draw_by="station_id"

    def run_analyze(self):
        path=self.entry_input.get()
        logger.info("Start analysis")
        self.mode_draw()
        logger.info(f"Draw by {self.draw_by}")
        if path == "":
            messagebox.showinfo(title="Notice",message="Please input data log")
        if path != "":     
            if Path(path).is_dir():
                self.df_limit_raw,self.df_data_raw=parser.summary_data(path,mode=config["sorting_mode"])
                self.df_limit_raw.to_csv("limit.csv",index=False)
                
            if Path(path).is_file():
                if not os.path.exists("limit.csv"):
                    messagebox.showerror(title="Warning",message="Không tìm thấy file limit, vui lòng chuyển sang folder và chạy một log bất kì để tạo file limit")
                    return
                else:
                    self.df_limit_raw=pd.read_csv("limit.csv")
                    self.df_data_raw=pd.read_csv(path)
            

            self.list_station=self.df_data_raw['station_id'].unique().tolist()
            self.CBBstation.configure(values=self.list_station)
            self.list_dut=self.df_data_raw['dut_id'].unique().tolist()
            self.CBBdut_id.configure(values=self.list_dut)
            
            self.list_phase=self.df_limit_raw["phase"].unique().tolist()
            self.CBBphase.configure(values=self.list_phase)
            #self.list_freq=self.df_limit_raw['freq'].astype("str").unique().tolist()
            #self.CBBfrequency.configure(values=self.list_freq)

            self.logic_running_analysis()

    def logic_running_analysis(self):
        if self.check_dut_compare.get() == 1 :
            logger.info("Run mode Compare")
            self.dut_compare()
            
        if self.check_correlation.get() == 1:
            logger.info("Run mode Correlation")
            self.correlation()
            
        if self.check_grr.get() == 1:
            logger.info("Run mode GRR")
            self.grr()

    def dut_compare(self):
        if self.check_drawing_or_not.get() == 1:
            self.graph.show_graph(limit_df=self.df_limit_raw,
                                data_df=self.df_data_raw,
                                draw_by=self.draw_by,
                                mode="dut_compare")
        self.table.make_table(self.df_data_raw)
    def correlation(self):
        self.avg_df,self.gap_df,self.gap_limit_df = correl.correlation(dataFrame_limit=self.df_limit_raw,
                                                                       dataFrame_raw=self.df_data_raw,
                                                                       limit_correl_config=config["limit_correl"])
        if self.check_drawing_or_not.get() == 1:
            self.graph.show_graph(limit_df=self.df_limit_raw,
                                correl_limit_df=self.gap_limit_df,
                                data_df=self.avg_df,
                                correl_df=self.gap_df,
                                draw_by="station_id",
                                mode="correlation")
                                
        self.table.make_table(self.df_data_raw)
    def grr(self):
        messagebox.showwarning(title="Warning",message="Chưa phát triển, hãy dùng những cái có sẵn")

    def select_file_or_dir(self):
        if self.check_from_dir.get()==1:
            self.select_dir(mode="input")
        if self.check_from_file.get()==1:
            self.select_dir(mode="fromfile")


    def check_logic_source(self, selection):
    # Tắt tất cả các nút
        self.check_from_dir.set(0)
        self.check_from_file.set(0)
        # Chỉ bật lại nút vừa nhấn
        if selection == 1: self.check_from_dir.set(1)
        if selection == 2: self.check_from_file.set(1)

    def check_logic_mode(self, selection):
    # Tắt tất cả các nút
        self.check_dut_compare.set(0)
        self.check_correlation.set(0)
        self.check_grr.set(0)

        # Chỉ bật lại nút vừa nhấn
        if selection == 1: self.check_dut_compare.set(1)
        if selection == 2: self.check_correlation.set(1)
        if selection == 3: self.check_grr.set(1)

    def check_logic_draw(self,selection):
        self.check_draw_by_dut.set(0)
        self.check_draw_by_station.set(0)
        if selection == 1: self.check_draw_by_station.set(1)
        if selection == 2: self.check_draw_by_dut.set(1)


    def select_dir(self,mode="input"):
        if mode =="fromfile":
            path=filedialog.askopenfilename(title="Select csv summary file",filetypes=[("CSV files", "*.csv")])
            if path:
                self.entry_input.delete(0,'end')
                self.entry_input.insert(0,path)
        if mode =="input":
            path=filedialog.askdirectory(title="Select log folder",initialdir="/")
            if path:
                self.entry_input.delete(0,'end')
                self.entry_input.insert(0,path)
        if mode =="output":
            path=filedialog.askdirectory(title="Select output folder",initialdir="/")
            if path:
                self.entry_output.delete(0,'end')
                self.entry_output.insert(0,path)

    def masterchef(self,event=None):
        if self.entry_input.get() == "bat che do nau an":
            self.check_masterchef_mode.set(value=1)
            self.masterchef_frame.grid(column=0,columnspan=3,row=19,pady=10)
            self.label_notice.configure(text="CHẾ ĐỘ NẤU ĂN")
            messagebox.showwarning(title="Dangerous",message="Đã bật chức năng nấu ăn")
            logger.info("Now you are master chef")
        if self.entry_input.get() == "tat che do nau an":
            self.check_masterchef_mode.set(value=0)
            self.masterchef_frame.grid_forget()
            self.label_notice.configure(text="CÓ LÀM THÌ MỚI CÓ ĂN")
            messagebox.showinfo(title="Notice",message="Đã tắt chức năng nấu ăn")
            logger.info("Now you are normal person")
        else:
            pass

    def search(self):
        self.station=self.CBBstation.get()
        self.dut_sn=self.CBBdut_id.get()
        self.phase_selected=self.CBBphase.get()
        df_phase_filter=self.df_data_raw.filter(regex=rf"^({re.escape(self.phase_selected)}_\d+(\.\d+)?|station_id|dut_id)$")
        if not self.phase_selected:
            self.can_refresh=False
            return
        else:
            self.can_refresh=True
            if self.station:
                grouped=df_phase_filter.groupby('station_id')
                for key,group in grouped:
                    if key == self.station:
                        self.index_sorted=group.index.to_list()
                        self.table.make_table(group)
            elif self.dut_sn:
                grouped=df_phase_filter.groupby('dut_id')
                for key,group in grouped:
                    if key == self.dut_sn:
                        self.index_sorted=group.index.to_list()
                        self.table.make_table(group)
            elif self.dut_sn and self.station:
                grouped=df_phase_filter.groupby('dut_id')
                for key,group in grouped:
                    if key == self.dut_sn:
                        groups2=group.groupby('station_id')
                        for station,g in groups2:
                            if station == self.station:
                                self.index_sorted=g.index.to_list()
                                self.table.make_table(g)

            else:
                self.index_sorted=df_phase_filter.index.to_list()
                self.table.make_table(df_phase_filter)


        #messagebox.showwarning(title="Warning",message="Chưa phát triển, hãy dùng những cái có sẵn")

class _ToolTabView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)


        

class _GraphTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.figures=[]
        container=ctk.CTkFrame(self)
        container.pack(fill="both",expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.canvas = tk.Canvas(
            container,
            bg="#242424",
            highlightthickness=1
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # ===== scrollbar dọc =====
        v_scroll = ctk.CTkScrollbar(
            container,
            orientation="vertical",
            command=self.canvas.yview
        )
        v_scroll.grid(row=0, column=1, sticky="ns")

        self.canvas.configure(yscrollcommand=v_scroll.set)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        # ===== inner frame =====
        self.inner = ctk.CTkFrame(self.canvas)
        self.window_id = self.canvas.create_window(
            (0, 0),
            window=self.inner,
            anchor="nw"
        )

        self.inner.bind("<Configure>", self._update_scrollregion)
        self.canvas.bind("<Configure>", self._resize_inner)
        self.show_img()

    def show_img(self):
        
        if os.path.exists("core/image.png"):
            fig, ax = plt.subplots()
            img = mpimg.imread("core/image.png")
            ax.imshow(img)
            ax.axis("off")
            
            self.pack_grarh(fig=fig)
        else: return
      
    def show_graph(self, limit_df, data_df,draw_by,correl_limit_df=None,correl_df=None,mode="dut_compare"):
        
        self.draw_by=draw_by
        self.limit_df=limit_df
        self.data_df=data_df
        self.correl_limit=correl_limit_df
        self.correl_data_df=correl_df
        self.mode=mode

        self._process_and_plot()
        #logger.info("Completed Analysis")
    
    def _process_and_plot(self):
        
        if self.mode == "dut_compare":
            phases = self.limit_df["phase"].unique()
            for phase in phases:
                df_phase_filter=self.data_df.filter(regex=rf"^({re.escape(phase)}_\d+(\.\d+)?|{re.escape(self.draw_by)})$").copy()
                limit_df_by_phase=self.limit_df[self.limit_df["phase"]==phase].copy()
                groups_data=parser.group_data(df_phase_filter,groupBy=self.draw_by)
                
                fig = plotter.maker_graph(
                    df_limit_by_phase=limit_df_by_phase,
                    groups=groups_data,  # gui vao dataframe dang long
                    phase=phase,
                    mode="default")
                self.figures.append(fig)
            logger.info("draw finish")
        elif self.mode == "correlation":
            self.draw_by = "station_id"
            # Lấy danh sách phase từ bảng limit correlation
            phases = self.limit_df["phase"].unique()
            for phase in phases:
                df_phase_filter=self.data_df.filter(regex=rf"^({re.escape(phase)}_\d+(\.\d+)?|{re.escape(self.draw_by)})$").copy()
                limit_df_by_phase=self.limit_df[self.limit_df["phase"]==phase].copy()
                groups_data=parser.group_data(df_phase_filter,groupBy=self.draw_by)
                
                fig = plotter.maker_graph(
                    df_limit_by_phase=limit_df_by_phase,
                    groups=groups_data,  # gui vao dataframe dang long
                    phase=phase,
                    mode="default",
                    title=" - Average")
                self.figures.append(fig)
                
                df_phase_correl_filter=self.correl_data_df.filter(regex=rf"^({re.escape(phase)}_\d+(\.\d+)?|{re.escape(self.draw_by)})$").copy()
               
                df_phase_correl_limit=self.correl_limit[self.correl_limit["phase"]==phase].copy()
                groups_data_correl=parser.group_data(df_phase_correl_filter,groupBy=self.draw_by)
                fig_correl = plotter.maker_graph(
                    df_limit_by_phase=df_phase_correl_limit,
                    groups=groups_data_correl,  # gui vao dataframe dang long
                    phase=phase,
                    mode="correlation")
                self.figures.append(fig_correl)
            logger.info("draw finish")
        self._render_figures(self.figures)
        #self.after(0, lambda: self._render_figures(self.figures))


    def _render_figures(self, figures):
        self.clear_inner()
        for fig in figures:
            if fig == figures[-1]:
                self.pack_grarh(fig)
                logger.info("Completed Analyze")
            else:
                self.pack_grarh(fig)


        # ---------------------------
    def pack_grarh(self,fig,height=600,width=800):
        
        frame = ctk.CTkFrame(self.inner, height,width)
        frame.pack(fill="both",expand=True,pady=10)
        
        frame.pack_propagate(False)
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw_idle()
        #canvas.get_tk_widget().config(width=700)
        canvas.get_tk_widget().grid(column=0,row=0,sticky="nesw")
        frame.columnconfigure(0,weight=1)
        frame.rowconfigure(0,weight=1)
        #pack(fill="both", expand=True,anchor="center")
    def clear_inner(self):
        for widget in self.inner.winfo_children():
            if isinstance(widget,ctk.CTkFrame):
                widget.destroy()
        self.figures=[]
    # ---------------------------
    def _update_scrollregion(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _resize_inner(self, event):
        self.canvas.itemconfig(self.window_id, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def export_pdf(self,path):
        if not self.figures:
            messagebox.showerror(title="Error",message="No data for export pdf.")
        else:
            with PdfPages(path) as pdf:
                for fig in self.figures:
                    pdf.savefig(fig,bbox_inches='tight')
            logger.info("Export PDF completed")
    
        

    

        
class _TableTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        #df=pd.read_csv("C:/Users/V1531673/Desktop/CODE/Audio Basic/summary.csv")
        
        
        self.sheet = Sheet(self,data=None,column_headers = None, row_index = None,header_bg = "#f8f9fa", index_bg = "#f8f9fa")


        self.sheet.enable_bindings(('all'))
       
        self.sheet.pack(expand=True, fill="both")    
    def make_table(self,dataFrame):
        self.df_data=dataFrame
        self.df_data=self.df_data.astype("str")
        headers=self.df_data.columns.tolist()
        data_sheet=self.df_data.values.tolist()
        full_sheet_data=[headers]+data_sheet
        #self.sheet.headers(headers)
        self.sheet.set_sheet_data(full_sheet_data)
        self.sheet.set_all_column_widths()
        self.sheet.refresh()

    def get_data_from_sheet(self):
        headers=self.sheet.headers()
        data=self.sheet.get_sheet_data()
        df_edit=pd.DataFrame(data=data[1:],columns=data[0])
        return df_edit
    
    
        