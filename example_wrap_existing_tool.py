import streamlit as st
from auth_client import require_tool_access, record_tool_use

TOOL_NAME = "bubble-sniffer"  # change this for each tool

email, status = require_tool_access(TOOL_NAME)

st.title("Your Existing Tool")
st.write("Keep your existing tool code below this line.")

# Example: only record usage when user actually runs/analyzes/scans.
if st.button("Run Tool"):
    # 1. Put your existing tool function here.
    st.success("Tool output goes here.")

    # 2. Record one usage after successful run.
    record_tool_use(email, TOOL_NAME)
