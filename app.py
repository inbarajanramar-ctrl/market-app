import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

# Set mobile-friendly page config
st.set_page_config(page_title="Market Levels Matrix", layout="centered")

st.title("📊 Market Structure Matrix")
st.write("Camarilla + CPR Multi-Timeframe Tool")

# --- 1. Sidebar / Input Panel for Data Editing ---
st.sidebar.header("📝 Edit Level Data")

# Default Data
default_data = {
    "Level": ["Daily", "Weekly", "Monthly", "Yearly"],
    "H4": [24016.90, 24217.40, 24218.50, 28649.78],
    "H3": [23920.50, 24115.25, 23883.13, 27389.69],
    "L3": [23727.70, 23910.95, 23212.37, 24869.51],
    "L4": [23631.30, 23808.80, 22877.00, 23609.42],
    "TC": [23960.23, 24009.91, 23872.32, 25431.31],
    "CP": [23914.85, 24006.72, 23764.13, 24733.02],
    "BC": [23869.47, 24003.53, 23655.94, 24034.73]
}

# Mobile input form to dynamically change values
updated_data = {"Level": ["Yearly", "Monthly", "Weekly", "Daily"]}
for col in ["H4", "H3", "L3", "L4", "TC", "CP", "BC"]:
    updated_data[col] = []

# Dynamic input fields per timeframe
for tf in ["Yearly", "Monthly", "Weekly", "Daily"]:
    with st.sidebar.expander(f"Modify {tf} Levels", expanded=(tf == "Daily")):
        d_idx = default_data["Level"].index(tf)
        for col in ["H4", "H3", "L3", "L4", "TC", "CP", "BC"]:
            val = st.number_input(f"{tf} {col}", value=default_data[col][d_idx], format="%.2f", key=f"{tf}_{col}")
            updated_data[col].append(val)

# Dynamic LTP Close price input
market_close_price = st.number_input("🔴 Today's Market Close Price (LTP)", value=23824.10, format="%.2f")

# Build DataFrame
df = pd.DataFrame(updated_data)

# --- 2. Mobile View Timeframe Filter Tabs ---
st.subheader("🎯 View Perspective")
selected_tab = st.radio("Select View Range:", ["Full View (Y to D)", "Trading View (M to D)", "Tactical View (W & D)"], horizontal=True)

if selected_tab == "Full View (Y to D)":
    sub_df = df.copy()
elif selected_tab == "Trading View (M to D)":
    sub_df = df[df["Level"].isin(["Monthly", "Weekly", "Daily"])].reset_index(drop=True)
else:
    sub_df = df[df["Level"].isin(["Weekly", "Daily"])].reset_index(drop=True)

# --- 3. Plotting Engine Optimized for Mobile Screen Resolution ---
def plot_mobile_engine(plot_df, ltp):
    # Dynamic aspect ratio for clean mobile viewing
    fig, ax = plt.subplots(figsize=(10, 6.5))
    x_positions = range(len(plot_df))
    bar_width = 0.4

    for idx, row in plot_df.iterrows():
        x = x_positions[idx]

        # Camarilla Framework
        ax.hlines(y=row["H4"], xmin=x - bar_width, xmax=x + bar_width, colors="blue", linewidth=2.5)
        ax.text(x, row["H4"] + 12, f'{row["H4"]:.1f}', ha="center", va="bottom", fontsize=8, color="blue", weight="bold")

        ax.hlines(y=row["H3"], xmin=x - bar_width, xmax=x + bar_width, colors="orange", linewidth=2.5)
        ax.text(x, row["H3"] + 12, f'{row["H3"]:.1f}', ha="center", va="bottom", fontsize=8, color="red", weight="bold")

        ax.hlines(y=row["L3"], xmin=x - bar_width, xmax=x + bar_width, colors="orange", linestyles="--", linewidth=2)
        ax.text(x, row["L3"] - 12, f'{row["L3"]:.1f}', ha="center", va="top", fontsize=8, color="red", weight="bold")

        ax.hlines(y=row["L4"], xmin=x - bar_width, xmax=x + bar_width, colors="blue", linestyles="--", linewidth=2)
        ax.text(x, row["L4"] - 12, f'{row["L4"]:.1f}', ha="center", va="top", fontsize=8, color="blue", weight="bold")

        # CPR Channels
        ax.hlines(y=row["TC"], xmin=x - bar_width, xmax=x + bar_width, colors="purple", linestyles=":", linewidth=1.5)
        ax.hlines(y=row["CP"], xmin=x - bar_width, xmax=x + bar_width, colors="purple", linestyles="-.", linewidth=2)
        ax.hlines(y=row["BC"], xmin=x - bar_width, xmax=x + bar_width, colors="purple", linestyles=":", linewidth=1.5)
        ax.text(x - bar_width, row["CP"], f' CP:{row["CP"]:.1f}', ha="left", va="center", fontsize=7.5, color="purple")

        # LTP Close Markers across all segments
        ax.hlines(y=ltp, xmin=x - bar_width, xmax=x + bar_width, colors="crimson", linestyles="-", linewidth=1.2, alpha=0.7)
        ax.plot(x, ltp, marker="o", color="crimson", markersize=5)
        
        if idx == len(plot_df) - 1:
            ax.text(x + bar_width + 0.02, ltp, f'LTP:{ltp}', va="center", ha="left", color="crimson", weight="bold", fontsize=8.5)

    # Clean mobile visual constraints
    ax.set_xticks(x_positions)
    ax.set_xticklabels(plot_df["Level"], fontsize=9.5, weight="bold")
    ax.grid(True, linestyle=":", alpha=0.4)
    ax.set_xlim(-0.5, len(plot_df) - 0.5)
    plt.tight_layout()
    return fig

# Display Chart on Mobile App Window Screen
chart_figure = plot_mobile_engine(sub_df, market_close_price)
st.pyplot(chart_figure)

# --- 4. Interactive Data Table Output View ---
st.subheader("📋 Active Data Table")
st.dataframe(df.set_index("Level"), use_container_width=True)
