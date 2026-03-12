import tkinter as tk
from tkinter import messagebox
import socket

class SocketApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TCP Socket Commander")
        self.client_socket = None

        # --- Giao diện (UI) ---
        # IP & Port
        tk.Label(root, text="IP Address:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_ip = tk.Entry(root)
        self.entry_ip.insert(0, "127.0.0.1") # Mặc định là localhost
        self.entry_ip.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(root, text="Port:").grid(row=1, column=0, padx=5, pady=5)
        self.entry_port = tk.Entry(root)
        self.entry_port.insert(0, "8080")
        self.entry_port.grid(row=1, column=1, padx=5, pady=5)

        # Nút Kết nối
        self.btn_connect = tk.Button(root, text="Connect", command=self.connect_socket)
        self.btn_connect.grid(row=0, column=2, rowspan=2, padx=5, pady=5, sticky="nsew")

        # Ô nhập lệnh (Command)
        tk.Label(root, text="Command:").grid(row=2, column=0, padx=5, pady=5)
        self.entry_cmd = tk.Entry(root, width=30)
        self.entry_cmd.grid(row=2, column=1, padx=5, pady=5)

        # Nút Gửi
        self.btn_send = tk.Button(root, text="Send", command=self.send_command, state="disabled")
        self.btn_send.grid(row=2, column=2, padx=5, pady=5)

        # Phản hồi từ Server
        self.text_log = tk.Text(root, height=8, width=45, state="disabled")
        self.text_log.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

    def log(self, msg):
        self.text_log.config(state="normal")
        self.text_log.insert(tk.END, msg + "\n")
        self.text_log.see(tk.END)
        self.text_log.config(state="disabled")

    def connect_socket(self):
        ip = self.entry_ip.get()
        port = int(self.entry_port.get())
        
        try:
            # Tạo socket TCP/IP
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Thiết lập timeout để không bị treo nếu IP không tồn tại
            self.client_socket.settimeout(5.0)
            self.client_socket.connect((ip, port))
            
            self.log(f"Connected to {ip}:{port}")
            self.btn_send.config(state="normal")
            self.btn_connect.config(text="Disconnect", command=self.disconnect_socket, fg="red")
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))

    def disconnect_socket(self):
        if self.client_socket:
            self.client_socket.close()
        self.log("Disconnected.")
        self.btn_send.config(state="disabled")
        self.btn_connect.config(text="Connect", command=self.connect_socket, fg="black")

    def send_command(self):
        cmd = self.entry_cmd.get()
        if not cmd: return

        try:
            # Gửi dữ liệu (phải chuyển sang bytes bằng encode)
            self.client_socket.sendall(cmd.encode('utf-8'))
            self.log(f"-> Sent: {cmd}")

            # Nhận phản hồi (Buffer 1024 bytes)
            response = self.client_socket.recv(1024)
            self.log(f"<- Recv: {response.decode('utf-8')}")
        except Exception as e:
            self.log(f"Error: {e}")
            self.disconnect_socket()

if __name__ == "__main__":
    root = tk.Tk()
    app = SocketApp(root)
    root.mainloop()