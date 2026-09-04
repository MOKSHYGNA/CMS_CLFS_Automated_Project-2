import streamlit as st
import subprocess
import sys

st.set_page_config(
    page_title="CMS DMEPOS Automation",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 CMS DMEPOS Automation System")
st.write("Automate DMEPOS data processing from one place.")

st.divider()

st.subheader("DMEPOS Automation")

if st.button("▶ Run DMEPOS Automation", type="primary"):

    st.warning(
        "DMEPOS automation is starting. This may take some time."
    )

    with st.spinner("Running DMEPOS automation..."):

        result = subprocess.run(
            [sys.executable, "run_pipeline.py"],
            capture_output=True,
            text=True
        )

    if result.returncode == 0:
        st.success(
            "✅ DMEPOS automation finished successfully!"
        )
    else:
        st.error(
            f"❌ DMEPOS automation failed. "
            f"Exit code: {result.returncode}"
        )

    with st.expander("View Pipeline Output"):
        st.text(result.stdout)

        if result.stderr:
            st.text("ERROR OUTPUT:")
            st.text(result.stderr)

st.divider()

st.subheader("Status")

st.info("Ready to run DMEPOS automation.")