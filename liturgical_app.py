import streamlit as st
import pandas as pd
from datetime import datetime

# 📘 Configure the Streamlit page
st.set_page_config(page_title="Liturgical Calendar", layout="centered")

# ——————————————
# 🔍 Load the liturgical calendar Excel file
# ——————————————
@st.cache_data
def load_calendar(path):
    df = pd.read_excel(path, sheet_name="Sheet1", engine="openpyxl")
    df.set_index("Event Name", inplace=True)
    return df

# 👇 Update this path if needed
file_path = "LiturgicalCalendar_1_3000.xlsx"
calendar_df = load_calendar(file_path)

# ——————————————
# 📅 Year input + event selection
# ——————————————
st.title("🕯️ Liturgical Calendar Explorer")

year = st.number_input("Select a Year", min_value=1, max_value=3000, value=2024, step=1)

events = list(calendar_df.index)
selected_event = st.selectbox("Choose a Liturgical Event", events)

# ——————————————
# 🧠 Compute and display result
# ——————————————
try:
    date_str = calendar_df.loc[selected_event, year]
    if date_str == "TBD":
        st.warning(f"⚠️ The date for **{selected_event}** in **{year}** is marked TBD.")
    else:
        date_obj = datetime.strptime(date_str, "%d-%b-%Y")
        weekday = date_obj.strftime("%A")
        st.success(f"📅 **{selected_event}** falls on **{weekday}, {date_str}** in **{year}**")
except Exception as e:
    st.error(f"⚠️ Unable to find data: {e}")

# ——————————————
# 📖 Optional: View all events for this year
# ——————————————
with st.expander("📘 View All Events for Selected Year"):
    all_events = calendar_df[year].reset_index()
    all_events.columns = ["Event", "Date"]
    st.dataframe(all_events, use_container_width=True)