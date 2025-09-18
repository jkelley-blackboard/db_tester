# PostgreSQL Connection & Network Diagnostic Tool

This Streamlit-based application helps users diagnose connectivity issues with PostgreSQL databases, especially AWS RDS instances. It provides network diagnostics, SSL certificate validation, and database connection testing in a user-friendly interface.

## Features

🔌 Connection Settings: Input host, port, database name, username, and password.
🔐 SSL Configuration: Select SSL mode and provide the path to the AWS RDS root certificate.
🌐 Network Diagnostics:

- Resolve host IP
- Display local and public IP
- Optional ping and traceroute tests


🔒 SSL Certificate Validation: Verifies the existence of the specified root certificate.
🧪 Connectivity Test: Checks TCP connectivity to the PostgreSQL host and port.
🗄️ Database Connection Test: Attempts to connect and run a simple query (SELECT version();) to verify access.
📝 Logging: All diagnostic messages are logged to connection_diagnostics.log.

## File Structure

pg_connection_tool.py: Main Streamlit app with UI and diagnostic logic.
helper_module.py: Contains utility functions for public IP retrieval and port connectivity testing.

## Requirements

Python 3.8+
Streamlit
psycopg2
Access to the AWS RDS root certificate (PEM bundle)

## Installation
Shellpip install streamlit psycopg2Show more lines
Running the App
Shellstreamlit run pg_connection_tool.pyShow more lines
Environment Variables (Optional)
You can set the default path to the AWS RDS root certificate using:
Shellexport PG_SSLROOTCERT=/path/to/rds-combined-ca-bundle.pemShow more lines

## Notes

Passwords are not persisted between sessions for security.
The tool supports both Windows and Unix-based systems for ping and traceroute.
SSL modes supported: disable, require, verify-ca, verify-full.

##License
tbd