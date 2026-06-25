import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages

# மொபைலுக்கு ஏற்றவாறு பக்கத்தை அமைத்தல்
st.set_page_config(page_title="Multi-Pivot Matrix Tool", layout="centered")

st.title("📊 Multi-Pivot Matrix Engine")
st.write("Compare Present vs Previous Frameworks")

# --- 1. லெவல்களை மாற்றும் பகுதி (Sidebar input panel) ---
st.sidebar.header("📝 Edit Matrix Data")

# புதுப்பிக்கப்பட்ட எண்கள் அடங்கிய ஆரம்பகால தரவுகள்
default_data = {
    "Level": ["Yearly", "Present Monthly", "Previous Weekly", "Present Weekly", "Previous Daily", "Present Daily"],
    "H4": [28649.78, 24218.50, 24217.40, 24318.16, 24187.09, 24178.43],
    "H3": [27389.69, 23883.13, 24115.25, 24187.08, 24104.37, 24117.22],
    "L3": [24869.51, 23212.37, 23910.95, 23924.92, 23938.93, 23994.79],
    "L4": [23609.42, 22877.00, 23808.80, 23793.84, 23856.21, 23933.57],
    "TC": [25431.31, 23872.32, 24009.91, 24045.09, 23994.32, 24150.30],
    "CP": [24733.02, 23764.13, 24006.72, 24034.18, 23966.98, 24118.87],
    "BC": [24034.73, 23655.94, 24003.53, 24023.28, 23939.65, 24087.43]
}

# புதிய எண்களைச் சேமிப்பதற்கான டிக்ஸ்னரி
updated_data = {"Level": ["Yearly", "Present Monthly", "Previous Weekly", "Present Weekly", "Previous Daily", "Present Daily"]}
for col in ["H4", "H3", "L3", "L4", "TC", "CP", "BC"]:
    updated_data[col] = []

# ஒவ்வொரு பிரிவிற்கும் இன்புட் பாக்ஸ்கள் ( text_input மொபைலில் எளிதாக டைப் செய்ய)
for tf in updated_data["Level"]:
    with st.sidebar.expander(f"Modify {tf} Levels", expanded=(tf in ["Present Daily", "Previous Daily"])):
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

# --- 2. 7 Types of Pivot Relationship இன்ஜின் ---
def detect_pivot_relationship(prev_tc, prev_bc, curr_tc, curr_bc):
    prev_high, prev_low = max(prev_tc, prev_bc), min(prev_tc, prev_bc)
    curr_high, curr_low = max(curr_tc, curr_bc), min(curr_bc, curr_tc)
    
    if curr_low > prev_high:
        return "🟢 Higher Value (Strongly Bullish)", "மார்க்கெட் நல்ல அப்-டிரெண்டில் மேலே செல்ல வாய்ப்பு அதிகம்."
    elif curr_high < prev_low:
        return "🔴 Lower Value (Strongly Bearish)", "மார்க்கெட் நல்ல டவுன்-டிரெண்டில் கீழே விழ வாய்ப்பு அதிகம்."
    elif curr_high < prev_high and curr_low > prev_low:
        return "🟣 Inside Value (Breakout Imminent)", "கடுமையான சுருக்கம்! பெரிய பிரேக்அவுட் மூவ்மெண்ட் இன்று நிகழும்."
    elif curr_high > prev_high and curr_low < prev_low:
        return "🔵 Outside Value (Sideways / Rangebound)", "சந்தை பெரிய டிரெண்ட் எடுக்காமல் இரண்டு பக்கமும் அலைபாயும்."
    elif curr_high > prev_high and curr_low >= prev_low:
        return "🟡 Overlapping Higher (Moderately Bullish)", "சந்தை லேசான பாசிட்டிவ் போக்கில் நகரக்கூடும்."
    elif curr_low < prev_low and curr_high <= prev_high:
        return "🟠 Overlapping Lower (Moderately Bearish)", "சந்தை லேசான நெகட்டிவ் போக்கில் நகரக்கூடும்."
    else:
        return "⚪ Unchanged Congestion", "மாற்றங்கள் இல்லை, முந்தைய ரேஞ்சிலேயே நீடிக்கிறது."

row_map = df.set_index("Level")
d_rel_title, d_rel_desc = detect_pivot_relationship(
    row_map.loc["Previous Daily", "TC"], row_map.loc["Previous Daily", "BC"],
    row_map.loc["Present Daily", "TC"], row_map.loc["Present Daily", "BC"]
)
w_rel_title, w_rel_desc = detect_pivot_relationship(
    row_map.loc["Previous Weekly", "TC"], row_map.loc["Previous Weekly", "BC"],
    row_map.loc["Present Weekly", "TC"], row_map.loc["Present Weekly", "BC"]
)

st.info(f"**📅 Intraday View (Prev Daily ➔ Pres Daily):** {d_rel_title}\n\n💡 *{d_rel_desc}*")
st.success(f"**⏳ Swing View (Prev Weekly ➔ Pres Weekly):** {w_rel_title}\n\n💡 *{w_rel_desc}*")

# --- 3. நீங்கள் கேட்ட புதிய வியூ பட்டன்கள் ---
st.subheader("🎯 View Perspective")
selected_tab = st.radio("Select View Range:", ["Full Structure View", "Tactical Focus View (W & D)"], horizontal=True)

if selected_tab == "Full Structure View":
    sub_df = df.copy()
else:
    # நீங்கள் கேட்டபடி முந்தைய/இப்போதைய வாரம் மற்றும் முந்தைய/இப்போதைய நாள் மட்டும் காட்டும் ফিল্টার
    sub_df = df[df["Level"].isin(["Previous Weekly", "Present Weekly", "Previous Daily", "Present Daily"])].reset_index(drop=True)

# --- 4. நிலையான Matplotlib சார்ட் என்ஜின் ---
def plot_mobile_engine(plot_df, ltp):
    fig, ax = plt.subplots(figsize=(10, 6.5))
    x_positions = range(len(plot_df))
    bar_width = 0.4
    all_prices = [ltp]

    for idx, row in plot_df.iterrows():
        x = x_positions[idx]
        all_prices.extend([row["H4"], row["H3"], row["L3"], row["L4"], row["TC"], row["CP"], row["BC"]])

        # Camarilla Highs & Lows
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

        # LTP Line
        ax.hlines(y=ltp, xmin=x - bar_width, xmax=x + bar_width, colors="crimson", linestyles="-", linewidth=1.2, alpha=0.7)
        ax.plot(x, ltp, marker="o", color="crimson", markersize=5)
        if idx == len(plot_df) - 1:
            ax.text(x + bar_width + 0.02, ltp, f'LTP:{ltp}', va="center", ha="left", color="crimson", weight="bold", fontsize=8.5)

    # Confluence Shading (Pink Bands)
    if "Present Weekly" in plot_df["Level"].values and "Present Daily" in plot_df["Level"].values:
        w_row = plot_df[plot_df["Level"] == "Present Weekly"].iloc[0]
        d_row = plot_df[plot_df["Level"] == "Present Daily"].iloc[0]
        all_keys = ["H4", "H3", "L3", "L4", "TC", "CP", "BC"]
        for wk in all_keys:
            for dk in all_keys:
                if abs(w_row[wk] - d_row[dk]) / w_row[wk] <= 0.0015:
                    y_min, y_max = min(w_row[wk], d_row[dk]), max(w_row[wk], d_row[dk])
                    ax.axhspan(y_min - 6, y_max + 6, xmin=0.2, xmax=0.9, color="#ff00ff", alpha=0.1)

    ax.set_xticks(x_positions)
    ax.set_xticklabels(plot_df["Level"], fontsize=9.5, weight="bold")
    ax.grid(True, linestyle=":", alpha=0.4)
    ax.set_xlim(-0.5, len(plot_df) - 0.5)
    
    # Auto-Zoom
    min_p, max_p = min(all_prices), max(all_prices)
    padding = (max_p - min_p) * 0.08
    ax.set_ylim(min_p - padding, max_p + padding)
    plt.tight_layout()
    return fig

st.pyplot(plot_mobile_engine(sub_df, market_close_price))

# --- 5. டேபிள் காட்டுகின்ற பகுதி ---
st.subheader("📋 Active Data Table")
st.dataframe(df.set_index("Level"), use_container_width=True)

# --- 6. PDF டவுன்லோடு செய்யும் வசதி (பட்டன் சேர்க்கப்பட்டுள்ளது) ---
st.subheader("📥 Download Analysis Report")

pdf_path = "Multi_Pivot_Analysis_Report.pdf"
with PdfPages(pdf_path) as pdf:
    # PDF-ல் இரண்டு வியூ சார்ட்டுகளும் தனித்தனி பக்கங்களாகச் சேமிக்கப்படும்
    for view_name, plot_data in [("Full View Structure", df), 
                                 ("Tactical Focus (W and D)", df[df["Level"].isin(["Previous Weekly", "Present Weekly", "Previous Daily", "Present Daily"])])]:
        fig_pdf = plot_mobile_engine(plot_data.reset_index(drop=True), market_close_price)
        plt.title(f"Market Analysis - {view_name}", fontsize=11, weight="bold", pad=12)
        pdf.savefig(fig_pdf)
        plt.close()

# பிடிஎஃப் டவுன்லோடு பட்டன்
with open(pdf_path, "rb") as pdf_file:
    st.download_button(label="Download PDF Matrix Report", data=pdf_file, file_name="Multi_Pivot_Matrix_Report.pdf", mime="application/pdf")
