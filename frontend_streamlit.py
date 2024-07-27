import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Google Sheets authentication
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
#creds = ServiceAccountCredentials.from_json_keyfile_name("credentials\monitoring-p2m-b170bdcce119.json", scope)
creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets.connections)
client = gspread.authorize(creds)

# Read the first 100 rows from the worksheet
@st.cache_data(ttl=60)
def load_data():
    sheet = client.open("BME680 Monitoring P2M").worksheet("Sheet1")
    data = sheet.get_all_records()
    return data

st.markdown("<h1 style='text-align: center; color: green;'>Green House Monitoring Desa Majalaya, Cianjur</h1>", unsafe_allow_html=True)

# Read data
bme680 = load_data()

# Convert data into a list of dictionaries
data_list = bme680

# Extracting specific data
dates = [row['Date'] for row in data_list]
times = [row['Time'] for row in data_list]
temperatures = [row['Temperature (C)'] for row in data_list]
humidity = [row['Humidity (%)'] for row in data_list]
pressure = [row['Pressure (mbar)'] for row in data_list]
gas_resistance = [row['Gas Resistance (kOhm)'] for row in data_list]

# Combine Date and Time into DateTime
datetimes = [datetime.strptime(f"{date} {time}", "%Y/%m/%d %I:%M:%S %p") for date, time in zip(dates, times)]

current_values = data_list[0]  # Assuming the most recent data is at the top
st.write("----")
st.write("### Kondisi Green House Saat Ini")
columns = st.columns(4)

# CSS styles for columns
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
    </style>
"""

st.markdown(style, unsafe_allow_html=True)

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

if st.button('Refresh Data'):
    st.cache_data.clear()
    st.rerun()

# Create a subplot for each parameter
fig = make_subplots(
    rows=2, cols=2, 
    subplot_titles=('Temperature (C)', 'Humidity (%)', 'Pressure (mbar)', 'Gas (kOhm)'),
    shared_xaxes=False
)

# Add a trace for each parameter
fig.add_trace(
    go.Scatter(x=datetimes, y=temperatures, name='Suhu (C)', mode='lines', line=dict(color='red')),
    row=1, col=1
)

fig.add_trace(
    go.Scatter(x=datetimes, y=humidity, name='Kelembaban (%)', mode='lines', line=dict(color='green')),
    row=1, col=2
)

fig.add_trace(
    go.Scatter(x=datetimes, y=pressure, name='Tekanan (mbar)', mode='lines', line=dict(color='blue')),
    row=2, col=1
)

fig.add_trace(
    go.Scatter(x=datetimes, y=gas_resistance, name='Gas (kOhm)', mode='lines', line=dict(color='yellow')),
    row=2, col=2
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
