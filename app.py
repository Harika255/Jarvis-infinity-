import streamlit as st

st.set_page_config(
    page_title="JARVIS Infinity",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 JARVIS INFINITY")
st.subheader("Safety-Aware Multimodal AI Agent")

st.markdown(
    """
    ### Context-Aware Decision Making • Task Planning • Computer Interaction

    Welcome to the web interface of **JARVIS Infinity**.
    """
)

st.divider()

user_input = st.text_area(
    "💬 Give JARVIS a task",
    placeholder="Example: I have a project review tomorrow. What should I do next?"
)

if st.button("🚀 Ask JARVIS"):
    if user_input.strip():
        st.success("JARVIS received your request!")
        st.write("**Your request:**", user_input)
    else:
        st.warning("Please enter a request first.")

st.divider()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("🧠 AI Brain", "READY")

with col2:
    st.metric("📋 Planner", "READY")

with col3:
    st.metric("🛡️ Safety", "ACTIVE")

with col4:
    st.metric("🔍 Verification", "READY")

st.divider()

st.caption(
    "JARVIS Infinity — Academic AI Agent Project"
)