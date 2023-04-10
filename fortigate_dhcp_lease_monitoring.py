import appdaemon.plugins.hass.hassapi as hass
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import mysql.connector
from mysql.connector import Error
import time

# Define a class for monitoring Fortigate DHCP leases
class FortigateDHCPLeaseMonitoring(hass.Hass):
    def initialize(self):
        # Parameters
        self.fortigate_base_url = self.args["fortigate_base_url"]
        self.api_key = self.args["api_key"]

        # MySQL database credentials
        self.mysql_host = self.args["mysql_host"]
        self.mysql_user = self.args["mysql_user"]
        self.mysql_password = self.args["mysql_password"]
        self.mysql_database = self.args["mysql_database"]

        # Ignore SSL errors
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        # Schedule the update to run every 10 minutes
        self.run_every(self.update_dhcp_leases, "now", 10 * 60)

    # Update DHCP leases every 10 minutes
    def update_dhcp_leases(self, kwargs):
        dhcp_leases = self.get_dhcp_leases(self.fortigate_base_url, self.api_key)
        recent_dhcp_leases = []

        connection = None
        try:
            connection = mysql.connector.connect(
                host=self.mysql_host,
                user=self.mysql_user,
                password=self.mysql_password,
                database=self.mysql_database
            )

            if connection.is_connected():
                self.create_table_if_not_exists(connection)

                if dhcp_leases:
                    for lease in dhcp_leases:
                        hostname = lease['hostname'] if 'hostname' in lease else 'N/A'
                        mac_address = lease['mac'] if 'mac' in lease else 'N/A'
                        interface = lease['interface'] if 'interface' in lease else 'N/A'
                        first_seen = time.strftime('%Y-%m-%d %H:%M:%S')
                        self.insert_dhcp_lease(connection, hostname, mac_address, interface)

                recent_dhcp_leases = self.get_recent_dhcp_leases(connection)

        except Error as e:
            self.log(f"Error: {e}")

        finally:
            if connection and connection.is_connected():
                connection.close()

        # Update the sensor in Home Assistant
        state_str = "\n".join([f"{lease[0]}, {lease[1]}" for lease in recent_dhcp_leases])
        self.set_state("sensor.new_dhcp_leases_last_7_days", state=state_str)

    # Get DHCP leases from Fortigate API
    def get_dhcp_leases(self, base_url, api_key):
        url = f'{base_url}/api/v2/monitor/system/dhcp?access_token={api_key}'
        response = requests.get(url, verify=False)

        if response.status_code == 200:
            leases = response.json()
            return leases['results']
        else:
            self.log(f"Error: {response.status_code}")
            return None

    # Create a table to store DHCP lease data if it doesn't exist
    def create_table_if_not_exists(self, connection):
        cursor = connection.cursor()
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS dhcp_leases (
            id INT AUTO_INCREMENT PRIMARY KEY,
            hostname VARCHAR(255) NOT NULL,
            mac_address VARCHAR(17) NOT NULL,
            interface VARCHAR(255) NOT NULL,
            first_seen TIMESTAMP NOT NULL,
            last_seen TIMESTAMP NOT NULL,
            UNIQUE (mac_address, interface)
        );
        '''
        cursor.execute(create_table_query)
        connection.commit()

    # Insert a DHCP lease into the database
    def insert_dhcp_lease(self, connection, hostname, mac_address, interface):
        cursor = connection.cursor()
        insert_query = '''
        INSERT INTO dhcp_leases (hostname, mac_address, interface, first_seen, last_seen)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            hostname = VALUES(hostname),
            last_seen = VALUES(last_seen),
            first_seen = IF(first_seen IS NULL, VALUES(first_seen), first_seen);
        '''
        current_time = time.strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(insert_query, (hostname, mac_address, interface, current_time, current_time))
        connection.commit()



    # Get recent DHCP leases from the last 7 days
    def get_recent_dhcp_leases(self, connection):
        cursor = connection.cursor()
        select_query = '''
        SELECT hostname, mac_address
        FROM dhcp_leases
        WHERE first_seen >= NOW() - INTERVAL 7 DAY;
        '''
        cursor.execute(select_query)
        return cursor.fetchall()

