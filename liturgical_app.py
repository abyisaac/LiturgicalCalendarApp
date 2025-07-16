import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF

# 🌈 Custom CSS for elegant UI and hiding Streamlit branding
st.markdown("""
    <style>
    html, body {
        font-family: 'Segoe UI', sans-serif;
        background-color: #f3f6fa;
    }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
    .heading-banner {
        font-size: 32px;
        font-weight: 700;
        text-align: center;
        color: white;
        padding: 12px 16px;
        border-radius: 10px;
        margin-bottom: 20px;
        background-color: #800000;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        letter-spacing: 0.8px;
    }
    .intro-text {
        text-align: center;
        font-size: 16px;
        color: #333333;
        margin-bottom: 30px;
        padding: 0 20px;
    }
    .calendar-box {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
    }
    .highlight-box {
        background: linear-gradient(135deg, #fdf6f0, #f0e6dc);
        border-left: 6px solid #800000;
        padding: 16px;
        border-radius: 10px;
        margin-bottom: 24px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    .custom-label {
        font-size: 17px;
        font-weight: bold;
        color: #333333;
        margin-top: 16px;
    }
    .small-subheader {
        font-size: 15px !important;
        font-weight: 600;
        color: #800000;
        margin-top: 24px;
    }
    .stDownloadButton button {
        font-size: 16px !important;
        font-weight: 600 !important;
        background-color: #800000 !important;
        color: white !important;
        border-radius: 8px;
        padding: 10px 20px;
        margin-top: 24px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# 📘 Page setup
st.set_page_config(page_title="Liturgical Calendar", page_icon="🕯️", layout="centered")
st.markdown("<div class='heading-banner'>🕯️ Liturgical Year Explorer</div>", unsafe_allow_html=True)

# 📘 Intro paragraph
st.markdown("""
    <div class='intro-text'>
        This app presents key liturgical dates observed by the <strong>Malankara Mar Thoma Syrian Church</strong>, following the <strong>Gregorian calendar</strong>. You can select any year and event to view its exact weekday and date. Events can also be filtered by month. The calendar spans from <strong>AD 1583 to 3000</strong>, making it useful for both current and historical reference. A <strong>downloadable PDF version</strong> is available for offline use, study, or sharing.
    </div>
""", unsafe_allow_html=True)

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
            formatted = f"{weekday}, {date_str}"
            st.markdown(f"""
                <div class='highlight-box'>
                    <div style='font-size:18px; font-weight:600; margin-bottom:6px;'>{selected_event}</div>
                    <div style='font-size:22px; font-family:Segoe UI, sans-serif; color:#003366;'>{formatted}</div>
                </div>
            """, unsafe_allow_html=True)
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
                    weekday = date_obj.strftime("%A")
                    month_filtered.append((event, f"{weekday}, {date_str}"))
            except:
                pass

    if month_filtered:
        st.markdown(f"<div class='small-subheader'>📘 Events in {selected_month} {year}</div>", unsafe_allow_html=True)
        df_month = pd.DataFrame(month_filtered, columns=["Day of Importance", "Day & Date"])
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
        self.cell(50, 6, "Day & Date", border=1, align="C")
        self.ln()

    def footer(self):
        pass

    def add_table(self, data):
        self.set_font("Arial", "", 8)
        row_height = 5.0
        self.set_y(self.get_y())
        for idx, (event, date_str) in enumerate(data, start=1):
            self.set_x(20)
            self.cell(20, row_height, str(idx), border=1, align="C")
            self.cell(100, row_height, str(event), border=1, align="L")
            self.cell(50, row_height, str(date_str), border=1, align="C")
            self.ln()

def create_year_pdf(year):
    data_pairs = []
    for event in calendar_df.index:
        date_str = calendar_df.loc[event, year]
        if pd.notna(date_str) and date_str != "TBD":
            try:
                date_obj = datetime.strptime(date_str, "%d-%b-%Y")
                weekday = date_obj.strftime("%A")
                formatted = f"{weekday}, {date_str}"
                data_pairs.append((event, formatted))
            except:
                data_pairs.append((event, date_str))
        else:
            data_pairs.append((event, date_str))
    pdf = PDFGenerator("P", "mm", "A4")
    pdf.add_page()
    pdf.add_table(data_pairs)
    return pdf.output(dest="S").encode("latin-1")

pdf_bytes = create_year_pdf(year)

st.download_button(
    label=f"⬇️ Download Full Calendar for AD {year} as PDF",
    data=pdf_bytes,
    file_name=f"LiturgicalCalendar_AD{year}.pdf",
    mime="application/pdf"
)