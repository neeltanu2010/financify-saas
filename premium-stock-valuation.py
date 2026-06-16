from streamlit_integration.auth_client import require_tool_access, record_tool_use

TOOL_NAME = "premium-honey-finder"
email, status = require_tool_access(TOOL_NAME)

# Put this line ONLY after the user successfully runs the tool:
# record_tool_use(email, TOOL_NAME)
