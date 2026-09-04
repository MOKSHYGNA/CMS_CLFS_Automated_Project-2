import streamlit as st
import subprocess
import sys
from pathlib import Path


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="CMS Automation System",
    page_icon="🏥",
    layout="wide"
)


# ============================================================
# PROJECT PATHS
# ============================================================

# Project 2 = folder where this app.py is located
PROJECT_2 = Path(__file__).resolve().parent

# DMEPOS Project 3 is inside Project 2
DMEPOS_PROJECT = PROJECT_2 / "CMS_DMEPOS_Automated_Project 3"
DMEPOS_PIPELINE = DMEPOS_PROJECT / "run_pipeline.py"


# ============================================================
# HEADER
# ============================================================

st.title("🏥 CMS Automation System")

st.markdown(
    """
    **Centralized CMS data automation dashboard**

    Run individual CMS automation processes or execute the
    complete automation pipeline from one place.
    """
)

st.divider()


# ============================================================
# PROCESS SELECTION
# ============================================================

st.subheader("📋 Select CMS Process")

process = st.selectbox(
    "Choose the process you want to run:",
    [
        "CLFS",
        "DMEPOS",
        "Physician",
        "Anesthesia",
        "Run Complete Automation"
    ]
)

st.write(f"**Selected Process:** `{process}`")

st.divider()


# ============================================================
# RUN AUTOMATION BUTTON
# ============================================================

if st.button(
    "▶ Run Automation",
    type="primary",
    use_container_width=True
):

    # ========================================================
    # CLFS AUTOMATION
    # ========================================================

    if process == "CLFS":

        st.info("🔄 CLFS automation is starting...")

        scripts = [
            "download_files.py",
            "etl_pipeline.py"
        ]

        success = True
        output = ""

        with st.spinner("Running CLFS automation..."):

            for script in scripts:

                result = subprocess.run(
                    [sys.executable, script],
                    capture_output=True,
                    text=True,
                    cwd=PROJECT_2
                )

                output += (
                    f"\n\n{'=' * 70}\n"
                    f"{script}\n"
                    f"{'=' * 70}\n"
                )

                output += result.stdout

                if result.stderr:
                    output += (
                        "\nERROR OUTPUT:\n"
                        + result.stderr
                    )

                if result.returncode != 0:
                    success = False
                    break

        if success:
            st.success(
                "✅ CLFS automation finished successfully!"
            )
        else:
            st.error(
                "❌ CLFS automation failed."
            )

        with st.expander("📄 View CLFS Output"):
            st.text(output)


    # ========================================================
    # PHYSICIAN AUTOMATION
    # ========================================================

    elif process == "Physician":

        st.info("🔄 Physician automation is starting...")

        with st.spinner("Running Physician automation..."):

            result = subprocess.run(
                [sys.executable, "physician_parser.py"],
                capture_output=True,
                text=True,
                cwd=PROJECT_2
            )

        if result.returncode == 0:

            st.success(
                "✅ Physician automation finished successfully!"
            )

        else:

            st.error(
                "❌ Physician automation failed."
            )

        with st.expander("📄 View Physician Output"):

            st.text(result.stdout)

            if result.stderr:

                st.text("ERROR OUTPUT:")

                st.text(result.stderr)


    # ========================================================
    # ANESTHESIA AUTOMATION
    # ========================================================

    elif process == "Anesthesia":

        st.info("🔄 Anesthesia automation is starting...")

        scripts = [
            "anesthesia_downloader.py",
            "anesthesia_parser.py",
            "anesthesia_database.py"
        ]

        success = True
        output = ""

        with st.spinner("Running Anesthesia automation..."):

            for script in scripts:

                result = subprocess.run(
                    [sys.executable, script],
                    capture_output=True,
                    text=True,
                    cwd=PROJECT_2
                )

                output += (
                    f"\n\n{'=' * 70}\n"
                    f"{script}\n"
                    f"{'=' * 70}\n"
                )

                output += result.stdout

                if result.stderr:

                    output += (
                        "\nERROR OUTPUT:\n"
                        + result.stderr
                    )

                if result.returncode != 0:

                    success = False

                    break

        if success:

            st.success(
                "✅ Anesthesia automation finished successfully!"
            )

        else:

            st.error(
                "❌ Anesthesia automation failed."
            )

        with st.expander("📄 View Anesthesia Output"):

            st.text(output)


    # ========================================================
    # DMEPOS AUTOMATION
    # ========================================================

    elif process == "DMEPOS":

        st.info("🔄 DMEPOS automation is starting...")

        # Check whether the DMEPOS pipeline exists
        if not DMEPOS_PIPELINE.exists():

            st.error(
                "❌ DMEPOS pipeline was not found."
            )

            st.code(str(DMEPOS_PIPELINE))

        else:

            with st.spinner("Running DMEPOS automation..."):

                result = subprocess.run(
                    [
                        sys.executable,
                        str(DMEPOS_PIPELINE)
                    ],
                    capture_output=True,
                    text=True,
                    cwd=DMEPOS_PROJECT
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

            with st.expander("📄 View DMEPOS Output"):

                st.text(result.stdout)

                if result.stderr:

                    st.text("ERROR OUTPUT:")

                    st.text(result.stderr)


    # ========================================================
    # COMPLETE CMS AUTOMATION
    # ========================================================

    elif process == "Run Complete Automation":

        st.warning(
            """
            ⚠️ Complete Automation will run the CMS automation
            pipeline. This may take some time.
            """
        )

        complete_output = ""

        complete_success = True


        # ----------------------------------------------------
        # STEP 1 — PROJECT 2
        # ----------------------------------------------------

        st.info(
            "🔵 Step 1 of 2 — Running Project 2 CMS automation..."
        )

        with st.spinner(
            "Running Project 2 automation..."
        ):

            result_project2 = subprocess.run(
                [
                    sys.executable,
                    "run_pipeline.py"
                ],
                capture_output=True,
                text=True,
                cwd=PROJECT_2
            )

        complete_output += (
            f"\n\n{'=' * 70}\n"
            "PROJECT 2 AUTOMATION OUTPUT\n"
            f"{'=' * 70}\n"
        )

        complete_output += result_project2.stdout

        if result_project2.stderr:

            complete_output += (
                "\n\nERROR OUTPUT:\n"
                + result_project2.stderr
            )

        if result_project2.returncode != 0:

            complete_success = False

            st.error(
                "❌ Project 2 automation failed."
            )

        else:

            st.success(
                "✅ Project 2 automation completed successfully!"
            )


        # ----------------------------------------------------
        # STEP 2 — DMEPOS
        # ----------------------------------------------------

        if complete_success:

            st.info(
                "🟢 Step 2 of 2 — Running DMEPOS automation..."
            )

            if not DMEPOS_PIPELINE.exists():

                complete_success = False

                st.error(
                    "❌ DMEPOS pipeline was not found."
                )

                complete_output += (
                    "\n\nDMEPOS PIPELINE NOT FOUND:\n"
                    + str(DMEPOS_PIPELINE)
                )

            else:

                with st.spinner(
                    "Running DMEPOS automation..."
                ):

                    result_dmepos = subprocess.run(
                        [
                            sys.executable,
                            str(DMEPOS_PIPELINE)
                        ],
                        capture_output=True,
                        text=True,
                        cwd=DMEPOS_PROJECT
                    )

                complete_output += (
                    f"\n\n{'=' * 70}\n"
                    "DMEPOS PROJECT 3 OUTPUT\n"
                    f"{'=' * 70}\n"
                )

                complete_output += result_dmepos.stdout

                if result_dmepos.stderr:

                    complete_output += (
                        "\n\nERROR OUTPUT:\n"
                        + result_dmepos.stderr
                    )

                if result_dmepos.returncode != 0:

                    complete_success = False

                    st.error(
                        f"❌ DMEPOS automation failed. "
                        f"Exit code: {result_dmepos.returncode}"
                    )

                else:

                    st.success(
                        "✅ DMEPOS automation completed successfully!"
                    )


        # ----------------------------------------------------
        # FINAL RESULT
        # ----------------------------------------------------

        st.divider()

        if complete_success:

            st.success(
                "🎉 COMPLETE CMS AUTOMATION FINISHED SUCCESSFULLY!"
            )

        else:

            st.error(
                "❌ Complete CMS automation failed."
            )


        # ----------------------------------------------------
        # COMPLETE OUTPUT
        # ----------------------------------------------------

        with st.expander(
            "📄 View Complete Pipeline Output"
        ):

            st.text(complete_output)


# ============================================================
# SYSTEM STATUS
# ============================================================

st.divider()

st.subheader("📊 System Status")

col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "CMS Processes",
        "4"
    )


with col2:

    st.metric(
        "Automation Mode",
        "ETL"
    )


with col3:

    if DMEPOS_PIPELINE.exists():

        st.metric(
            "DMEPOS Pipeline",
            "Ready"
        )

    else:

        st.metric(
            "DMEPOS Pipeline",
            "Not Found"
        )


# ============================================================
# FOOTER
# ============================================================

st.caption(
    "CMS Automation System • Centralized ETL and data processing dashboard"
)