import streamlit as st
import socket
import psycopg2
import subprocess
import datetime
import platform
import os
from helper_module import get_public_ip, test_port_connectivity

def log_message(message):
    with open("connection_diagnostics.log", "a") as log_file:
        timestamp = datetime.datetime.now().isoformat()
        log_file.write(f"[{timestamp}] {message}\n")

st.set_page_config(layout="wide")
st.title("Blackboad DDA PostgreSQL Connection Tester")
st.subheader("For use with Blackboard's DDA service.")
st.markdown("https://help.blackboard.com/Learn/Administrator/SaaS/Integrations/Direct_Data_Access.")

# Initialize session state for persistent fields
defaults = {
    "host": "",
    "port": "5432",
    "dbname": "",
    "user": "",
    "sslmode": "verify-full",
    "sslrootcert": os.environ.get("PG_SSLROOTCERT", "rds-combined-ca-bundle.pem")
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Create two columns
col1, col2 = st.columns(2)

# Input fields in the left column
with col1:
    st.header("Connection Settings")
    row1_col1, row1_col2, row1_col3 = st.columns(3)
    st.session_state.host = row1_col1.text_input("Host", value=st.session_state.host)
    st.session_state.port = row1_col2.text_input("Port", value=st.session_state.port)
    st.session_state.dbname = row1_col3.text_input("Database Name", value=st.session_state.dbname)

    row2_col1, row2_col2 = st.columns(2)
    st.session_state.user = row2_col1.text_input("Username", value=st.session_state.user)
    password = row2_col2.text_input("Password", type="password")

    st.header("SSL Settings for AWS RDS")
    st.session_state.sslmode = st.selectbox(
        "SSL Mode", ["disable", "require", "verify-ca", "verify-full"],
        index=["disable", "require", "verify-ca", "verify-full"].index(st.session_state.sslmode)
    )
    st.session_state.sslrootcert = st.text_input(
        "Path to AWS RDS Root Certificate (sslrootcert)",
        value=st.session_state.sslrootcert
    )
    st.link_button(
        "Get the latest PEM bundle from AWS", 
        "https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.SSL.html#:~:text=Certificate%20bundle%20(PEM)", 
        help=None, type="secondary", 
        width="content"
        )

    run_ping = st.checkbox("Run ping test")
    run_traceroute = st.checkbox("Run traceroute")

# Results in the right column
with col2:
    if st.button("Test Connection"):
        st.header("Results")

        # Network Diagnostics
        st.subheader("Network Diagnostics")
        try:
            remote_ip = socket.gethostbyname(st.session_state.host)
            st.write(f"Resolved IP for {st.session_state.host}: {remote_ip}")
            log_message(f"Resolved IP for {st.session_state.host}: {remote_ip}")
        except Exception as e:
            st.error(f"Failed to resolve IP: {e}")
            log_message(f"Failed to resolve IP: {e}")

        try:
            local_ip = socket.gethostbyname(socket.gethostname())
            st.write(f"Local IP: {local_ip}")
            log_message(f"Local IP: {local_ip}")
        except Exception as e:
            st.error(f"Failed to get local IP: {e}")
            log_message(f"Failed to get local IP: {e}")

        public_ip = get_public_ip()
        st.write(f"Your public IP address: {public_ip}")
        log_message(f"Public IP: {public_ip}")

        if run_ping:
            try:
                st.subheader("Ping Test")
                is_windows = platform.system() == "Windows"
                ping_cmd = ["ping", "-n", "4", st.session_state.host] if is_windows else ["ping", "-c", "4", st.session_state.host]
                result = subprocess.run(ping_cmd, capture_output=True, text=True)
                st.code(result.stdout)
                log_message("Ping output:\n" + result.stdout)
            except Exception as e:
                st.error(f"Ping failed: {e}")
                log_message(f"Ping failed: {e}")

        if run_traceroute:
            st.subheader("Traceroute Output")
            is_windows = platform.system() == "Windows"
            traceroute_cmd = ["tracert", st.session_state.host] if is_windows else ["traceroute", st.session_state.host]
            try:
                process = subprocess.Popen(traceroute_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                for line in process.stdout:
                    st.text(line.strip())
                    log_message(line.strip())
            except Exception as e:
                st.error(f"Traceroute failed: {e}")
                log_message(f"Traceroute failed: {e}")

        # SSL Certificate Validation
        st.subheader("SSL Certificate Validation")
        ssl_errors = []
        if st.session_state.sslmode in ["verify-ca", "verify-full", "require"]:
            if st.session_state.sslrootcert and not os.path.isfile(st.session_state.sslrootcert):
                ssl_errors.append(f"Root certificate path does not exist: {st.session_state.sslrootcert}")
        if ssl_errors:
            for err in ssl_errors:
                st.error(err)
                log_message(err)
        else:
            st.success("SSL certificate path is valid.")
            log_message("SSL certificate path is valid.")

        # Connectivity Test
        st.subheader("Connectivity Test to PostgreSQL Host")
        success, message = test_port_connectivity(st.session_state.host, st.session_state.port)
        if success:
            st.success(message)
        else:
            st.error(message)
        log_message(message)

        # Database Connection Test and Query Result
        st.subheader("Database Connection Test")
        try:
            conn_params = {
                "host": st.session_state.host,
                "port": st.session_state.port,
                "dbname": st.session_state.dbname,
                "user": st.session_state.user,
                "password": password,
                "sslmode": st.session_state.sslmode
            }
            if st.session_state.sslrootcert:
                conn_params["sslrootcert"] = st.session_state.sslrootcert
            conn = psycopg2.connect(**conn_params)
            st.success("Connection successful!")
            log_message("Connection successful to PostgreSQL database.")

            # Query Result Display
            st.subheader("Query Result")
            cur = conn.cursor()
            cur.execute("SELECT version();")
            version = cur.fetchone()
            st.code(version[0])
            log_message(f"Query result: {version[0]}")
            cur.close()
            conn.close()
        except Exception as e:
            st.error(f"Connection failed: {e}")
            log_message(f"Connection failed: {e}")
