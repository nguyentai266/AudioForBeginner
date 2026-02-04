import os
import shutil
import tkinter as tk
from ftplib import FTP
from tkinter import filedialog, messagebox, ttk

import numpy as np
import pandas as pd

from core.parser import ParserLog


class RFAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("RF support tool - V1.0")
        self.root.geometry("1500x950")
        
        self.parser = ParserLog() 
        
        self.source_path = tk.StringVar(value="")
        self.output_path = tk.StringVar(value="") 
        
        # --- CẤU HÌNH FTP ---
        self.ftp_host = tk.StringVar(value="10.239.73.213")
        self.ftp_user = tk.StringVar(value="Mars")
        self.ftp_pass = tk.StringVar(value="GGFTP@22")
        self.ftp_dir = tk.StringVar(value="/.Enzo/log")
        
        self.item_search_var = tk.StringVar()
        self.mode_var = tk.StringVar(value="GRR") 
        self.target_str = tk.StringVar(value="17.0")
        self.delta_str = tk.StringVar(value="0.5")
        
        self.df_summary = None
        self.measure_cols = [] 

        self._setup_ui()

    def _setup_ui(self):
        # --- 1. TOP PANEL ---
        top_frame = tk.Frame(self.root, bg="#f8f9fa", padx=10, pady=10, bd=1, relief="ridge")
        top_frame.pack(side="top", fill="x")
        
        input_row = tk.Frame(top_frame, bg="#f8f9fa")
        input_row.pack(fill="x", pady=2)
        tk.Label(input_row, text="📁 Input Dir: ", bg="#f8f9fa", font=("Arial", 9, "bold"), width=12, anchor="w").pack(side="left")
        tk.Entry(input_row, textvariable=self.source_path, width=80).pack(side="left", padx=5)
        tk.Button(input_row, text="...", command=lambda: self._browse_dir(self.source_path), bg="#6c757d", fg="white", width=8).pack(side="left")
        
        output_row = tk.Frame(top_frame, bg="#f8f9fa")
        output_row.pack(fill="x", pady=2)
        tk.Label(output_row, text="📂 Output Dir:", bg="#f8f9fa", font=("Arial", 9, "bold"), width=12, anchor="w").pack(side="left")
        tk.Entry(output_row, textvariable=self.output_path, width=80).pack(side="left", padx=5)
        tk.Button(output_row, text="...", command=lambda: self._browse_dir(self.output_path), bg="#6c757d", fg="white", width=8).pack(side="left")

        ftp_row = tk.Frame(top_frame, bg="#f8f9fa")
        ftp_row.pack(fill="x", pady=5)
        tk.Label(ftp_row, text="FTP Host:", bg="#f8f9fa", font=("Arial", 9, "bold"), width=12, anchor="w").pack(side="left")
        tk.Entry(ftp_row, textvariable=self.ftp_host, width=20).pack(side="left", padx=5)
        tk.Label(ftp_row, text="User:", bg="#f8f9fa").pack(side="left", padx=2)
        tk.Entry(ftp_row, textvariable=self.ftp_user, width=15).pack(side="left", padx=5)
        tk.Label(ftp_row, text="Password:", bg="#f8f9fa").pack(side="left", padx=2)
        tk.Entry(ftp_row, textvariable=self.ftp_pass, show="*", width=15).pack(side="left", padx=5)
        tk.Label(ftp_row, text="Remote Dir:", bg="#f8f9fa").pack(side="left", padx=2)
        tk.Entry(ftp_row, textvariable=self.ftp_dir, width=20).pack(side="left", padx=5)

        tool_row = tk.Frame(top_frame, bg="#f8f9fa")
        tool_row.pack(fill="x", pady=5)
        tk.Label(tool_row, text="Run Mode:", bg="#f8f9fa", font=("Arial", 9, "bold"), width=12, anchor="w").pack(side="left")
        self.mode_combo = ttk.Combobox(tool_row, textvariable=self.mode_var, width=15, state="readonly")
        self.mode_combo['values'] = ("DEBUG", "AUDIT", "GRR","CALIBRATION","PRODUCTION") 
        self.mode_combo.pack(side="left", padx=5)
        tk.Button(tool_row, text="LOAD DATA", command=self._load_data_logic, bg="#0078d7", fg="white", font=("Arial", 9, "bold"), width=15).pack(side="left", padx=20)
        
        # Nút Upload FTP cũ (Dựa trên Filter)
        tk.Button(tool_row, text="FTP upload sorted", command=self._upload_to_ftp, bg="#17a2b8", fg="white", font=("Arial", 8, "bold"), width=15).pack(side="right", padx=5)
        
        # NÚT MỚI: UPLOAD TOÀN BỘ DỮ LIỆU ĐÃ NẠP
        tk.Button(tool_row, text="FTP upload ALL", command=self._upload_all_to_ftp, bg="#6f42c1", fg="white", font=("Arial", 8, "bold"), width=15).pack(side="right", padx=5)

        # --- 2. MAIN CONTENT ---
        paned = tk.PanedWindow(self.root, orient="horizontal", bg="#cccccc", sashwidth=4)
        paned.pack(expand=True, fill="both", padx=2, pady=2)

        left_frame = tk.Frame(paned, bg="white", padx=5, pady=5)
        paned.add(left_frame, width=220)
        self.dut_tree = ttk.Treeview(left_frame, columns=("ID", "P"), show="headings", selectmode="extended")
        self.dut_tree.heading("ID", text="DUT ID"); self.dut_tree.heading("P", text="PASS")
        self.dut_tree.column("ID", width=160); self.dut_tree.column("P", width=40, anchor="center")
        self.dut_tree.pack(expand=True, fill="both")
        self.dut_tree.bind("<<TreeviewSelect>>", self._on_dut_selection_change)

        right_frame = tk.Frame(paned, bg="white", padx=10, pady=5)
        paned.add(right_frame, width=1250)

        tk.Entry(right_frame, textvariable=self.item_search_var, bg="#e1f5fe").pack(fill="x", pady=5)
        self.item_search_var.trace_add("write", self._refresh_item_table)

        self.item_tree = ttk.Treeview(right_frame, columns=("Name", "Max", "Min", "Mean"), show="headings", selectmode="extended")
        for col in ("Name", "Max", "Min", "Mean"): self.item_tree.heading(col, text=col,anchor="center")
        self.item_tree.column("Name", width=700,anchor="w")
        self.item_tree.column("Max", width=30,anchor="center")
        self.item_tree.column("Mean", width=30,anchor="center")
        self.item_tree.column("Min", width=30,anchor="center")
        self.item_tree.pack(expand=True, fill="both")

        action_frame = tk.Frame(right_frame, bg="white", pady=10)
        action_frame.pack(fill="x")
        tk.Label(action_frame, text="Target ± Delta:").pack(side="left")
        tk.Entry(action_frame, textvariable=self.target_str, width=8).pack(side="left", padx=5)
        tk.Entry(action_frame, textvariable=self.delta_str, width=8).pack(side="left", padx=5)
        tk.Button(action_frame, text="RUN", command=self._calculate_report, bg="#28a745", fg="white", font=("Arial", 8, "bold"), width=15).pack(side="left", padx=10)
        tk.Button(action_frame, text="COPY LOGS", command=self._copy_pass_logs, bg="#ffc107", fg="black", font=("Arial", 8, "bold"), width=20).pack(side="left")

        self.result_text = tk.Text(right_frame, height=12, bg="#1a1a1a", fg="#00ff41", font=("Consolas", 10), padx=10, pady=10)
        self.result_text.pack(side="bottom", fill="x", pady=10)

    # --- HÀM UPLOAD TOÀN BỘ DỮ LIỆU ---
    def _upload_all_to_ftp(self):
        """Upload toàn bộ file .json đã nạp (không cần filter)"""
        if self.df_summary is None or self.df_summary.empty:
            messagebox.showwarning("Warning", "No data loaded. Please load data first.")
            return
        
        # Xác nhận với người dùng trước khi upload số lượng lớn
        if not messagebox.askyesno("Confirm", f"Upload ALL {len(self.df_summary)} logs to FTP?"):
            return

        self._execute_ftp_transfer(self.df_summary, "ALL DATA")

    # --- HÀM UPLOAD THEO FILTER (CŨ) ---
    def _upload_to_ftp(self):
        df = self._get_filtered()
        if df is None or df.empty:
            messagebox.showwarning("Warning", "No filtered data. Please select items and RUN first.")
            return
        self._execute_ftp_transfer(df, "FILTERED DATA")

    # --- LOGIC TRUYỀN FILE CHUNG ---
    def _execute_ftp_transfer(self, df_to_upload, label):
        host, user, pw = self.ftp_host.get(), self.ftp_user.get(), self.ftp_pass.get()
        remote_dir = self.ftp_dir.get()

        try:
            self.result_text.insert(tk.END, f"[{label}] Connecting to FTP {host}...\n")
            self.root.update_idletasks()

            with FTP(host) as ftp:
                ftp.login(user=user, passwd=pw)
                try:
                    ftp.cwd(remote_dir)
                except:
                    ftp.mkd(remote_dir)
                    ftp.cwd(remote_dir)

                count = 0
                unique_paths = df_to_upload['log_path'].dropna().unique()
                for path in unique_paths:
                    json_path = path.replace('.csv', '.json')
                    if os.path.exists(json_path):
                        jsonfile = os.path.basename(json_path)
                        csvfile = os.path.basename(path)
                        with open(json_path, 'rb') as f:
                            ftp.storbinary(f"STOR {jsonfile}", f)
                        with open(path,'rb') as ff:
                            ftp.storbinary(f"STOR {csvfile}", ff)
                        count += 1
                
                self.result_text.insert(tk.END, f"[{label}] Uploaded: {count} files to {remote_dir}\n")
                messagebox.showinfo("FTP Finish", f"Successfully uploaded {count} files.")
        except Exception as e:
            self.result_text.insert(tk.END, f"FTP Error: {str(e)}\n")
            messagebox.showerror("FTP Error", str(e))

    # --- GIỮ NGUYÊN CÁC LOGIC CÒN LẠI ---
    def _browse_dir(self, var):
        path = filedialog.askdirectory()
        if path: var.set(path)

    def _load_data_logic(self):
        path, run_mode = self.source_path.get(), self.mode_var.get()
        if not os.path.exists(path): return
        try:
            _, full_df = self.parser.summary_data(path, mode="rf") 
            if not full_df.empty:
                mode_pattern = f"_{run_mode}_"
                self.df_summary = full_df[
                    (full_df['log_path'].str.contains(mode_pattern, case=False, na=False)) & 
                    (full_df['result'].str.upper() == 'PASS')
                ].copy()
                self._refresh_dut_list(); self._refresh_item_table()
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, f"Input successfuly: {len(self.df_summary)} logs PASS on mode {run_mode}\n")
        except Exception as e: messagebox.showerror("Error", str(e))

    def _on_dut_selection_change(self, event): self._refresh_item_table()

    def _refresh_item_table(self, *args):
        if self.df_summary is None: return
        for row in self.item_tree.get_children(): self.item_tree.delete(row)
        selected_duts = [self.dut_tree.item(i)['values'][0] for i in self.dut_tree.selection()]
        df = self.df_summary if not selected_duts else self.df_summary[self.df_summary['dut_id'].isin(selected_duts)]
        kw = self.item_search_var.get().lower()
        cols = [c for c in self.df_summary.columns if kw in c.lower() and c not in ["dut_id", "log_path", "result"]]
        for col in cols:
            nums = pd.to_numeric(df[col], errors='coerce')
            self.item_tree.insert("", "end", values=(col, f"{nums.max():.2f}", f"{nums.min():.2f}", f"{nums.mean():.2f}"))

    def _refresh_dut_list(self):
        for row in self.dut_tree.get_children(): self.dut_tree.delete(row)
        summary = self.df_summary.groupby('dut_id').size().reset_index(name='c')
        for _, r in summary.iterrows(): self.dut_tree.insert("", "end", values=(r['dut_id'], r['c']))

    def _get_filtered(self):
        items = [self.item_tree.item(i)['values'][0] for i in self.item_tree.selection()]
        if not items: return None
        selected_duts = [self.dut_tree.item(i)['values'][0] for i in self.dut_tree.selection()]
        df_base = self.df_summary if not selected_duts else self.df_summary[self.df_summary['dut_id'].isin(selected_duts)]
        try:
            t = float(self.target_str.get() or 0)
            d = float(self.delta_str.get() or 0)
        except ValueError:
            messagebox.showerror("Error", "Target and Delta must be numbers")
            return None
        df_num = df_base[items].apply(pd.to_numeric, errors='coerce')
        mask = np.all((df_num >= t - d) & (df_num <= t + d), axis=1)
        return df_base[mask]

    def _calculate_report(self):
        df_filtered = self._get_filtered()
        self.result_text.delete(1.0, tk.END)
        if df_filtered is not None:
            selected_duts = [self.dut_tree.item(i)['values'][0] for i in self.dut_tree.selection()]
            dut_context = f"Selected DUT ID: {selected_duts}" if selected_duts else "ALL DUT"
            self.result_text.insert(tk.END, f"--- RUN REPORT ---\n")
            self.result_text.insert(tk.END, f"Message: {dut_context}\n")
            self.result_text.insert(tk.END, f"Target:{self.target_str.get()} ± Delta:{self.delta_str.get()}\n")
            self.result_text.insert(tk.END, f"Result Pass: {len(df_filtered)} log found\n")
            self.result_text.insert(tk.END, f"------------------\n")
            self.result_text.see(tk.END)

    def _copy_pass_logs(self):
        df = self._get_filtered()
        if df is None:
            messagebox.showwarning("Warning", "Please select items and run filter first")
            return
        target = self.output_path.get()
        if not target or not os.path.exists(target):
            target = filedialog.askdirectory(title="Choose directory output")
            if target: self.output_path.set(target)
            else: return
        count = 0
        for path in df['log_path'].dropna().unique():
            json_path = path.replace('.csv', '.json')
            if os.path.exists(json_path):
                shutil.copy(path,target)
                shutil.copy(json_path, target)
                count += 1
        self.result_text.insert(tk.END, f"Complete copy {count} file .json to: {target}\n")
        messagebox.showinfo("Finish", f"Copy successfuly {count} files.")

if __name__ == "__main__":
    root = tk.Tk(); app = RFAnalyzerGUI(root); root.mainloop()