"""
Author: Berhan Erdogan
Assignment: #2
Description: Port Scanner — A tool that scans a target machine for open network ports
"""

import socket
import threading
import sqlite3
import sys
import os
import platform
import datetime



version = sys.version
system = platform.system()
print(f"Python Version : {version}")
print(f"Operating System: {system}")

# This dictionary maps commonly used port numbers to their service names.
common_ports = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    3306: "MySQL",
    3389: "RDP",
    8080: "HTTP-Alt"
}

DB_NAME = "scan_history.db"


class NetworkTool:
    def __init__(self, target):
        self.__target = target

    # Q3: What is the benefit of using @property and @target.setter?
    # @property and @target.setter gives control over how attributes are read and written,
    # instead of allowing direct access. Bad data can be prevented with validation.
    @property
    def target(self):
        return self.__target
    
    @target.setter
    def target(self, target):
        if not target or not target.strip():
            raise ValueError("Target cannot be empty")
        self.__target = target
    
    def __del__(self):
        print("NetworkTool instance destroyed")




# Q1: How does PortScanner reuse code from NetworkTool?
# PortScanner calls super().__init__() to run NetworkTool's setup,
# and automatically inherits @property, setter, and validation 
class PortScanner(NetworkTool):

    def __init__(self, target):
        super().__init__(target)
        self.scan_results = []
        self.lock = threading.Lock()


    def __del__(self):
        super().__del__()
        print("PortScanner instance destroyed")



    def scan_port(self, port):

        # Q4: What would happen without try-except here?
        # Without try-except, if a port scan fails or the connection is refused,
        # the program would crash completely and stop scanning the remaining ports.
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((self.target, port))
            status = "Open" if result == 0 else "Closed"
            name = common_ports.get(port, "Unknown")
            with self.lock:
                self.scan_results.append((port, status, name))
            if status == "Open":
                print(f"{port} is OPEN - {name}")
        except socket.error as e:
            print(f"Error scanning port {port}: {e}")
        finally:
            sock.close()

    def get_open_ports(self):
        results = self.scan_results
        open_ports = [(port, status, name) for port, status, name in results if status == "Open"]
        return open_ports
    
    # Q2: Why do we use threading instead of scanning one port at a time?
    # Scanning ports one at a time means waiting for each connection timeout before moving to the next,
    # but With t hreading, all ports are scanned simultaneously
    def scan_range(self, start_port, end_port):
        
        threads = []
        for port in range(start_port, end_port+1):
            t = threading.Thread(target=self.scan_port, args=(port,))
            threads.append(t)
        
        for t in threads: t.start()
        for t in threads: t.join()  

    def save_results(self, target, results):
        try:
            timestamp = str(datetime.datetime.now())
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                               CREATE TABLE IF NOT EXISTS scans (
                               id INTEGER PRIMARY KEY AUTOINCREMENT,
                               target TEXT,
                               port INTEGER,
                               status TEXT,
                               service TEXT,
                               scan_date TEXT
                               )""")
                for port, status, service in results:
                    cursor.execute("""
                                    INSERT INTO scans (target, port, status, service, scan_date)
                                   VALUES (?,?,?,?,?)
                                    """, (target, port, status, service, timestamp))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Database Error: {e}")

    def load_past_scans(self):
        try:
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                result = cursor.execute("SELECT * FROM scans")
                past_scans = result.fetchall()
                for _, target, port, status, service, scan_date in past_scans:
                    print(f"[{scan_date}] {target} : Port {port} ({service}) - {status}")
        except sqlite3.Error:
            print("No past scans found.")

# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":
    try:
        target = input("Enter target IP (default 127.0.0.1): ").strip()
        if not target:
            target = "127.0.0.1"

        start = int(input("Enter start port (1-1024): "))
        end = int(input("Enter end port (1-1024): "))

        if not (1 <= start <= 1024) or not (1 <= end <= 1024):
            print("Port must be between 1 and 1024.")
        elif end < start:
            print("End port must be greater than or equal to start port.")
        else:
            scanner = PortScanner(target)
            print(f"Scanning {target} from port {start} to {end}...")
            scanner.scan_range(start, end)

            open_ports = scanner.get_open_ports()
            print(f"\n--- Scan Results for {target} ---")
            for port, status, service in open_ports:
                print(f"Port {port}: {status} ({service})")
            print("------")
            print(f"Total open ports found: {len(open_ports)}")

            scanner.save_results(target, scanner.scan_results)

            history = input("Would you like to see past scan history? (yes/no): ").strip()
            if history == "yes":
                scanner.load_past_scans()
            else:
                exit

    except ValueError:
        print("Invalid input. Please enter a valid integer.")

# Q5: New Feature Proposal
# A scan comparison feature that compares the current scan results with the previous scan
# from the database and highlights any newly opened or closed ports.
# It would use a list comprehension to find changes: new_ports = [p for p in current if p not in previous]
# Diagram: See diagram_101591316.png in the repository root
