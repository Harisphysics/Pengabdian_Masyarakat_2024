import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots
from streamlit_gsheets import GSheetsConnection 

# Create a connection to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Read the first 100 rows from the worksheet
@st.cache_data(ttl=60)
def load_data():
    return conn.read(
        worksheet="Sheet1",
        ttl="10m",
        nrows=500  # Add this parameter to read the first 100 rows
    )

st.markdown("<h1 style='text-align: center; color: green;'>Green House Monitoring Desa Majalaya, Cianjur</h1>", unsafe_allow_html=True)

# Read data
bme680 = load_data()
# # Display the dataframe in Streamlit
# st.write("Data from Google Sheets:", bme680)

bme680['DateTime'] = pd.to_datetime(bme680['Date'] + ' ' + bme680['Time'])
bme680.drop(columns=['Date', 'Time'], inplace=True)

current_values = bme680.iloc[0]  # Assuming the most recent data is at the top
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
    st.experimental_rerun()

# Create a subplot for each parameter
fig = make_subplots(
    rows=2, cols=2, 
    subplot_titles=('Temperature (C)', 'Humidity (%)', 'Pressure (mbar)', 'Gas Resistance (kOhm)'),
    shared_xaxes=False
)

# Add a trace for each parameter
fig.add_trace(
    go.Scatter(x=bme680['DateTime'], y=bme680['Temperature (C)'], name='Suhu (C)', mode='lines', line=dict(color='red')),
    row=1, col=1
)

fig.add_trace(
    go.Scatter(x=bme680['DateTime'], y=bme680['Humidity (%)'], name='Kelembaban (%)', mode='lines', line=dict(color='green')),
    row=1, col=2
)

fig.add_trace(
    go.Scatter(x=bme680['DateTime'], y=bme680['Pressure (mbar)'], name='Tekanan (mbar)', mode='lines', line=dict(color='blue')),
    row=2, col=1
)

fig.add_trace(
    go.Scatter(x=bme680['DateTime'], y=bme680['Gas Resistance (kOhm)'], name='Gas Resistance (kOhm)', mode='lines', line=dict(color='yellow')),
    row=2, col=2
)

# Update layout for better visualization
fig.update_layout(
    height=800,
    title_text="Parameter Monitoring Green House",
    showlegend=False,
    xaxis_title='Waktu',
    yaxis_title='Nilai',
    xaxis2_title='Waktu',
    yaxis2_title='Nilai',
    xaxis3_title='Waktu',
    yaxis3_title='Nilai',
    xaxis4_title='Waktu',
    yaxis4_title='Nilai',
)

# Display the plot in Streamlit
st.plotly_chart(fig)
