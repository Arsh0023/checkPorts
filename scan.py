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
        user="",
        password="",
        database="ports"
    )
    cursor = conn.cursor()

    # Create hosts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hosts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ip_address VARCHAR(16) NOT NULL,
            hostname VARCHAR(255),
            state_reason VARCHAR(50),
            state_ttl INT,
            state VARCHAR(10)
        )
    ''')

    # Create ports table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ports (
            id INT AUTO_INCREMENT PRIMARY KEY,
            host_id INT,
            port_id INT,
            protocol VARCHAR(10),
            reason VARCHAR(50),
            reason_ttl INT,
            state VARCHAR(10),
            service_name VARCHAR(50),
            FOREIGN KEY (host_id) REFERENCES hosts(id)
        )
    ''')

    
    for ip in publicIps:
        try:
            print(f"Performing check for - {ip}")
            data = nmap.scan_top_ports(target=ip)

            details = data[ip]
            cursor.execute('''
                INSERT INTO hosts (ip_address, hostname, state_reason, state_ttl, state)
                VALUES (%s, %s, %s, %s, %s)
            ''', (
                ip,
                details['hostname'][0]['name'],
                details['state']['reason'],
                int(details['state']['reason_ttl']),
                details['state']['state']
            ))
            host_id = cursor.lastrowid

            # Insert data into ports table
            for port in details['ports']:
                cursor.execute('''
                    INSERT INTO ports (host_id, port_id, protocol, reason, reason_ttl, state, service_name)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                ''', (
                    host_id,
                    int(port['portid']),
                    port['protocol'],
                    port['reason'],
                    int(port['reason_ttl']),
                    port['state'],
                    port['service']['name']
                ))
        except Exception as e:
            print(f'Error!!! {e} for {ip}')
        finally:
            conn.commit()
            conn.close()