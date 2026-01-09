import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk
import numpy as np
import pandas as pd
from CTkTable import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from tksheet import Sheet

from core.csv_parser import log_parser

TITLE_FONT=("Calibri",22,'bold')
CONTENT_FONT=("Calibri",18,'bold')
LABLE_FONT=("Calibri",14,'bold')
BG_COLOR="#00A2E8"
class MainView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
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
        self.check_dut_compare=ctk.IntVar(value=1)
        self.check_correlation=ctk.IntVar(value=0)
        self.check_grr=ctk.IntVar(value=0)
        self.check_masterchef_mode=ctk.IntVar(value=0)


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
        self.station=ctk.CTkComboBox(search_frame,width=combo_width,height=30,values=[""])
        self.station.grid(row=1,column=1,sticky="nsew",pady=10)

        ctk.CTkLabel(search_frame,text="Dut SN",font=CONTENT_FONT,text_color=combo_color_text).grid(row=1,column=2,sticky="nsew",padx=10,pady=10)
        self.dut_id=ctk.CTkComboBox(search_frame,width=combo_width,height=30,values=[""],)
        self.dut_id.grid(row=1,column=3,sticky="nsew",pady=10)

        ctk.CTkLabel(search_frame,text="Phase",font=CONTENT_FONT,text_color=combo_color_text).grid(row=1,column=4,sticky="nsew",padx=10,pady=10)
        self.phase_select=ctk.CTkComboBox(search_frame,width=combo_width,height=30,values=[""],)
        self.phase_select.grid(row=1,column=5,sticky="nsew",pady=10)

        ctk.CTkLabel(search_frame,text="Frequency",font=CONTENT_FONT,text_color=combo_color_text).grid(row=1,column=6,sticky="nsew",padx=10,pady=10)
        self.freq_select=ctk.CTkComboBox(search_frame,width=combo_width,height=30,values=[""],)
        self.freq_select.grid(row=1,column=7,sticky="nsew",pady=10)

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
        self.process_data=log_parser()
        self.select_phase=self.process_data.select_phases
    def _side_bar_view(self,master):

        
        self.sideBarFrame=ctk.CTkFrame(master,fg_color=BG_COLOR)
        self.sideBarFrame.pack(fill='both',expand=True)
        self.sideBarFrame.columnconfigure(1,weight=1)
        self.sideBarFrame.rowconfigure(16,weight=1)

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

        self.btn_run=ctk.CTkButton(self.sideBarFrame,text="Run",font=CONTENT_FONT,fg_color="#63FF1D",text_color="#030352",command=lambda:self.update_sheet())
        self.btn_run.grid(row=12,column=0,columnspan=3,sticky="",pady=10)

        self.btn_refresh=ctk.CTkButton(self.sideBarFrame,text="Refresh",font=CONTENT_FONT,fg_color="#63FF1D",text_color="#030352",command=lambda:self.refresh())
        self.btn_refresh.grid(row=13,column=0,columnspan=3,sticky="",pady=10)

        self.btn_export_csv=ctk.CTkButton(self.sideBarFrame,text="Export",font=CONTENT_FONT,fg_color="#63FF1D",text_color="#030352",command=lambda:self.export_csv())
        self.btn_export_csv.grid(row=14,column=0,columnspan=3,sticky="",pady=10)




        self.masterchef_frame=ctk.CTkFrame(self.sideBarFrame,fg_color=BG_COLOR)
        self.masterchef_frame.grid_forget()
        self.btn_chef=ctk.CTkButton(self.masterchef_frame,text="Nấu Ăn",font=CONTENT_FONT,fg_color="#63FF1D",text_color="#030352",command=lambda:self.chef())
        self.btn_chef.grid(row=0,column=0)
    def refresh(self):
        pass
    def export_csv(self):
        path=filedialog.asksaveasfilename(title="Summary csv data",defaultextension=".csv",filetypes=[("CSV files", "*.csv")])
        df_export=self.df_data.T
        df_export.to_csv(path,index=True)  
        messagebox.showinfo(title="Notice",message=f"Export csv file completed")

    def chef(self):
        summary_file=filedialog.askopenfilename(title="Select csv summary file",filetypes=[("CSV files", "*.csv")])
        output_folder=filedialog.askdirectory(title="Select output log folder",initialdir="/")
        self.process_data.update_log_files(summary_file,output_folder)
        messagebox.showwarning(title="Warning",message="Đã nấu xong món")
        
        


    def update_sheet(self):
        path=self.entry_input.get()
        if path == "":
            messagebox.showinfo(title="Notice",message="Please input data log")
        if path != "":
            if Path(path).is_dir():
                self.df_limit,self.df_data=self.process_data.summary_data(path,mode="sort")
                
                self.table.make_table(self.df_data)
            if Path(path).is_file():
                self.df_data=pd.read_csv(path,index_col=0)
                
                
                self.table.make_table(self.df_data.T)
                
        



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
        if self.entry_input.get() == "bat chuc nang nau an":
            self.check_masterchef_mode.set(value=1)
            self.masterchef_frame.grid(column=0,columnspan=3,row=15,pady=10)
            self.label_notice.configure(text="CHẾ ĐỘ NẤU ĂN")
            messagebox.showwarning(title="Dangerous",message="Đã bật chức năng nấu ăn")
            print("Now you are master chef")
        if self.entry_input.get() == "tat chuc nang nau an":
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

        # ===== inner frame =====
        self.inner = ctk.CTkFrame(self.canvas)
        self.window_id = self.canvas.create_window(
            (0, 0),
            window=self.inner,
            anchor="nw"
        )

        self.inner.bind("<Configure>", self._update_scrollregion)
        self.canvas.bind("<Configure>", self._resize_inner)

        # ===== tạo nhiều biểu đồ =====
        for i in range(8):
            self.add_plot(i + 1)

    # ---------------------------
    def add_plot(self, index):
        frame = ctk.CTkFrame(self.inner, height=800)
        frame.pack(fill="both", padx=20, pady=15)
        frame.pack_propagate(False)

        fig = Figure(figsize=(7, 2.6), dpi=100)
        fig.patch.set_facecolor("#e6e6e6")
        ax = fig.add_subplot(111)

        freq = np.logspace(2, 4, 100)
        y = 5 / (freq / 100) + np.random.uniform(0.05, 0.2)

        ax.plot(freq, y, label=f"DUT {index}")
        ax.axhline(1.0, color="red", linewidth=2, label="limit")

        ax.set_xscale("log")
        ax.set_title(f"Frequency Response - DUT {index}")
        ax.set_xlabel("Frequency (Hz)")
        ax.set_ylabel("Level (dB)")
        ax.grid(True, which="both", linestyle="--", linewidth=0.5)
        ax.legend()

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    # ---------------------------
    def _update_scrollregion(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _resize_inner(self, event):
        self.canvas.itemconfig(self.window_id, width=event.width)
        

        
class _TableTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        #df=pd.read_csv("C:/Users/V1531673/Desktop/CODE/Audio Basic/summary.csv")
        
        self.parser=log_parser()
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


        