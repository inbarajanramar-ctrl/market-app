import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# மொபைலுக்கு ஏற்றவாறு பக்கத்தை அமைத்தல்
st.set_page_config(page_title="Multi-Pivot Matrix Tool", layout="centered")

st.title("📊 Multi-Pivot Matrix Engine")
st.write("Compare Present vs Previous Frameworks with Mobile Pinch-to-Zoom")

# --- 1. லெவல்களை மாற்றும் பகுதி (Sidebar input panel) ---
st.sidebar.header("📝 Edit Matrix Data")

# புதுப்பிக்கப்பட்ட முந்தைய வார எண்கள் அடங்கிய ஆரம்பகால தரவுகள் (Handwritten + New Weekly Data)
default_data = {
    "Level": ["Yearly", "Present Monthly", "Previous Weekly", "Present Weekly", "Previous Daily", "Present Daily"],
    "H4": [28649.78, 24218.50, 23939.26, 24217.40, 24016.90, 24187.09],
    "H3": [27389.69, 23883.13, 23781.08, 24115.25, 23920.50, 24104.37],
    "L3": [24869.51, 23212.37, 23464.72, 23910.95, 23727.70, 23938.93],
    "L4": [23609.42, 22877.00, 23306.54, 23808.80, 23631.30, 23856.21],
    "TC": [25431.31, 23872.32, 23534.52, 24009.91, 23960.23, 23994.32],
    "CP": [24733.02, 23764.13, 23446.13, 24006.72, 23914.85, 23966.98],
    "BC": [24034.73, 23655.94, 23357.75, 24003.53, 23869.47, 23939.65]
}

# புதிய எண்களைச் சேமிப்பதற்கான டிக்ஸ்னரி
updated_data = {"Level": ["Yearly", "Present Monthly", "Previous Weekly", "Present Weekly", "Previous Daily", "Present Daily"]}
for col in ["H4", "H3", "L3", "L4", "TC", "CP", "BC"]:
    updated_data[col] = []

# ஒவ்வொரு பிரிவிற்கும் இன்புட் பாக்ஸ்கள் (குழப்பமில்லாத மேப்பிங் குறியீட்டுடன்)
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

# --- 3. வியூ பட்டன்கள் ---
st.subheader("🎯 View Perspective")
selected_tab = st.radio("Select View Range:", ["Full Structure View", "Tactical Present View (W & D)"], horizontal=True)

if selected_tab == "Full Structure View":
    sub_df = df.copy()
else:
    sub_df = df[df["Level"].isin(["Present Weekly", "Present Daily"])].reset_index(drop=True)

# --- 4. Plotly இன்டрак்டிவ் மொபைல் ஜூம் என்ஜின் ---
def plot_plotly_mobile_engine(plot_df, ltp):
    fig = go.Figure()
    all_prices = [ltp]
    x_labels = list(plot_df["Level"])
    
    for idx, row in plot_df.iterrows():
        all_prices.extend([row["H4"], row["H3"], row["L3"], row["L4"], row["TC"], row["CP"], row["BC"]])
        
        # 1. Camarilla Highs
        fig.add_trace(go.Scatter(x=[idx-0.25, idx+0.25], y=[row["H4"], row["H4"]], mode="lines+text",
                                 line=dict(color="#0044ff", width=3), text=[f'{row["H4"]:.1f}', ""], textposition="top center", showlegend=False))
        fig.add_trace(go.Scatter(x=[idx-0.25, idx+0.25], y=[row["H3"], row["H3"]], mode="lines+text",
                                 line=dict(color="#ff8800", width=3), text=[f'{row["H3"]:.1f}', ""], textposition="top center", showlegend=False))
        
        # 2. Camarilla Lows
        fig.add_trace(go.Scatter(x=[idx-0.25, idx+0.25], y=[row["L3"], row["L3"]], mode="lines+text",
                                 line=dict(color="#ff8800", width=2, dash="dash"), text=[f'{row["L3"]:.1f}', ""], textposition="bottom center", showlegend=False))
        fig.add_trace(go.Scatter(x=[idx-0.25, idx+0.25], y=[row["L4"], row["L4"]], mode="lines+text",
                                 line=dict(color="#0044ff", width=2, dash="dash"), text=[f'{row["L4"]:.1f}', ""], textposition="bottom center", showlegend=False))
        
        # 3. CPR Channels
        fig.add_trace(go.Scatter(x=[idx-0.25, idx+0.25], y=[row["TC"], row["TC"]], mode="lines", line=dict(color="#8800cc", width=1, dash="dot"), showlegend=False))
        fig.add_trace(go.Scatter(x=[idx-0.25, idx+0.25], y=[row["CP"], row["CP"]], mode="lines+text", line=dict(color="#8800cc", width=2, dash="dashdot"),
                                 text=[f'CP:{row["CP"]:.1f}', ""], textposition="middle left", showlegend=False))
        fig.add_trace(go.Scatter(x=[idx-0.25, idx+0.25], y=[row["BC"], row["BC"]], mode="lines", line=dict(color="#8800cc", width=1, dash="dot"), showlegend=False))
        
        # 4. LTP Close Markers
        fig.add_trace(go.Scatter(x=[idx-0.25, idx+0.25], y=[ltp, ltp], mode="lines", line=dict(color="#dc143c", width=1.5), showlegend=False))
        fig.add_trace(go.Scatter(x=[idx], y=[ltp], mode="markers", marker=dict(color="#dc143c", size=7), showlegend=False))

    # LTP மார்க்கர் லேபிள்
    fig.add_trace(go.Scatter(x=[len(plot_df)-1], y=[ltp], mode="text", text=[f'LTP: {ltp:.2f}'], textposition="middle right", font=dict(color="#dc143c", size=10), showlegend=False))

    # 5. ஆட்டோமேட்டிக் Confluence Zone (பிழை முழுமையாகச் சரிசெய்யப்பட்டுள்ளது)
    if "Present Weekly" in plot_df["Level"].values and "Present Daily" in plot_df["Level"].values:
        w_row = plot_df[plot_df["Level"] == "Present Weekly"].iloc[0]
        d_row = plot_df[plot_df["Level"] == "Present Daily"].iloc[0]
        w_idx = list(plot_df["Level"]).index("Present Weekly")
        d_idx = list(plot_df["Level"]).index("Present Daily")
        
        all_keys = ["H4", "H3", "L3", "L4", "TC", "CP", "BC"]
        for wk in all_keys:
            for dk in all_keys:
                if abs(w_row[wk] - d_row[dk]) / w_row[wk] <= 0.0015:
                    y_min, y_max = min(w_row[wk], d_row[dk]), max(w_row[wk], d_row[dk])
                    fig.add_shape(type="rect", x0=w_idx, y0=y_min-5, x1=d_idx, y1=y_max+5, fillcolor="#ff00ff", opacity=0.1, line_width=0)

    # 6. மொபைல் வியூ வடிவமைப்பு
    min_p, max_p = min(all_prices), max(all_prices)
    padding = (max_p - min_p) * 0.08
    
    fig.update_layout(
        xaxis=dict(tickvals=list(range(len(plot_df))), ticktext=x_labels, tickfont=dict(size=10, weight="bold"), fixedrange=True),
        yaxis=dict(range=[min_p - padding, max_p + padding], gridcolor="#eeeeee"),
        margin=dict(l=15, r=45, t=20, b=20),
        plot_bgcolor="white",
        dragmode="pan"
    )
    return fig

# திரையில் இன்டராக்டிவ் சார்ட்டைக் காட்டுதல்
st.plotly_chart(plot_plotly_mobile_engine(sub_df, market_close_price), use_container_width=True, config={'scrollZoom': True})

# --- 5. டேபிள் காட்டுகின்ற பகுதி ---
st.subheader("📋 Active Data Table")
st.dataframe(df.set_index("Level"), use_container_width=True)
