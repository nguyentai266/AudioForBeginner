import os
import threading
import tkinter as tk
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from CTkTable import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from tksheet import Sheet

from core.logger import setup_logging
from core.parser import ParserLog
from core.plotter import DrawChart

TITLE_FONT=("Calibri",22,'bold')
CONTENT_FONT=("Calibri",18,'bold')
LABLE_FONT=("Calibri",14,'bold')
BG_COLOR="#00A2E8"

process_data=ParserLog()
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
        toolTab=MainTabView.add("Tool")
        _HomeTabView(homeTab).pack(fill="both",expand=True)
        _ToolTabView(toolTab).pack(fill="both",expand=True)
        
        

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
        
        

        

    def _content_view(self,master):
        search_frame=ctk.CTkFrame(master,fg_color=BG_COLOR)
        search_frame.pack(padx=0,pady=0,fill="both")
        search_frame.grid_columnconfigure(8,weight=1)
        search_frame.grid_rowconfigure(0,weight=1)
        combo_width=250
        btn_width=100
        combo_color_text="#FFFFFF"
        self.label_notice=ctk.CTkLabel(search_frame, text="CÓ LÀM THÌ MỚI CÓ ĂN",anchor="center",font=TITLE_FONT,text_color="#FFFFFF")
        self.label_notice.grid(row=0,column=1,columnspan=8,sticky="ew")
        #search_UI
        ctk.CTkLabel(search_frame,text="Station",font=CONTENT_FONT,text_color=combo_color_text).grid(row=1,column=0,sticky="nsew",padx=10,pady=10)
        self.CBBstation=ctk.CTkComboBox(search_frame,width=combo_width,height=30,values=self.list_station)
        self.CBBstation.grid(row=1,column=1,sticky="nsew",pady=10)

        ctk.CTkLabel(search_frame,text="Dut SN",font=CONTENT_FONT,text_color=combo_color_text).grid(row=1,column=2,sticky="nsew",padx=10,pady=10)
        self.CBBdut_id=ctk.CTkComboBox(search_frame,width=combo_width,height=30,values=self.list_dut,)
        self.CBBdut_id.grid(row=1,column=3,sticky="nsew",pady=10)

        ctk.CTkLabel(search_frame,text="Phase",font=CONTENT_FONT,text_color=combo_color_text).grid(row=1,column=4,sticky="nsew",padx=10,pady=10)
        self.CBBphase=ctk.CTkComboBox(search_frame,width=combo_width,height=30,values=self.list_phase,)
        self.CBBphase.grid(row=1,column=5,sticky="nsew",pady=10)

        ctk.CTkLabel(search_frame,text="Frequency",font=CONTENT_FONT,text_color=combo_color_text).grid(row=1,column=6,sticky="nsew",padx=10,pady=10)
        self.CBBfrequency=ctk.CTkComboBox(search_frame,width=combo_width,height=30,values=self.list_freq,)
        self.CBBfrequency.grid(row=1,column=7,sticky="nsew",pady=10)

        self.search_btn=ctk.CTkButton(search_frame,width=btn_width,text="Search",font=CONTENT_FONT,fg_color="#63FF1D",text_color="#030352",command=self.search,)
        self.search_btn.grid(row=1,column=8,sticky="nsew",padx=10,pady=10)

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
        self.sideBarFrame.rowconfigure(19,weight=1)

        ctk.CTkLabel(self.sideBarFrame, text="Menu", font=TITLE_FONT,fg_color=BG_COLOR,).grid(row=0,column=0,columnspan=3,sticky="",pady=5)
        ctk.CTkLabel(self.sideBarFrame,text="From",font=CONTENT_FONT,fg_color=BG_COLOR).grid(row=1,column=0,columnspan=3,pady=5,sticky='w')
        
        ctk.CTkCheckBox(self.sideBarFrame,text="Folder",font=LABLE_FONT,corner_radius=5,variable=self.check_from_dir,command=lambda:self.check_logic_source(1)).grid(row=2,column=0,sticky="w")
        ctk.CTkCheckBox(self.sideBarFrame,text="File",font=LABLE_FONT,corner_radius=5,variable=self.check_from_file,command=lambda:self.check_logic_source(2)).grid(row=3,column=0,sticky="w")

        ctk.CTkLabel(self.sideBarFrame,text="Input",font=LABLE_FONT,fg_color=BG_COLOR).grid(row=4,column=0,padx=0,pady=0,sticky='w')
        ctk.CTkLabel(self.sideBarFrame,text="Output",font=LABLE_FONT,fg_color=BG_COLOR).grid(row=6,column=0,padx=0,pady=0,sticky="w")
        self.entry_input=ctk.CTkEntry(self.sideBarFrame,placeholder_text="csv log")
        self.entry_input.grid(column=0,row=5,sticky="nesw",columnspan=2)
        self.entry_input.bind("<Return>", self.masterchef)
        self.entry_output=ctk.CTkEntry(self.sideBarFrame,placeholder_text="output")
        self.entry_output.grid(column=0,row=7,sticky='nesw',columnspan=2)
        self.btn_input_path=ctk.CTkButton(self.sideBarFrame,height=25,width=30,corner_radius=5, text="...",command=self.select_file_or_dir)
        self.btn_input_path.grid(column=2,row=5,padx=2,sticky="esn")
        self.btn_output_path=ctk.CTkButton(self.sideBarFrame,height=25,width=30,corner_radius=5, text="...",command=lambda:self.select_dir(mode="output"))
        self.btn_output_path.grid(column=2,row=7,padx=2,sticky="esn")
        ctk.CTkLabel(self.sideBarFrame, text="Mode", font=CONTENT_FONT,fg_color=BG_COLOR,).grid(row=8,column=0,columnspan=3,sticky="w",pady=10)
        
        ctk.CTkCheckBox(self.sideBarFrame,text="DUT Compare",font=LABLE_FONT,corner_radius=5,variable=self.check_dut_compare,command=lambda:self.check_logic_mode(1)).grid(row=9,column=0,sticky="w")
        ctk.CTkCheckBox(self.sideBarFrame,text="Correlation",font=LABLE_FONT,corner_radius=5,variable=self.check_correlation,command=lambda:self.check_logic_mode(2)).grid(row=10,column=0,sticky="w")
        ctk.CTkCheckBox(self.sideBarFrame,text="GRR",font=LABLE_FONT,corner_radius=5,variable=self.check_grr,command=lambda:self.check_logic_mode(3)).grid(row=11,column=0,sticky="w")

        ctk.CTkLabel(self.sideBarFrame,text="Graph By", font=CONTENT_FONT,fg_color=BG_COLOR).grid(row=12,column=0,columnspan=3,sticky="w",pady=10)
        ctk.CTkCheckBox(self.sideBarFrame,text="Station",font=LABLE_FONT,corner_radius=5,variable=self.check_draw_by_station,command=lambda:self.check_logic_draw(1)).grid(row=13,column=0,sticky="w")
        ctk.CTkCheckBox(self.sideBarFrame,text="DUT",font=LABLE_FONT,corner_radius=5,variable=self.check_draw_by_dut,command=lambda:self.check_logic_draw(2)).grid(row=14,column=0,sticky="w")

        self.btn_run=ctk.CTkButton(self.sideBarFrame,text="Run",font=CONTENT_FONT,fg_color="#63FF1D",text_color="#030352",command=lambda:self.run_analyze())
        self.btn_run.grid(row=15,column=0,columnspan=3,sticky="",pady=10)

        self.btn_refresh=ctk.CTkButton(self.sideBarFrame,text="Refresh",font=CONTENT_FONT,fg_color="#63FF1D",text_color="#030352",command=lambda:self.refresh())
        self.btn_refresh.grid(row=16,column=0,columnspan=3,sticky="",pady=10)

        self.btn_export_csv=ctk.CTkButton(self.sideBarFrame,text="Export",font=CONTENT_FONT,fg_color="#63FF1D",text_color="#030352",command=lambda:self.export_csv())
        self.btn_export_csv.grid(row=17,column=0,columnspan=3,sticky="",pady=10)




        self.masterchef_frame=ctk.CTkFrame(self.sideBarFrame,fg_color=BG_COLOR)
        self.masterchef_frame.grid_forget()
        self.btn_chef=ctk.CTkButton(self.masterchef_frame,text="Nấu Ăn",font=CONTENT_FONT,fg_color="#63FF1D",text_color="#030352",command=lambda:self.chef())
        self.btn_chef.grid(row=0,column=0)
    def refresh(self):
        pass
    def export_csv(self):
        path=filedialog.asksaveasfilename(title="Summary csv data",defaultextension=".csv",filetypes=[("CSV files", "*.csv")])
        df_export=self.df_data
        df_export.to_csv(path,index=False)  
        messagebox.showinfo(title="Notice",message=f"Export csv file completed")

    def chef(self):
        summary_file=filedialog.askopenfilename(title="Select csv summary file",filetypes=[("CSV files", "*.csv")])
        output_folder=filedialog.askdirectory(title="Select output log folder",initialdir="/")
        process_data.update_log_files_by_row(summary_file,output_folder)
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
                self.df_limit,self.df_data=process_data.summary_data(path,mode="audio_sort")
                self.df_limit.to_csv("limit.csv",index=False)
                
                self.graph.show_graph(limit_df=self.df_limit,data_df=self.df_data,drawBy=self.draw_by)
                self.table.make_table(self.df_data)
                
            if Path(path).is_file():
                if not os.path.exists("limit.csv"):
                    
                    messagebox.showerror(title="Warning",message="Không tìm thấy file limit, vui lòng chuyển sang folder và chạy một log bất kì để tạo file limit")
                    return
                else:
                    self.df_limit=pd.read_csv("limit.csv")
                    self.df_data=pd.read_csv(path)
                    self.graph.show_graph(limit_df=self.df_limit,data_df=self.df_data,drawBy=self.draw_by)
                    self.table.make_table(self.df_data)

            self.list_station=self.df_data['station_id'].unique().tolist()
            self.CBBstation.configure(values=self.list_station)
            self.list_dut=self.df_data['dut_id'].unique().tolist()
            self.CBBdut_id.configure(values=self.list_dut)
            
            self.list_phase=self.df_limit["phase"].unique().tolist()
            self.CBBphase.configure(values=self.list_phase)
            self.list_freq=self.df_limit['freq'].astype("str").unique().tolist()
            self.CBBfrequency.configure(values=self.list_freq)      
            


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
            self.masterchef_frame.grid(column=0,columnspan=3,row=18,pady=10)
            self.label_notice.configure(text="CHẾ ĐỘ NẤU ĂN")
            messagebox.showwarning(title="Dangerous",message="Đã bật chức năng nấu ăn")
            print("Now you are master chef")
        if self.entry_input.get() == "tat che do nau an":
            self.check_masterchef_mode.set(value=0)
            self.masterchef_frame.grid_forget()
            self.label_notice.configure(text="CÓ LÀM THÌ MỚI CÓ ĂN")
            messagebox.showinfo(title="Notice",message="Đã tắt chức năng nấu ăn")
            print("Now you are normal person")
        else:
            pass




    def search(self):
        pass

class _ToolTabView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)


        

class _GraphTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        

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
        fig, ax = plt.subplots()
        img = mpimg.imread("image.png")
        ax.imshow(img)
        ax.axis("off")
        self.pack_grarh(fig=fig)
      
    def show_graph(self, limit_df, data_df,drawBy):
        self.clear_inner()
        t = threading.Thread(
            target=self._process_and_plot,
            args=(limit_df, data_df),
            daemon=True
        )
        t.start()
        logger.info("Completed Analysis")
    def old_process_and_plot(self, limit_df, data_df):
        phases = limit_df["phase"].unique()
        

        df_t = data_df.T.reset_index()
        df_t = df_t.rename(columns={"index": "measurement"})
        def prepare(phase):
            return phase
        figures = []
        df_sort = process_data.df_phase_freq(df_t)
        with ThreadPoolExecutor(max_workers=4) as executor:
            for phase in executor.map(prepare, phases):
                # VẼ Ở MAIN THREAD
                fig = plotter.maker_graph(
                    limit_df=limit_df,
                    data_df=df_sort,
                    phase=phase
                )
                figures.append(fig)
       
        self.after(0, lambda: self._render_figures(figures))
    
    def _process_and_plot(self, limit_df, data_df):
        phases = limit_df["phase"].unique()

        # TRANSPOSE 1 LẦN DUY NHẤT
        df_t = (
            data_df
            .T
            .reset_index()
            .rename(columns={"index": "measurement"})
        )

        # TIỀN XỬ LÝ DATA (nặng) → song song
        with ThreadPoolExecutor(max_workers=4) as executor:
            future = executor.submit(process_data.df_phase_freq, df_t)
            df_sort = future.result()

        figures = []

        # VẼ → TUẦN TỰ (NHANH HƠN + AN TOÀN)
        for phase in phases:
            fig = plotter.maker_graph(
                limit_df=limit_df,
                data_df=df_sort,
                phase=phase
            )
            figures.append(fig)

        self.after(0, lambda: self._render_figures(figures))


    def _render_figures(self, figures):
        for fig in figures:
            self.pack_grarh(fig)
           


        # ---------------------------
    def pack_grarh(self,fig):
        
        frame = ctk.CTkFrame(self.inner, height=600,width=800)
        frame.pack(fill="both",expand=True,pady=10)
        frame.columnconfigure(0,weight=1)
        frame.rowconfigure(0,weight=1)
        frame.pack_propagate(False)
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().config(width=700)
        canvas.get_tk_widget().grid(column=0,row=0,sticky="nesw")
        #pack(fill="both", expand=True,anchor="center")
    def clear_inner(self):
        for widget in self.inner.winfo_children():
            widget.destroy()
    # ---------------------------
    def _update_scrollregion(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _resize_inner(self, event):
        self.canvas.itemconfig(self.window_id, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")



    

        
class _TableTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        #df=pd.read_csv("C:/Users/V1531673/Desktop/CODE/Audio Basic/summary.csv")
        
        self.parser=ParserLog()
        self.sheet = Sheet(self,data=None,column_headers = None, row_index = None,header_bg = "#f8f9fa", index_bg = "#f8f9fa")


        self.sheet.enable_bindings(('all'))
        self.sheet.pack(expand=True, fill="both")    
    def make_table(self,dataFrame):
        self.df_data=dataFrame
        self.df_data=self.df_data.astype("str")
        data_sheet=self.df_data.values.tolist()
        self.sheet.headers(self.df_data.columns.tolist())
        self.sheet.set_sheet_data(data_sheet)
        self.sheet.refresh()


        