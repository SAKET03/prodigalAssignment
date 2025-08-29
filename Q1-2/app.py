import streamlit as st

import main

st.set_page_config(
    page_title="Debt Collection Conversation Analyzer",
    page_icon="📞",
    layout="wide",
)

st.title("📞 Debt Collection Conversation Analyzer")
st.markdown(
    "Analyze debt collection conversations for compliance and professionalism using **Pattern Matching** or **LLM** approaches."
)

# Sidebar
st.sidebar.header("Configuration")
groq_api_key = st.sidebar.text_input(
    "Groq API Key (required for LLM)",
    type="password",
)

# Layout
col1, col2 = st.columns([1, 2])

with col1:
    st.header("Source")
    uploaded_file = st.file_uploader(
        "Upload ZIP of JSON conversations",
        type="zip",
    )

    st.header("Method")
    approach = st.selectbox("Select Approach", ["Pattern Matching", "LLM"])

    st.header("Task")
    task = st.selectbox(
        "Select Task",
        ["Profanity Detection", "Privacy and Compliance Violation"],
    )

    run_analysis = st.button("Run Analysis", type="primary")

with col2:
    st.header("Results")

    if run_analysis:
        if uploaded_file is None:
            st.warning("Please upload a ZIP file first.")
        else:
            total_calls = None
            # -----------------------------
            # PROFANITY DETECTION
            # -----------------------------
            if task == "Profanity Detection":
                if approach == "LLM":
                    agent_df, customer_df = main.profanity_detection_llm(uploaded_file)
                else:  # Pattern Matching
                    agent_df, customer_df = main.profanity_detection_pattern(
                        uploaded_file
                    )

                conversations = main.load_conversations_from_zip(uploaded_file)
                total_calls = len(conversations)

                # -----------------------------
                # Summary Stats
                # -----------------------------
                st.subheader("Summary Stats")

                # Create metrics grid
                metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

                with metric_col1:
                    st.metric(
                        "Agent Profanity",
                        len(agent_df),
                    )

                with metric_col2:
                    st.metric(
                        "Customer Profanity",
                        len(customer_df),
                    )

                with metric_col3:
                    violation_rate = (
                        round((len(agent_df) / total_calls * 100), 1)
                        if total_calls > 0
                        else 0
                    )
                    st.metric("Agent Violation Rate", f"{violation_rate}%")

                with metric_col4:
                    st.metric("Total Calls", total_calls)

                # -----------------------------
                # Detailed DataFrames
                # -----------------------------
                st.subheader("Agent Profanity Details")
                if len(agent_df) > 0:
                    st.dataframe(agent_df, width="stretch")
                else:
                    st.info("No agent profanity detected")

                st.subheader("Customer Profanity Details")
                if len(customer_df) > 0:
                    st.dataframe(customer_df, width="stretch")
                else:
                    st.info("No customer profanity detected")

            # -----------------------------
            # PRIVACY DETECTION
            # -----------------------------
            elif task == "Privacy and Compliance Violation":
                if approach == "LLM":
                    violated_df = main.privacy_detection_llm(uploaded_file)
                else:  # Pattern Matching
                    violated_df = main.privacy_detection_pattern(uploaded_file)

                # Get total calls processed (this might need adjustment based on your main)
                conversations = main.load_conversations_from_zip(uploaded_file)
                total_calls_processed = len(conversations)
                violations_detected = len(violated_df)

                # -----------------------------
                # Summary Stats
                # -----------------------------
                st.subheader("Summary Stats")

                # Create metrics grid
                metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

                with metric_col1:
                    st.metric(
                        "Total Violations",
                        violations_detected,
                    )

                with metric_col2:
                    violation_rate = (
                        round((violations_detected / total_calls_processed * 100), 1)
                        if total_calls_processed > 0
                        else 0
                    )
                    st.metric("Violation Rate", f"{violation_rate}%")

                with metric_col3:
                    compliance_rate = round(100 - violation_rate, 1)
                    st.metric("Compliance Rate", f"{compliance_rate}%")

                with metric_col4:
                    st.metric("Total Processed", total_calls_processed)

                # -----------------------------
                # Detailed DataFrame
                # -----------------------------
                st.subheader("Violation Details")
                if len(violated_df) > 0:
                    st.dataframe(violated_df, width="stretch")
                else:
                    st.success("No privacy violations detected")
