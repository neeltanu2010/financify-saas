import streamlit as st
from protect_tool import require_tool_access, record_tool_use

TOOL_NAME = "bubble-sniffer"
user = require_tool_access(TOOL_NAME)

st.title("Bubble Sniffer")

if st.button("Run Tool"):
    # Record usage only when the user actually runs the paid action.
    record_tool_use(TOOL_NAME)
    st.success("Now run your existing tool logic here.")
