import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="India Population Chatbot", page_icon="🇮🇳", layout="centered")
st.title("🇮🇳 India Population Chatbot (World Bank Live)")

# -------------------------------
# 1️⃣ Load Population Data (Hidden)
# -------------------------------
@st.cache_data
def load_population_data():
    urls = {
        "Male": "https://api.worldbank.org/v2/country/IN/indicator/SP.POP.TOTL.MA.IN?format=json",
        "Female": "https://api.worldbank.org/v2/country/IN/indicator/SP.POP.TOTL.FE.IN?format=json",
        "Total": "https://api.worldbank.org/v2/country/IN/indicator/SP.POP.TOTL?format=json"
    }

    all_data = []
    headers = {"User-Agent": "Mozilla/5.0"}

    for gender, url in urls.items():
        try:
            r = requests.get(url, headers=headers, timeout=30)
            r.raise_for_status()
            data = r.json()[1]  # 2nd element has actual records
            for entry in data:
                if entry["value"] is not None:
                    all_data.append({
                        "Year": int(entry["date"]),
                        "Gender": gender,
                        "Population": int(entry["value"])
                    })
        except Exception as e:
            st.error(f"⚠️ Error fetching {gender} data: {e}")

    df = pd.DataFrame(all_data)
    df.sort_values(by="Year", inplace=True)
    return df

df = load_population_data()

# -------------------------------
# 2️⃣ Chat Interface (Dataset Hidden)
# -------------------------------
if not df.empty:
    st.subheader("💬 Ask about India's Population")

    query = st.text_input("Example: 'Show male population in 2021' or 'Total population in 2010'")

    if query:
        query = query.lower()
        gender = None
        year = None

        # Detect gender
        for g in ["male", "female", "total"]:
            if g in query:
                gender = g.capitalize()
                break

        # Detect year
        for y in df["Year"].unique():
            if str(y) in query:
                year = int(y)
                break

        # Answer generation
        if gender and year:
            result = df[(df["Gender"] == gender) & (df["Year"] == year)]
            if not result.empty:
                val = result["Population"].values[0]
                st.success(f"👨‍👩‍👧 {gender} population in {year} was **{val:,}**.")
            else:
                st.warning("No data found for that year and gender.")
        elif gender:
            recent = df[df["Gender"] == gender].iloc[-1]
            st.info(f"Latest {gender} population (Year {recent['Year']}) is **{recent['Population']:,}**.")
        else:
            st.info("Please mention a gender (male/female/total) and optionally a year.")
else:
    st.error("❌ Could not load data. Please check your internet connection.")
