import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from streamlit_js_eval import streamlit_js_eval
r_layout = "wide"

#set up bassic
st.set_page_config(
    page_title="Green House",
    page_icon="https://psikologi.unj.ac.id/wp-content/uploads/2020/10/Logo.png",  
    layout=r_layout, 
    initial_sidebar_state="expanded" 
)
page_width = streamlit_js_eval(js_expressions='window.innerWidth', key='WIDTH',  want_output = True,)

# Google Sheets authentication
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets.connections)
# creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets.connections)
client = gspread.authorize(creds)

# Read the first 100 rows from the worksheet
@st.cache_data(ttl=60)
def load_data(sheet):
    sheet = client.open("BME680 Monitoring P2M").worksheet(sheet)
    data = sheet.get_all_records()
    return data

# header
html_header = """
    <div class="jumbotron" style="display: flex; justify-content: space-around; flex-direction: row; align-items: center;">
        <img class="logo" src="https://psikologi.unj.ac.id/wp-content/uploads/2020/10/Logo.png" alt="logo UNJ" style="width: 100px; height: 100px;margin-right: 20px;"></img>
        <h1 style=' color: green; width: auto;'>Green House Monitoring Desa Majalaya, Cianjur</h1>
    </div>
"""
st.markdown(html_header, unsafe_allow_html=True)


# Read data
sheet_1 = load_data("Sheet1")
sheet_2 = load_data("Sheet2")

# Convert data into a list of dictionaries
data_list_1 = sheet_1
data_list_2 = sheet_2

# Extracting specific data
dates = [row['Date'] for row in data_list_1]
times = [row['Time'] for row in data_list_1]
temperatures = [row['Temperature (C)'] for row in data_list_1]
humidity = [row['Humidity (%)'] for row in data_list_1]
pressure = [row['Pressure (mbar)'] for row in data_list_1]
gas_resistance = [row['Gas Resistance (kOhm)'] for row in data_list_1]
height = [row['Ketinggian'] for row in data_list_2]
concentration = [row['Konsentrasi'] for row in data_list_2]


# Combine Date and Time into DateTime
datetimes = [datetime.strptime(f"{date} {time}", "%Y/%m/%d %I:%M:%S %p") for date, time in zip(dates, times)]

current_values = data_list_1[0]  # Assuming the most recent data is at the top
current_values_2 = data_list_2[0]  # Assuming the most recent data is at the top
st.write("----")
st.write("### Kondisi Green House Saat Ini")
columns = st.columns(6, gap='large')



# Function to create styled markdown for parameters and values
def create_styled_markdown(label, value):
    return f"""
    <div class="parameter-label">{label}</div>
    <div class="current-value">{value}</div>
    """

columns[0].markdown(create_styled_markdown("Suhu (C)", current_values['Temperature (C)']), unsafe_allow_html=True)
columns[1].markdown(create_styled_markdown("Kelembaban (%)", current_values['Humidity (%)']), unsafe_allow_html=True)
columns[2].markdown(create_styled_markdown("tekanan (mbar)", current_values['Pressure (mbar)']), unsafe_allow_html=True)
columns[3].markdown(create_styled_markdown("Gas (kOhm)", current_values['Gas Resistance (kOhm)']), unsafe_allow_html=True)
columns[4].markdown(create_styled_markdown("Ketinggian (cm)", current_values_2['Ketinggian']), unsafe_allow_html=True)
columns[5].markdown(create_styled_markdown("Konsentrasi (ppm)", current_values_2['Konsentrasi']), unsafe_allow_html=True)

if st.button('Refresh Data'):
    st.cache_data.clear()
    st.rerun()

# Create a subplot for each parameter
# setting row and column of graphic
if page_width <= 942:
    row_a, col_a = 1, 1
    row_b, col_b = 1, 2
    row_c, col_c = 2, 1
    row_d, col_d = 2, 2
    row_e, col_e = 3, 1
    row_f, col_f = 3, 2
    row_master, col_master = 3, 2
else:
    row_a, col_a = 1, 1
    row_b, col_b = 1, 2
    row_c, col_c = 1, 3
    row_d, col_d = 2, 1
    row_e, col_e = 2, 2
    row_f, col_f = 2, 3
    row_master, col_master = 2, 3
fig = make_subplots(
    rows=row_master, cols=col_master, 
    subplot_titles=('Temperature (C)', 'Humidity (%)', 'Pressure (mbar)', 'Gas (kOhm)', 'Ketinggian (cm)', 'Konsentrasi (ppm)'),
    shared_xaxes=False
)


# Add a trace for each parameter
fig.add_trace(
    go.Scatter(x=datetimes, y=temperatures, name='Suhu (C)', mode='lines', line=dict(color='red')),
    row=row_a, col=col_a
)

fig.add_trace(
    go.Scatter(x=datetimes, y=humidity, name='Kelembaban (%)', mode='lines', line=dict(color='green')),
    row=row_b, col=col_b
)

fig.add_trace(
    go.Scatter(x=datetimes, y=pressure, name='Tekanan (mbar)', mode='lines', line=dict(color='blue')),
    row=row_c, col=col_c
)

fig.add_trace(
    go.Scatter(x=datetimes, y=gas_resistance, name='Gas (kOhm)', mode='lines', line=dict(color='yellow')),
    row=row_d, col=col_d
)
fig.add_trace(
    go.Scatter(x=datetimes, y=height, name='Ketinggian (cm)', mode='lines', line=dict(color='#ffbd31')),
    row=row_e, col=col_e
)
fig.add_trace(
    go.Scatter(x=datetimes, y=concentration, name='Konsentrasi (ppm)', mode='lines', line=dict(color='black')),
    row=row_f, col=col_f
)

# Update layout for better visualization
fig.update_layout(
    height=800,
    title_text="Parameter Monitoring Green House",
    showlegend=False,
    xaxis_title='Waktu',
    xaxis2_title='Waktu',
    xaxis3_title='Waktu',
    xaxis4_title='Waktu',
)

# Display the plot in Streamlit
st.plotly_chart(fig)

# CSS
style = """
    <style>
    .current-value {
        font-size: 24px;
        font-weight: bold;
        color: #ff4b4b;
    }
    .parameter-label {
        font-size: 18px;
        color: #4b4bff;
    }
    @media screen and (max-width: 500px) {
        .logo {
            display: none;
        }
    }
    </style>
"""
st.markdown(style, unsafe_allow_html=True)
