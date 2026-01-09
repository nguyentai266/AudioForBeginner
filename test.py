import tkinter as tk

import customtkinter as ctk
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

ctk.set_appearance_mode("dark")


class MultiPlotVerticalScroll(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.geometry("900x700")
        self.title("Vertical Scroll - Multiple Plots")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ===== container =====
        container = ctk.CTkFrame(self)
        container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # ===== canvas =====
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
        frame.pack(fill="x", padx=20, pady=15)
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


if __name__ == "__main__":
    app = MultiPlotVerticalScroll()
    app.mainloop()
