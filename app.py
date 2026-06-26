import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf
from matplotlib.backends.backend_pdf import PdfPages

# மொபைலுக்கு ஏற்றவாறு பக்கத்தை அமைத்தல்
st.set_page_config(page_title="Advanced Multi-Pivot Matrix", layout="centered")

st.title("📊 Advanced Multi-Pivot Structure Matrix")
st.write("Calculates Accurate Completed Frames from Daily Market History")

# --- 1. சிம்பல் செலக்டர் இன்புட் ---
ticker_options = {
    "Nifty 50": "^NSEI",
    "Bank Nifty": "^NSEBANK",
    "Sensex": "^BSESN",
    "Reliance": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "HDFC Bank": "HDFCBANK.NS"
}

selected_symbol_label = st.selectbox("🎯 Select Instrument / Stock:", list(ticker_options.keys()))
custom_ticker = st.text_input("✍️ Or Type Custom Yahoo Ticker:", value=ticker_options[selected_symbol_label])

# --- 2. தினசரி டேட்டாவை எடுத்து துல்லியமாக பிரிக்கும் புதிய இன்ஜின் ---
@st.cache_data(ttl=60)  # 1 நிமிடத்திற்கு ஒருமுறை டேட்டாவை புதுப்பிக்கும்
def fetch_perfect_ohlc_matrix(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    
    # 2 வருட தினசரி டேட்டாவை எடுக்கிறோம் (இதிலிருந்து வார/மாத லெவல்களை நாமே துல்லியமாகப் பிரிப்போம்)
    df = ticker.history(period="2y", interval="1d")
    
    if df.empty or len(df) < 60:
        st.error("No sufficient data found.")
        st.stop()
        
    # தற்போதைய லைவ் விலை (LTP)
    try:
        ltp = ticker.basic_info['lastPrice']
    except:
        ltp = df['Close'].iloc[-1]

    matrix_data = {}
    
    # A. DAILY FRAMES (நேற்றைய நாள் vs இன்றைய நாள்)
    matrix_data["Present Daily"] = {"H": df['High'].iloc[-1], "L": df['Low'].iloc[-1], "C": df['Close'].iloc[-1]}
    matrix_data["Previous Daily"] = {"H": df['High'].iloc[-2], "L": df['Low'].iloc[-2], "C": df['Close'].iloc[-2]}
    
    # B. WEEKLY FRAMES (Resampling Daily Data to Weekly Columns)
    # 'W-SUN' கொடுத்து வாராந்திர இறுதி விலைகளைப் பிரிக்கிறோம்
    df_weekly = df.resample('W-SUN').agg({'High': 'max', 'Low': 'min', 'Close': 'last'})
    df_weekly = df_weekly.dropna()
    
    # கடைசி வாரம் தற்போதைய ரன்னிங் வாரம் என்பதால், அதற்கு முந்தைய 2 முழுமையான வாரங்களை எடுக்கிறோம்
    matrix_data["Previous Week"] = {"H": df_weekly['High'].iloc[-2], "L": df_weekly['Low'].iloc[-2], "C": df_weekly['Close'].iloc[-2]}
    matrix_data["2 Weeks Ago"] = {"H": df_weekly['High'].iloc[-3], "L": df_weekly['Low'].iloc[-3], "C": df_weekly['Close'].iloc[-3]}
    
    # C. MONTHLY FRAMES (Resampling Daily Data to Monthly Columns)
    df_monthly = df.resample('ME').agg({'High': 'max', 'Low': 'min', 'Close': 'last'})
    df_monthly = df_monthly.dropna()
    
    # கடைசி மாதம் ரன்னிங் மாதம் என்பதால், அதற்கு முந்தைய 2 முழுமையான மாதங்களை எடுக்கிறோம்
    matrix_data["Previous Month"] = {"H": df_monthly['High'].iloc[-2], "L": df_monthly['Low'].iloc[-2], "C": df_monthly['Close'].iloc[-2]}
    matrix_data["2 Months Ago"] = {"H": df_monthly['High'].iloc[-3], "L": df_monthly['Low'].iloc[-3], "C": df_monthly['Close'].iloc[-3]}
    
    return matrix_data, round(ltp, 2)

# --- 3. ஆட்டோமேட்டிக் லெவல் கால்குலேட்டர் ஃபங்ஷன் ---
def calculate_pivot_levels(high, low, close):
    cp = (high + low + close) / 3.0
    bc = (high + low) / 2.0
    tc = (cp - bc) + cp
    range_val = high - low
    h4 = close + (range_val * 1.1 / 2.0)
    h3 = close + (range_val * 1.1 / 4.0)
    l3 = close - (range_val * 1.1 / 4.0)
    l4 = close - (range_val * 1.1 / 2.0)
    return {"H4": round(h4,2), "H3": round(h3,2), "L3": round(l3,2), "L4": round(l4,2), "TC": round(tc,2), "CP": round(cp,2), "BC": round(bc,2)}

with st.spinner("Fetching data from website..."):
    try:
        web_data, market_close_price = fetch_perfect_ohlc_matrix(custom_ticker)
        st.success(f"Loaded Data for {custom_ticker}! LTP: {market_close_price}")
    except Exception as e:
        st.error("Connection error. Please verify the Ticker name.")
        st.stop()

# லெவல்களை கணக்கிட்டு வரிசைப்படுத்துதல்
view_order = ["2 Months Ago", "Previous Month", "2 Weeks Ago", "Previous Week", "Previous Daily", "Present Daily"]
calculated_rows = []
for tf in view_order:
    vals = web_data.get(tf, {"H": 0, "L": 0, "C": 0})
    pivots = calculate_pivot_levels(vals["H"], vals["L"], vals["C"])
    pivots["Level"] = tf
    calculated_rows.append(pivots)

df = pd.DataFrame(calculated_rows)[["Level", "H4", "H3", "L3", "L4", "TC", "CP", "BC"]]

# --- 4. 7 Types of Pivot Relationship இன்ஜின் ---
def detect_pivot_relationship(prev_tc, prev_bc, curr_tc, curr_bc):
    prev_high, prev_low = max(prev_tc, prev_bc), min(prev_tc, prev_bc)
    curr_high, curr_low = max(curr_tc, curr_bc), min(curr_bc, curr_tc)
    if curr_low > prev_high: return "🟢 Higher Value (Strongly Bullish)", "மார்க்கெட் நல்ல அப்-டிரெண்டில் மேலே செல்ல வாய்ப்பு அதிகம்."
    elif curr_high < prev_low: return "🔴 Lower Value (Strongly Bearish)", "மார்க்கெட் நல்ல டவுன்-டிரெண்டில் கீழே விழ வாய்ப்பு அதிகம்."
    elif curr_high < prev_high and curr_low > prev_low: return "🟣 Inside Value (Breakout Imminent)", "கடுமையான சுருக்கம்! பெரிய பிரேக்அவுட் மூவ்மெண்ட் இன்று நிகழும்."
    elif curr_high > prev_high and curr_low < prev_low: return "🔵 Outside Value (Sideways / Rangebound)", "சந்தை பெரிய டிரெண்ட் எடுக்காமல் இரண்டு பக்கமும் அலைபாயும்."
    elif curr_high > prev_high and curr_low >= prev_low: return "🟡 Overlapping Higher (Moderately Bullish)", "சந்தை லேசான பாசிட்டிவ் போக்கில் நகரக்கூடும்."
    elif curr_low < prev_low and curr_high <= prev_high: return "🟠 Overlapping Lower (Moderately Bearish)", "சந்தை லேசான நெகட்டிவ் போக்கில் நகரக்கூடும்."
    else: return "⚪ Unchanged Congestion", "மாற்றங்கள் இல்லை, முந்தைய ரேஞ்சிலேயே நீடிக்கிறது."

row_map = df.set_index("Level")
m_title, m_desc = detect_pivot_relationship(row_map.loc["2 Months Ago", "TC"], row_map.loc["2 Months Ago", "BC"], row_map.loc["Previous Month", "TC"], row_map.loc["Previous Month", "BC"])
w_title, w_desc = detect_pivot_relationship(row_map.loc["2 Weeks Ago", "TC"], row_map.loc["2 Weeks Ago", "BC"], row_map.loc["Previous Week", "TC"], row_map.loc["Previous Week", "BC"])
d_title, d_desc = detect_pivot_relationship(row_map.loc["Previous Daily", "TC"], row_map.loc["Previous Daily", "BC"], row_map.loc["Present Daily", "TC"], row_map.loc["Present Daily", "BC"])
wd_title, wd_desc = detect_pivot_relationship(row_map.loc["Previous Week", "TC"], row_map.loc["Previous Week", "BC"], row_map.loc["Present Daily", "TC"], row_map.loc["Present Daily", "BC"])

# அனாலிசிஸ் ரிப்போர்ட் பாக்ஸ்
st.info(f"**🦅 Month-on-Month View (2 Months Ago ➔ Prev Month):** {m_title}\n\n💡 *{m_desc}*")
st.success(f"**⏳ Week-on-Week View (2 Weeks Ago ➔ Prev Week):** {w_title}\n\n💡 *{w_desc}*")
st.warning(f"**📅 Day-on-Day View (Prev Daily ➔ Pres Daily):** {d_title}\n\n💡 *{d_desc}*")
st.error(f"**🎯 Tactical Core View (Prev Week ➔ Pres Daily):** {wd_title}\n\n💡 *{wd_desc}*")

# --- 5. 4 விதமான சார்ட் வியூ பட்டன்கள் ---
st.subheader("🎯 View Perspective")
selected_tab = st.radio("Select View Range:", [
    "Full Structure View", 
    "Two Month Relationship", 
    "Two Week Relationship", 
    "Two Day & Weekly to Daily View"
], horizontal=True)

if selected_tab == "Full Structure View":
    sub_df = df.copy()
elif selected_tab == "Two Month Relationship":
    sub_df = df[df["Level"].isin(["2 Months Ago", "Previous Month"])].reset_index(drop=True)
elif selected_tab == "Two Week Relationship":
    sub_df = df[df["Level"].isin(["2 Weeks Ago", "Previous Week"])].reset_index(drop=True)
else:
    sub_df = df[df["Level"].isin(["Previous Week", "Previous Daily", "Present Daily"])].reset_index(drop=True)

# --- 6. நிலையான Matplotlib சார்ட் என்ஜின் ---
def plot_mobile_engine(plot_df, ltp):
    fig, ax = plt.subplots(figsize=(10, 6.5))
    x_positions = range(len(plot_df))
    bar_width = 0.4
    all_prices = [ltp]

    for idx, row in plot_df.iterrows():
        x = x_positions[idx]
        all_prices.extend([row["H4"], row["H3"], row["L3"], row["L4"], row["TC"], row["CP"], row["BC"]])
        
        # Camarilla
        ax.hlines(y=row["H4"], xmin=x - bar_width, xmax=x + bar_width, colors="blue", linewidth=2.5)
        ax.text(x, row["H4"] + (ltp*0.0005), f'{row["H4"]:.1f}', ha="center", va="bottom", fontsize=8, color="blue", weight="bold")
        ax.hlines(y=row["H3"], xmin=x - bar_width, xmax=x + bar_width, colors="orange", linewidth=2.5)
        ax.text(x, row["H3"] + (ltp*0.0005), f'{row["H3"]:.1f}', ha="center", va="bottom", fontsize=8, color="red", weight="bold")
        ax.hlines(y=row["L3"], xmin=x - bar_width, xmax=x + bar_width, colors="orange", linestyles="--", linewidth=2)
        ax.text(x, row["L3"] - (ltp*0.0005), f'{row["L3"]:.1f}', ha="center", va="top", fontsize=8, color="red", weight="bold")
        ax.hlines(y=row["L4"], xmin=x - bar_width, xmax=x + bar_width, colors="blue", linestyles="--", linewidth=2)
        ax.text(x, row["L4"] - (ltp*0.0005), f'{row["L4"]:.1f}', ha="center", va="top", fontsize=8, color="blue", weight="bold")
        
        # CPR
        ax.hlines(y=row["TC"], xmin=x - bar_width, xmax=x + bar_width, colors="purple", linestyles=":", linewidth=1.5)
        ax.hlines(y=row["CP"], xmin=x - bar_width, xmax=x + bar_width, colors="purple", linestyles="-.", linewidth=2)
        ax.hlines(y=row["BC"], xmin=x - bar_width, xmax=x + bar_width, colors="purple", linestyles=":", linewidth=1.5)
        ax.text(x - bar_width, row["CP"], f' CP:{row["CP"]:.1f}', ha="left", va="center", fontsize=7.5, color="purple")
        
        # LTP
        ax.hlines(y=ltp, xmin=x - bar_width, xmax=x + bar_width, colors="crimson", linestyles="-", linewidth=1.2, alpha=0.7)
        ax.plot(x, ltp, marker="o", color="crimson", markersize=5)
        if idx == len(plot_df) - 1: ax.text(x + bar_width + 0.02, ltp, f'LTP:{ltp}', va="center", ha="left", color="crimson", weight="bold", fontsize=8.5)

    # Confluence Shading
    if "Previous Week" in plot_df["Level"].values and "Present Daily" in plot_df["Level"].values:
        w_row = plot_df[plot_df["Level"] == "Previous Week"].iloc[0]
        d_row = plot_df[plot_df["Level"] == "Present Daily"].iloc[0]
        all_keys = ["H4", "H3", "L3", "L4", "TC", "CP", "BC"]
        for wk in all_keys:
            for dk in all_keys:
                if abs(w_row[wk] - d_row[dk]) / w_row[wk] <= 0.0015:
                    y_min, y_max = min(w_row[wk], d_row[dk]), max(w_row[wk], d_row[dk])
                    ax.axhspan(y_min - (ltp*0.0002), y_max + (ltp*0.0002), xmin=0.1, xmax=0.9, color="#ff00ff", alpha=0.1)

    ax.set_xticks(x_positions)
    ax.set_xticklabels(plot_df["Level"], fontsize=9.5, weight="bold")
    ax.grid(True, linestyle=":", alpha=0.4)
    ax.set_xlim(-0.5, len(plot_df) - 0.5)
    
    min_p, max_p = min(all_prices), max(all_prices)
    padding = (max_p - min_p) * 0.08
    ax.set_ylim(min_p - padding, max_p + padding)
    plt.tight_layout()
    return fig

st.pyplot(plot_mobile_engine(sub_df, market_close_price))

# --- 7. ஆக்டிவ் டேட்டா டேபிள் மற்றும் PDF டவுன்லோடு ---
st.subheader("📋 Active Data Table")
st.dataframe(df.set_index("Level"), use_container_width=True)

st.subheader("📥 Download Analysis Report")
pdf_path = "Advanced_Multi_Pivot_Report.pdf"
with PdfPages(pdf_path) as pdf:
    for view_name, plot_data in [
        ("Full View Structure", df), 
        ("Two Month Relationship", df[df["Level"].isin(["2 Months Ago", "Previous Month"])]),
        ("Two Week Relationship", df[df["Level"].isin(["2 Weeks Ago", "Previous Week"])]),
        ("Two Day and Weekly to Daily View", df[df["Level"].isin(["Previous Week", "Previous Daily", "Present Daily"])])
    ]:
        fig_pdf = plot_mobile_engine(plot_data.reset_index(drop=True), market_close_price)
        plt.title(f"Market Analysis - {view_name}", fontsize=11, weight="bold", pad=12)
        pdf.savefig(fig_pdf)
        plt.close()

with open(pdf_path, "rb") as pdf_file:
    st.download_button(label="Download Full PDF Matrix Report", data=pdf_file, file_name="Advanced_Multi_Pivot_Report.pdf", mime="application/pdf")
