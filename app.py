import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages

# மொபைலுக்கு ஏற்றவாறு பக்கத்தை அமைத்தல்
st.set_page_config(page_title="Advanced Market Levels Matrix", layout="centered")

st.title("📊 Market Structure Matrix")
st.write("Camarilla + CPR Multi-Timeframe Analytical Engine")

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

# ஒவ்வொரு டைம்ஃபிரேமிற்கும் தனித்தனி இன்புட் பாக்ஸ்கள்
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
    market_close_price = 24021.65

# டேட்டாபிரேம் உருவாக்குதல்
df = pd.DataFrame(updated_data)

# --- 2. டைம்ஃபிரேம் மாற்றிப் பார்க்கும் பட்டன்கள் ---
st.subheader("🎯 View Perspective")
selected_tab = st.radio("Select View Range:", ["Full View (Y to D)", "Trading View (M to D)", "Tactical View (W & D)"], horizontal=True)

if selected_tab == "Full View (Y to D)":
    sub_df = df.copy()
elif selected_tab == "Trading View (M to D)":
    sub_df = df[df["Level"].isin(["Monthly", "Weekly", "Daily"])].reset_index(drop=True)
else:
    sub_df = df[df["Level"].isin(["Weekly", "Daily"])].reset_index(drop=True)

# --- 3. மேம்படுத்தப்பட்ட ஜூம் & கான்ஃப்ளூயன்ஸ் கொண்ட புதிய என்ஜின் ---
def plot_mobile_engine(plot_df, ltp):
    fig, ax = plt.subplots(figsize=(11, 7.5))
    x_positions = range(len(plot_df))
    bar_width = 0.42

    # ஒய்-அச்சை ஜூம் (Zoom Y-Axis) செய்வதற்காக விலைகளைச் சேமிக்கும் லிஸ்ட்
    all_prices_in_view = [ltp]

    for idx, row in plot_df.iterrows():
        x = x_positions[idx]
        
        # தற்போதைய பார்வையில் இருக்கும் அனைத்து விலைகளையும் சேர்த்தல்
        all_prices_in_view.extend([row["H4"], row["H3"], row["L3"], row["L4"], row["TC"], row["CP"], row["BC"]])

        # 1. Camarilla Highs (H4 / H3)
        ax.hlines(y=row["H4"], xmin=x - bar_width, xmax=x + bar_width, colors="#0044ff", linewidth=2.5)
        ax.text(x, row["H4"] + 8, f'{row["H4"]:.1f}', ha="center", va="bottom", fontsize=8, color="#0044ff", weight="bold")

        ax.hlines(y=row["H3"], xmin=x - bar_width, xmax=x + bar_width, colors="#ff8800", linewidth=2.5)
        ax.text(x, row["H3"] + 8, f'{row["H3"]:.1f}', ha="center", va="bottom", fontsize=8, color="#cc0000", weight="bold")

        # 2. Camarilla Lows (L3 / L4)
        ax.hlines(y=row["L3"], xmin=x - bar_width, xmax=x + bar_width, colors="#ff8800", linestyles="--", linewidth=2)
        ax.text(x, row["L3"] - 8, f'{row["L3"]:.1f}', ha="center", va="top", fontsize=8, color="#cc0000", weight="bold")

        ax.hlines(y=row["L4"], xmin=x - bar_width, xmax=x + bar_width, colors="#0044ff", linestyles="--", linewidth=2)
        ax.text(x, row["L4"] - 8, f'{row["L4"]:.1f}', ha="center", va="top", fontsize=8, color="#0044ff", weight="bold")

        # 3. CPR கோடுகள் (TC, CP, BC)
        ax.hlines(y=row["TC"], xmin=x - bar_width, xmax=x + bar_width, colors="#8800cc", linestyles=":", linewidth=1.5)
        ax.hlines(y=row["CP"], xmin=x - bar_width, xmax=x + bar_width, colors="#8800cc", linestyles="-.", linewidth=2)
        ax.hlines(y=row["BC"], xmin=x - bar_width, xmax=x + bar_width, colors="#8800cc", linestyles=":", linewidth=1.5)
        ax.text(x - bar_width, row["CP"], f' CP:{row["CP"]:.1f}', ha="left", va="center", fontsize=7.5, color="#8800cc", weight="semibold")

        # 4. லைவ் மார்க்கெட் Close (LTP) கிடைமட்டக் கோடு
        ax.hlines(y=ltp, xmin=x - bar_width, xmax=x + bar_width, colors="#dc143c", linestyles="-", linewidth=1.5, alpha=0.8)
        ax.plot(x, ltp, marker="o", color="#dc143c", markersize=6)
        
        if idx == len(plot_df) - 1:
            ax.text(x + bar_width + 0.02, ltp, f'LTP: {ltp:.2f}', va="center", ha="left", color="#dc143c", weight="bold", fontsize=9)

    # --- 5. ஆட்டோமேட்டிக் Confluence Zone கண்டறிதல் (Weekly & Daily இருந்தால் மட்டும்) ---
    if "Weekly" in plot_df["Level"].values and "Daily" in plot_df["Level"].values:
        w_row = plot_df[plot_df["Level"] == "Weekly"].iloc[0]
        d_row = plot_df[plot_df["Level"] == "Daily"].iloc[0]
        w_idx = plot_df[plot_df["Level"] == "Weekly"].index[0]
        d_idx = plot_df[plot_df["Level"] == "Daily"].index[0]

        all_keys = ["H4", "H3", "L3", "L4", "TC", "CP", "BC"]
        has_shading = False

        for wk in all_keys:
            for dk in all_keys:
                # 0.15% நெருக்கம் இருக்கிறதா என்று கணக்கிடுதல்
                if abs(w_row[wk] - d_row[dk]) / w_row[wk] <= 0.0015:
                    y_min, y_max = min(w_row[wk], d_row[dk]), max(w_row[wk], d_row[dk])
                    
                    # ஓவர்லேப் பகுதியை ஹைலைட் செய்தல்
                    ax.axhspan(y_min - 6, y_max + 6, xmin=0.42, xmax=0.96, color="#ff00ff", alpha=0.12)
                    if not has_shading:
                        ax.text((w_idx + d_idx)/2, y_max + 18, "⚠️ STRUCTURAL CLUSTER", ha="center", color="#8800cc", fontsize=9, weight="black")
                        has_shading = True

    # --- 6. முக்கிய காட்சி மேம்பாடுகள் மற்றும் ஆட்டோ-ஜூம் தர்க்கம் ---
    ax.set_xticks(x_positions)
    ax.set_xticklabels(plot_df["Level"], fontsize=10, weight="bold")
    ax.grid(True, linestyle=":", alpha=0.5, color="#cccccc")
    ax.set_xlim(-0.5, len(plot_df) - 0.5)
    
    # தற்போதைய வியூவிற்கு தகுந்தவாறு ஒய்-அச்சை ஜூம் செய்தல் (Dynamic Zooming)
    min_price = min(all_prices_in_view)
    max_price = max(all_prices_in_view)
    padding = (max_price - min_price) * 0.08  # விளிம்புகளில் 8% இடைவெளி தருதல்
    ax.set_ylim(min_price - padding, max_price + padding)
    
    plt.tight_layout()
    return fig

# திரையில் புதிய ஜூம் செய்யப்பட்ட சார்ட்டைக் காட்டுதல்
chart_figure = plot_mobile_engine(sub_df, market_close_price)
st.pyplot(chart_figure)

# --- 4. டேபிளைக் காட்டுதல் ---
st.subheader("📋 Active Data Table")
st.dataframe(df.set_index("Level"), use_container_width=True)

# --- 5. PDF டவுன்லோடு செய்யும் வசதி ---
st.subheader("📥 Download Analysis Report")

pdf_path = "Market_Levels_Analysis.pdf"
with PdfPages(pdf_path) as pdf:
    for view_name, plot_data in [("Full View", df), 
                                 ("Trading View", df[df["Level"].isin(["Monthly", "Weekly", "Daily"])]), 
                                 ("Tactical View", df[df["Level"].isin(["Weekly", "Daily"])])]:
        fig_pdf = plot_mobile_engine(plot_data.reset_index(drop=True), market_close_price)
        plt.title(f"Market Levels - {view_name}", fontsize=12, weight="bold", pad=15)
        pdf.savefig(fig_pdf)
        plt.close()

# பிடிஎஃப் டவுன்லோடு பட்டன்
with open(pdf_path, "rb") as pdf_file:
    st.download_button(label="Download PDF Report", data=pdf_file, file_name="Market_Levels_Analysis.pdf", mime="application/pdf")
