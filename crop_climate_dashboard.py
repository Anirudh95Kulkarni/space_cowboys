# crop_climate_dashboard.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import os

# ============================================================
# Load ideal crop conditions from local JSON file
# ============================================================
LOCAL_JSON_PATH = "ideal_conditions.json"

if not os.path.exists(LOCAL_JSON_PATH):
    st.error(f"❌ Missing file: {LOCAL_JSON_PATH}. Please place it in the same folder.")
    st.stop()

with open(LOCAL_JSON_PATH, "r", encoding="utf-8") as f:
    ideal_conditions = json.load(f)

# ============================================================
# Streamlit App Layout
# ============================================================
st.set_page_config(page_title="Crop Climate Dashboard", layout="wide")
st.title("🌾 Crop Growth Suitability Dashboard (Demo Version)")
st.markdown("""
Use this interactive demo to:
1. Input location coordinates  
2. Select a crop  
3. View ideal growing conditions  
4. Compare with simulated climate data  
5. Get a recommendation on whether the crop is suitable  
6. See trend visualization
""")

# ============================================================
# 1️⃣ Input for location
# ============================================================
st.header("📍 Step 1: Location Input")
col1, col2 = st.columns(2)
with col1:
    lat = st.number_input("Latitude", -90.0, 90.0, 23.5, step=0.1)
with col2:
    lon = st.number_input("Longitude", -180.0, 180.0, 88.3, step=0.1)

# ============================================================
# 2️⃣ Select crop type
# ============================================================
st.header("🌱 Step 2: Select Crop Type")
crop = st.selectbox("Select Crop", list(ideal_conditions.keys()))

# ============================================================
# 3️⃣ Display ideal conditions
# ============================================================
st.header(f"🌾 Step 3: Ideal Conditions for {crop}")
ideal_df = pd.DataFrame(list(ideal_conditions[crop].items()), columns=["Parameter", "Ideal Range"])
st.table(ideal_df)

# ============================================================
# 4️⃣ Simulated Local Climate Data
# ============================================================
st.header("🌤 Step 4: Average Annual Climate Data (Simulated)")
np.random.seed(42)

# Generate demo climate data
years = np.arange(2015, 2025)
avg_temp = np.random.uniform(20, 35, len(years))
rainfall = np.random.uniform(800, 2000, len(years))
humidity = np.random.uniform(60, 90, len(years))
sunlight = np.random.uniform(5, 10, len(years))

df = pd.DataFrame({
    "Year": years,
    "Temperature (°C)": avg_temp,
    "Rainfall (mm)": rainfall,
    "Humidity (%)": humidity,
    "Sunlight (hrs/day)": sunlight
})

st.dataframe(df)

# ============================================================
# 5️⃣ Recommendation
# ============================================================
st.header("🧭 Step 5: Crop Suitability Recommendation")

mean_temp = df["Temperature (°C)"].mean()
mean_rain = df["Rainfall (mm)"].mean()
mean_humid = df["Humidity (%)"].mean()
mean_sun = df["Sunlight (hrs/day)"].mean()

st.write(f"**Average Temperature:** {mean_temp:.1f} °C")
st.write(f"**Average Rainfall:** {mean_rain:.1f} mm/year")
st.write(f"**Average Humidity:** {mean_humid:.1f} %")
st.write(f"**Average Sunlight:** {mean_sun:.1f} hrs/day")

# Basic suitability logic
if crop.lower() == "rice":
    suitable = (20 <= mean_temp <= 35) and (1000 <= mean_rain <= 2000) and (70 <= mean_humid <= 85)
elif crop.lower() == "wheat":
    suitable = (10 <= mean_temp <= 25) and (300 <= mean_rain <= 900)
elif crop.lower() == "maize":
    suitable = (18 <= mean_temp <= 27) and (500 <= mean_rain <= 1000)
elif crop.lower() == "soybean":
    suitable = (20 <= mean_temp <= 30) and (500 <= mean_rain <= 900)
else:
    suitable = False

if suitable:
    st.success(f"✅ This location is suitable for growing {crop}.")
else:
    st.error(f"❌ This location may **not be suitable** for growing {crop}.")

# ============================================================
# 6️⃣ Trend visualization
# ============================================================
st.header("📈 Step 6: Climate Condition Trends (Simulated)")

fig, ax1 = plt.subplots(figsize=(8, 5))
ax1.plot(df["Year"], df["Temperature (°C)"], 'r-o', label='Temperature (°C)')
ax2 = ax1.twinx()
ax2.plot(df["Year"], df["Rainfall (mm)"], 'b-s', label='Rainfall (mm)')

ax1.set_xlabel("Year")
ax1.set_ylabel("Temperature (°C)", color='r')
ax2.set_ylabel("Rainfall (mm)", color='b')
plt.title(f"{crop} - Simulated Climate Trends")
st.pyplot(fig)

# ============================================================
# CSV Download Option
# ============================================================
csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Download Climate Data (CSV)",
    data=csv,
    file_name=f"{crop}_climate_data_demo.csv",
    mime="text/csv",
)
