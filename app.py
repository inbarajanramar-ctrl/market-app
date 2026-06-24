import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages

# மொபைலுக்கு ஏற்றவாறு பக்கத்தை அமைத்தல்
st.set_page_config(page_title="Market Levels Matrix", layout="centered")

st.title("📊 Market Structure Matrix")
st.write("Camarilla + CPR Multi-Timeframe Tool")

# --- 1. லெவல்களை மாற்றும் பகுதி (Sidebar input panel) ---
st.sidebar.header("📝 Edit Level Data")

# ஆரம்பகால தரவுகள் (Handwritten Table Data)
default_data = {
    "Level": ["Daily", "Weekly", "Monthly", "Yearly"],
    "H4": [24187.09, 24217.40, 24218.50, 28649.78],
    "H3": [24104.37, 24115.25, 23883.13, 27389.69],
    "L3": [23938.93, 23910.95, 23212.37, 24869.51],
    "L4": [23856.21, 23808.80, 22877.00, 23609.42],
    "TC": [23994.32, 24009.91, 23872.32, 25431.31],
    "CP": [23966.98, 24006.72, 23764.13, 24733.02],
    "BC": [23939.65, 24003.53, 23655.94, 24034.73]
}

# புதிய எண்களைச் சேமிப்பதற்கான டிக்ஸ்னரி
updated_data = {"Level": ["Yearly", "Monthly", "Weekly", "Daily"]}
for col in ["H4", "H3", "L3", "L4", "TC", "CP", "BC"]:
    updated_data[col] = []

# ஒவ்வொரு டைம்ஃபிரேமிற்கும் தனித்தனி இன்புட் பாக்ஸ்கள் (மொபைலில் டைப் செய்ய வசதியாக text_input)
for tf in ["Yearly", "Monthly", "Weekly", "Daily"]:
    with st.sidebar.expander(f"Modify {tf} Levels", expanded=(tf == "Daily")):
        d_idx = default_data["Level"].index(tf)
        for col in ["H4", "H3", "L3", "L4", "TC", "CP", "BC"]:
            val_str = st.text_input(f"{tf} {col}", value=str(default_data[col][d_idx]), key=f"{tf}_{col}")
            try:
                updated_data[col].append(float(val_str))
            except ValueError:
                updated_data[col].append(0.0)

# மார்க்கெட் க்ளோஸ் பிரைஸ் இன்புட் (LTP)
market_close_str = st.text_input("🔴 Today's Market Close Price (LTP)", value="24021.65")
try:
    market_close_price = float(market_close_str)
except ValueError:
    market_close_price = 23824.10

# டேட்டாபிரேம் உருவாக்குதல்
df = pd.DataFrame(updated_data)

# --- 2. டைம்ஃபிரேம் மாற்றிப் பார்க்கும் பட்டன்கள் ---
st.subheader("🎯 View Perspective")
selected_tab = st.st_radio = st.radio("Select View Range:", ["Full View (Y to D)", "Trading View (M to D)", "Tactical View (W & D)"], horizontal=True)

if selected_tab == "Full View (Y to D)":
    sub_df = df.copy()
elif selected_tab == "Trading View (M to D)":
    sub_df = df[df["Level"].isin(["Monthly", "Weekly", "Daily"])].reset_index(drop=True)
else:
    sub_df = df[df["Level"].isin(["Weekly", "Daily"])].reset_index(drop=True)

# --- 3. சார்ட் வரைவதற்க்கான என்ஜின் ---
def plot_mobile_engine(plot_df, ltp):
    fig, ax = plt.subplots(figsize=(10, 6.5))
    x_positions = range(len(plot_df))
    bar_width = 0.4

    for idx, row in plot_df.iterrows():
        x = x_positions[idx]

        # Camarilla கோடுகள்
        ax.hlines(y=row["H4"], xmin=x - bar_width, xmax=x + bar_width, colors="blue", linewidth=2.5)
        ax.text(x, row["H4"] + 12, f'{row["H4"]:.1f}', ha="center", va="bottom", fontsize=8, color="blue", weight="bold")

        ax.hlines(y=row["H3"], xmin=x - bar_width, xmax=x + bar_width, colors="orange", linewidth=2.5)
        ax.text(x, row["H3"] + 12, f'{row["H3"]:.1f}', ha="center", va="bottom", fontsize=8, color="red", weight="bold")

        ax.hlines(y=row["L3"], xmin=x - bar_width, xmax=x + bar_width, colors="orange", linestyles="--", linewidth=2)
        ax.text(x, row["L3"] - 12, f'{row["L3"]:.1f}', ha="center", va="top", fontsize=8, color="red", weight="bold")

        ax.hlines(y=row["L4"], xmin=x - bar_width, xmax=x + bar_width, colors="blue", linestyles="--", linewidth=2)
        ax.text(x, row["L4"] - 12, f'{row["L4"]:.1f}', ha="center", va="top", fontsize=8, color="blue", weight="bold")

        # CPR கோடுகள்
        ax.hlines(y=row["TC"], xmin=x - bar_width, xmax=x + bar_width, colors="purple", linestyles=":", linewidth=1.5)
        ax.hlines(y=row["CP"], xmin=x - bar_width, xmax=x + bar_width, colors="purple", linestyles="-.", linewidth=2)
        ax.hlines(y=row["BC"], xmin=x - bar_width, xmax=x + bar_width, colors="purple", linestyles=":", linewidth=1.5)
        ax.text(x - bar_width, row["CP"], f' CP:{row["CP"]:.1f}', ha="left", va="center", fontsize=7.5, color="purple")

        # LTP க்ளோஸ் புள்ளி
        ax.hlines(y=ltp, xmin=x - bar_width, xmax=x + bar_width, colors="crimson", linestyles="-", linewidth=1.2, alpha=0.7)
        ax.plot(x, ltp, marker="o", color="crimson", markersize=5)
        
        if idx == len(plot_df) - 1:
            ax.text(x + bar_width + 0.02, ltp, f'LTP:{ltp}', va="center", ha="left", color="crimson", weight="bold", fontsize=8.5)

    ax.set_xticks(x_positions)
    ax.set_xticklabels(plot_df["Level"], fontsize=9.5, weight="bold")
    ax.grid(True, linestyle=":", alpha=0.4)
    ax.set_xlim(-0.5, len(plot_df) - 0.5)
    plt.tight_layout()
    return fig

# திரையில் சார்ட்டைக் காட்டுதல்
chart_figure = plot_mobile_engine(sub_df, market_close_price)
st.pyplot(chart_figure)

# --- 4. டேபிளைக் காட்டுதல் ---
st.subheader("📋 Active Data Table")
st.dataframe(df.set_index("Level"), use_container_width=True)

# --- 5. PDF டவுன்லோடு செய்யும் வசதி (தானாக PDF ஜெனரேட் ஆகும்) ---
st.subheader("📥 Download Analysis Report")

pdf_path = "Market_Levels_Analysis.pdf"
with PdfPages(pdf_path) as pdf:
    # 3 பக்கங்கள் கொண்ட PDF உருவாக்கப்படும்
    for view_name, plot_data in [("Full View", df), 
                                 ("Trading View", df[df["Level"].isin(["Monthly", "Weekly", "Daily"])]), 
                                 ("Tactical View", df[df["Level"].isin(["Weekly", "Daily"])])]:
        fig_pdf = plot_mobile_engine(plot_data.reset_index(drop=True), market_close_price)
        plt.title(f"Market Levels - {view_name}")
        pdf.savefig(fig_pdf)
        plt.close()

# பிடிஎஃப் டவுன்லோடு பட்டன்
with open(pdf_path, "rb") as pdf_file:
    st.download_button(label="Download PDF Report", data=pdf_file, file_name="Market_Levels_Analysis.pdf", mime="application/pdf")
