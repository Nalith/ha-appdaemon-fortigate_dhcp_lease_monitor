# Fortigate DHCP Lease Monitoring

## Introduction

This script, `FortigateDHCPLeaseMonitoring`, is designed to monitor DHCP leases from a Fortigate device, store the lease information in a MySQL database, and update a sensor in Home Assistant with recent DHCP lease information. The script is written in Python and is intended to be used with AppDaemon in the Home Assistant ecosystem. This script was created using ChatGPT-4, a powerful AI language model developed by OpenAI.

## Detailed Overview

The `FortigateDHCPLeaseMonitoring` class extends `hass.Hass` from the AppDaemon library, allowing it to be seamlessly integrated into the Home Assistant environment. The main components of the script include:

1. **Initialization**: The `initialize()` method sets up the required parameters, such as the Fortigate API URL, API key, and MySQL database credentials. It also disables SSL warnings and schedules the `update_dhcp_leases()` method to run every 10 minutes.

2. **Updating DHCP Leases**: The `update_dhcp_leases()` method retrieves the current DHCP leases from the Fortigate API, establishes a connection to the MySQL database, and ensures that the required table exists in the database. It then iterates through the retrieved DHCP leases and inserts them into the database. Finally, it updates the Home Assistant sensor with the recent DHCP leases from the past 7 days.

3. **Fortigate API Interaction**: The `get_dhcp_leases()` method makes a request to the Fortigate API to fetch the current DHCP lease information. It returns the lease data as a list of dictionaries or `None` if an error occurs.

4. **MySQL Database Interaction**: The script includes several methods to interact with the MySQL database, such as `create_table_if_not_exists()`, `insert_dhcp_lease()`, and `get_recent_dhcp_leases()`. These methods are responsible for creating the table to store DHCP lease data, inserting a new lease into the table, and retrieving recent leases, respectively.

By using this script, you can effectively monitor your Fortigate DHCP leases, store the lease information in a MySQL database, and keep track of recent leases in your Home Assistant environment. The script can be easily customized to suit your specific requirements, such as adjusting the update interval or modifying the database structure.
