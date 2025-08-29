"""
Interactive Call Analysis Visualization
Analyzes overtalk and silence metrics in call logs with timeline visualization
"""

import json
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


class CallAnalyzer:
    """Analyzes call data for overtalk and silence metrics"""

    def __init__(self, conversation_data: List[Dict]):
        self.conversation_data = conversation_data
        self.timeline_data = self._create_timeline()

    def _create_timeline(self) -> pd.DataFrame:
        """Create a timeline DataFrame from conversation data"""
        timeline_rows = []

        for segment in self.conversation_data:
            timeline_rows.append(
                {
                    "speaker": segment["speaker"],
                    "text": segment["text"],
                    "start_time": segment["stime"],
                    "end_time": segment["etime"],
                    "duration": segment["etime"] - segment["stime"],
                }
            )

        return pd.DataFrame(timeline_rows)

    def detect_overlaps(self) -> List[Dict]:
        """Detect overlapping speech segments"""
        overlaps = []
        df = self.timeline_data.sort_values("start_time")

        for i in range(len(df) - 1):
            current = df.iloc[i]
            next_segment = df.iloc[i + 1]

            # Check if current segment ends after next segment starts
            if current["end_time"] > next_segment["start_time"]:
                overlap_start = max(current["start_time"], next_segment["start_time"])
                overlap_end = min(current["end_time"], next_segment["end_time"])
                overlap_duration = overlap_end - overlap_start

                if overlap_duration > 0:
                    overlaps.append(
                        {
                            "start_time": overlap_start,
                            "end_time": overlap_end,
                            "duration": overlap_duration,
                            "speakers": [current["speaker"], next_segment["speaker"]],
                        }
                    )

        return overlaps

    def detect_silences(self) -> List[Dict]:
        """Detect silence gaps - any moment when neither speaker is speaking"""
        silences = []
        df = self.timeline_data.sort_values("start_time")

        # Get total call duration (from first start to last end)
        call_start = df["start_time"].min()
        call_end = df["end_time"].max()

        # Create timeline points for all speech segments
        speech_intervals = []
        for _, segment in df.iterrows():
            speech_intervals.append((segment["start_time"], segment["end_time"]))

        # Sort intervals by start time
        speech_intervals.sort()

        # Merge overlapping intervals to get continuous speech periods
        merged_intervals = []
        for start, end in speech_intervals:
            if merged_intervals and start <= merged_intervals[-1][1]:
                # Overlapping or adjacent intervals, merge them
                merged_intervals[-1] = (
                    merged_intervals[-1][0],
                    max(merged_intervals[-1][1], end),
                )
            else:
                # Non-overlapping interval
                merged_intervals.append((start, end))

        # Find silence gaps between merged intervals
        # Check for silence before first speech
        if merged_intervals and merged_intervals[0][0] > call_start:
            silences.append(
                {
                    "start_time": call_start,
                    "end_time": merged_intervals[0][0],
                    "duration": merged_intervals[0][0] - call_start,
                }
            )

        # Check for silences between speech intervals
        for i in range(len(merged_intervals) - 1):
            current_end = merged_intervals[i][1]
            next_start = merged_intervals[i + 1][0]

            if next_start > current_end:
                silences.append(
                    {
                        "start_time": current_end,
                        "end_time": next_start,
                        "duration": next_start - current_end,
                    }
                )

        # Check for silence after last speech
        if merged_intervals and merged_intervals[-1][1] < call_end:
            silences.append(
                {
                    "start_time": merged_intervals[-1][1],
                    "end_time": call_end,
                    "duration": call_end - merged_intervals[-1][1],
                }
            )

        return silences

    def calculate_metrics(self) -> Dict[str, Any]:
        """Calculate overall call metrics"""
        overlaps = self.detect_overlaps()
        silences = self.detect_silences()

        total_call_duration = self.timeline_data["end_time"].max()
        total_overlap_time = sum([overlap["duration"] for overlap in overlaps])
        total_silence_time = sum([silence["duration"] for silence in silences])

        # Calculate speaking time for each speaker
        agent_time = self.timeline_data[self.timeline_data["speaker"] == "Agent"][
            "duration"
        ].sum()
        customer_time = self.timeline_data[self.timeline_data["speaker"] == "Customer"][
            "duration"
        ].sum()

        return {
            "total_duration": total_call_duration,
            "total_overlap_time": total_overlap_time,
            "total_silence_time": total_silence_time,
            "overlap_percentage": (total_overlap_time / total_call_duration) * 100,
            "silence_percentage": (total_silence_time / total_call_duration) * 100,
            "agent_speaking_time": agent_time,
            "customer_speaking_time": customer_time,
            "agent_talk_percentage": (agent_time / total_call_duration) * 100,
            "customer_talk_percentage": (customer_time / total_call_duration) * 100,
            "overlaps": overlaps,
            "silences": silences,
            "num_overlaps": len(overlaps),
            "num_silences": len(silences),
        }


def create_timeline_visualization(analyzer: CallAnalyzer) -> go.Figure:
    """Create 2 subplot timeline: Agent/Customer speech and Overlaps/Silences"""
    from plotly.subplots import make_subplots

    fig = make_subplots(
        rows=2,
        cols=1,
        row_heights=[0.6, 0.4],
        subplot_titles=("Agent & Customer Speech", "Overlaps & Silences"),
        vertical_spacing=0.08,
        shared_xaxes=True,
    )

    df = analyzer.timeline_data
    overlaps = analyzer.detect_overlaps()
    silences = analyzer.detect_silences()

    # Get total call duration for consistent x-axis
    call_start = df["start_time"].min()
    call_end = df["end_time"].max()

    # Subplot 1: Agent segments (red) - bottom half
    agent_segments = df[df["speaker"] == "Agent"]
    for i, segment in agent_segments.iterrows():
        fig.add_trace(
            go.Scatter(
                x=[
                    segment["start_time"],
                    segment["end_time"],
                    segment["end_time"],
                    segment["start_time"],
                    segment["start_time"],
                ],
                y=[0.1, 0.1, 0.45, 0.45, 0.1],
                fill="toself",
                fillcolor="rgba(255, 0, 0, 0.7)",
                line=dict(color="red", width=2),
                mode="lines",
                name="Agent" if i == agent_segments.index[0] else "",
                text=segment["text"][:50] + "..."
                if len(segment["text"]) > 50
                else segment["text"],
                hovertemplate="<b>Agent</b><br>From: %{x:.1f}s<br>Text: %{text}<extra></extra>",
                showlegend=True if i == agent_segments.index[0] else False,
                legendgroup="agent",
            ),
            row=1,
            col=1,
        )

    # Subplot 1: Customer segments (green) - top half
    customer_segments = df[df["speaker"] == "Customer"]
    for i, segment in customer_segments.iterrows():
        fig.add_trace(
            go.Scatter(
                x=[
                    segment["start_time"],
                    segment["end_time"],
                    segment["end_time"],
                    segment["start_time"],
                    segment["start_time"],
                ],
                y=[0.55, 0.55, 0.9, 0.9, 0.55],
                fill="toself",
                fillcolor="rgba(0, 255, 0, 0.7)",
                line=dict(color="green", width=2),
                mode="lines",
                name="Customer" if i == customer_segments.index[0] else "",
                text=segment["text"][:50] + "..."
                if len(segment["text"]) > 50
                else segment["text"],
                hovertemplate="<b>Customer</b><br>From: %{x:.1f}s<br>Text: %{text}<extra></extra>",
                showlegend=True if i == customer_segments.index[0] else False,
                legendgroup="customer",
            ),
            row=1,
            col=1,
        )

    # Subplot 2: Overlap visualization
    for i, overlap in enumerate(overlaps):
        fig.add_trace(
            go.Scatter(
                x=[
                    overlap["start_time"],
                    overlap["end_time"],
                    overlap["end_time"],
                    overlap["start_time"],
                    overlap["start_time"],
                ],
                y=[0.6, 0.6, 1, 1, 0.6],
                fill="toself",
                fillcolor="rgba(255, 165, 0, 0.8)",
                line=dict(color="orange", width=3),
                mode="lines",
                name="Overlap" if i == 0 else "",
                hovertemplate=f"From: {overlap['start_time']:.1f}s to {overlap['end_time']:.1f}s<br>Duration: {overlap['duration']:.1f}s<br>Speakers: {', '.join(overlap['speakers'])}<extra></extra>",
                showlegend=True if i == 0 else False,
                legendgroup="overlap",
            ),
            row=2,
            col=1,
        )

    # Subplot 2: Silence visualization
    for i, silence in enumerate(silences):
        fig.add_trace(
            go.Scatter(
                x=[
                    silence["start_time"],
                    silence["end_time"],
                    silence["end_time"],
                    silence["start_time"],
                    silence["start_time"],
                ],
                y=[0, 0, 0.4, 0.4, 0],
                fill="toself",
                fillcolor="rgba(128, 128, 128, 0.6)",
                line=dict(color="gray", width=1),
                mode="lines",
                name="Silence" if i == 0 else "",
                hovertemplate=f"From: {silence['start_time']:.1f}s to {silence['end_time']:.1f}s<br>Duration: {silence['duration']:.1f}s<extra></extra>",
                showlegend=True if i == 0 else False,
                legendgroup="silence",
            ),
            row=2,
            col=1,
        )

    # Update layout
    fig.update_layout(
        title="Interactive Call Analysis Timeline - 2 Track View",
        height=700,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    # Update x-axes - same scale for both subplots
    for row in [1, 2]:
        fig.update_xaxes(range=[call_start, call_end], row=row, col=1)

    # Only show x-axis title on bottom subplot
    fig.update_xaxes(title_text="Time (seconds)", row=2, col=1)

    # Update y-axes
    fig.update_yaxes(
        title_text="Speakers",
        row=1,
        col=1,
        range=[0, 1],
        tickvals=[0.275, 0.725],
        ticktext=["Agent", "Customer"],
    )
    fig.update_yaxes(
        title_text="Events",
        row=2,
        col=1,
        range=[0, 1],
        tickvals=[0.2, 0.8],
        ticktext=["Silence", "Overlap"],
    )

    return fig


def load_conversation_files(directory: str) -> Dict[str, List[Dict]]:
    """Load all conversation JSON files from directory"""
    conversations = {}
    conversation_dir = Path(directory)

    if not conversation_dir.exists():
        return conversations

    for json_file in conversation_dir.glob("*.json"):
        try:
            with open(json_file, "r") as f:
                data = json.load(f)
                conversations[json_file.stem] = data
        except Exception as e:
            st.error(f"Error loading {json_file}: {e}")

    return conversations


# Streamlit App
def main():
    st.set_page_config(
        page_title="Call Analysis Dashboard", page_icon="📞", layout="wide"
    )

    st.title("📞 Interactive Call Analysis Dashboard")
    st.markdown("Analyze overtalk and silence metrics in call logs")

    # Sidebar for file selection
    st.sidebar.header("Call Selection")

    # Load conversations
    conversations_dir = "/workspace/prodigal/Q3/allConversations"
    conversations = load_conversation_files(conversations_dir)

    if not conversations:
        st.error("No conversation files found in the allConversations directory")
        return

    # Select conversation
    selected_conversation = st.sidebar.selectbox(
        "Choose a conversation:",
        options=list(conversations.keys()),
        format_func=lambda x: f"Call {x[:8]}...",
    )

    if selected_conversation:
        # Analyze selected conversation
        conversation_data = conversations[selected_conversation]
        analyzer = CallAnalyzer(conversation_data)

        # Calculate metrics
        metrics = analyzer.calculate_metrics()

        # Display key metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Duration", f"{metrics['total_duration']:.1f}s")

        with col2:
            st.metric(
                "Overlap %",
                f"{metrics['overlap_percentage']:.1f}%",
                delta=f"{metrics['num_overlaps']} occurrences",
            )

        with col3:
            st.metric(
                "Silence %",
                f"{metrics['silence_percentage']:.1f}%",
                delta=f"{metrics['num_silences']} gaps",
            )

        with col4:
            st.metric(
                "Agent/Customer Ratio",
                f"{metrics['agent_talk_percentage']:.0f}/{metrics['customer_talk_percentage']:.0f}%",
            )

        # Timeline visualization
        st.header("📊 Interactive Timeline")
        timeline_fig = create_timeline_visualization(analyzer)
        st.plotly_chart(timeline_fig, width="stretch")


if __name__ == "__main__":
    main()
