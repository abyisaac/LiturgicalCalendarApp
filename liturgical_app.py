import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF

# 🌈 Custom CSS for heading and layout
st.markdown("""
    <style>
    html, body {
        font-family: 'Segoe UI', sans-serif;
        background-color: #f3f6fa;
    }
    .heading-banner {
        font-size: 36px;
        font-weight: 700;
        text-align: center;
        color: white;
        padding: 16px;
        border-radius: 12px;
        margin-bottom: 25px;
        background-color: #800000;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        letter-spacing: 1px;
    }
    .calendar-box {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .highlight {
        background-color: #e8f0fe;
        padding: 10px;
        border-radius: 8px;
        font-size: 18px;
        margin-bottom: 16px;
        color: #003366;
    }
    .custom-label {
        font-size: 18px;
        font-weight: bold;
        color: #333333;
        margin-top: 10px;
    }
    .small-subheader {
        font-size: 16px !important;
        font-weight: 600;
        color: #800000;
        margin-top: 20px;
    }
    .stDownloadButton button {
        font-size: 18px !important;
        font-weight: bold !important;
        background-color: #800000 !important;
        color: white !important;
        border-radius: 6px;
        padding: 10px 20px;
        margin-top: 20px;
    }
    [data-testid="stElementToolbar"] {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# 📘 Page setup
st.set_page_config(page_title="Liturgical Calendar", layout="centered")
st.markdown("<div class='heading-banner'>🕯️ Liturgical Year Explorer</div>", unsafe_allow_html=True)

# 📄 Load calendar data
@st.cache_data
def load_calendar(path):
    df = pd.read_excel(path, sheet_name="Sheet1", engine="openpyxl")
    df.set_index("Event Name", inplace=True)
    return df

file_path = "LiturgicalCalendar_1583_3000.xlsx"
calendar_df = load_calendar(file_path)

with st.container():
    st.markdown("<div class='calendar-box'>", unsafe_allow_html=True)

    today = datetime.today()
    current_year = today.year
    current_month = today.strftime("%B")

    st.markdown("<div class='custom-label'>Select a Year <span style='font-weight:normal;'>(or type a year)</span></div>", unsafe_allow_html=True)
    year = st.number_input("Select a Year", min_value=1583, max_value=3000, value=current_year, step=1)

    st.markdown("<div class='custom-label'>Choose a Liturgical Event</div>", unsafe_allow_html=True)
    events = list(calendar_df.index)
    selected_event = st.selectbox("Choose a Liturgical Event", events, placeholder="Type or choose from list")

    try:
        date_str = calendar_df.loc[selected_event, year]
        if date_str == "TBD":
            st.warning(f"⚠️ The date for **{selected_event}** in **{year}** is marked TBD.")
        else:
            date_obj = datetime.strptime(date_str, "%d-%b-%Y")
            weekday = date_obj.strftime("%A")
            st.markdown(
                f"<div class='highlight'>📅 <strong>{selected_event}</strong> falls on <strong>{weekday}, {date_str}</strong></div>",
                unsafe_allow_html=True
            )
    except Exception as e:
        st.error(f"⚠️ Unable to find data for {selected_event}: {e}")

    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    st.markdown("<div class='custom-label'>Filter Events by Month</div>", unsafe_allow_html=True)
    selected_month = st.selectbox("Filter Events by Month", month_names, index=month_names.index(current_month))

    month_filtered = []
    for event in calendar_df.index:
        date_str = calendar_df.loc[event, year]
        if pd.notna(date_str) and date_str != "TBD":
            try:
                date_obj = datetime.strptime(date_str, "%d-%b-%Y")
                if date_obj.strftime("%B") == selected_month:
                    month_filtered.append((event, date_str))
            except:
                pass

    if month_filtered:
        st.markdown(f"<div class='small-subheader'>📘 Events in {selected_month} {year}</div>", unsafe_allow_html=True)
        df_month = pd.DataFrame(month_filtered, columns=["Day of Importance", "Date"])
        st.dataframe(df_month, use_container_width=True)
    else:
        st.info(f"No events found in {selected_month} {year}.")

    st.markdown("</div>", unsafe_allow_html=True)

# 📄 PDF Generator
class PDFGenerator(FPDF):
    def header(self):
        self.set_font("Arial", "B", 11)
        self.set_y(12)
        self.cell(0, 8, f"Liturgical Calendar for AD {year}", ln=True, align="C")
        self.set_font("Arial", "B", 9)
        self.set_x(20)
        self.cell(20, 6, "Sl. No.", border=1, align="C")
        self.cell(100, 6, "Day of Importance", border=1, align="C")
        self.cell(50, 6, "Date", border=1, align="C")
        self.ln()

    def footer(self):
        pass

    def add_table(self, data):
        self.set_font("Arial", "", 8)
        row_height = 5.0
        self.set_y(self.get_y())
        for idx, (event, date) in enumerate(data, start=1):
            self.set_x(20)
            self.cell(20, row_height, str(idx), border=1, align="C")
            self.cell(100, row_height, str(event), border=1, align="L")
            self.cell(50, row_height, str(date), border=1, align="C")
            self.ln()

def create_year_pdf(year):
    data_pairs = list(zip(calendar_df.index, calendar_df[year]))
    pdf = PDFGenerator("P", "mm", "A4")
    pdf.add_page()
    pdf.add_table(data_pairs)
    return pdf.output(dest="S").encode("latin-1")

pdf_bytes = create_year_pdf(year)

st.download_button(
    label=f"⬇️ **Download Full Calendar for AD {year} as PDF**",
    data=pdf_bytes,
    file_name=f"LiturgicalCalendar_AD{year}.pdf",
    mime="application/pdf"
)