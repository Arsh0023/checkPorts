import os
import nmap3
import config
import sqlite3
import mysql.connector
from pprint import pprint
from get_ips import get_public_ips

publicIps = get_public_ips(config.REGION)

if __name__ == '__main__':

    nmap = nmap3.Nmap()

    conn = mysql.connector.connect(
    host="127.0.0.1",
    user="your_username",
    password="your_password"
    )

    cursor = conn.cursor()

    #create hosts table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS hosts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip_address VARCHAR(16) NOT NULL,
        hostname VARCHAR(255),
        state_reason VARCHAR(50),
        state_ttl INTEGER,
        state VARCHAR(10)
    )''')
    # Create ports table

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        host_id INTEGER,
        port_id INTEGER,
        protocol VARCHAR(10),
        reason VARCHAR(50),
        reason_ttl INTEGER,
        state VARCHAR(10),
        service_name VARCHAR(50),
        FOREIGN KEY (host_id) REFERENCES hosts(id)
    )''')

    for ip in publicIps:
        print(f"Performing check for - {ip}")
        #nmap.scan_command(target=ip, arg='-p-')
        data = nmap.scan_top_ports(target=ip)
        
        details = data[ip]
        cursor.execute('''
        INSERT INTO hosts (ip_address, hostname, state_reason, state_ttl, state)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        ip,
        details['hostname'][0]['name'] ,
        details['state']['reason'],
        int(details['state']['reason_ttl']),
        details['state']['state']
    ))
        host_id = cursor.lastrowid

    # Insert data into ports table
        for port in details['ports']:
            cursor.execute('''
            INSERT INTO ports (host_id, port_id, protocol, reason, reason_ttl, state, service_name)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            host_id,
            int(port['portid']),
            port['protocol'],
            port['reason'],
            int(port['reason_ttl']),
            port['state'],
            port['service']['name']
        ))
        
        break
    
    conn.commit()
    conn.close()