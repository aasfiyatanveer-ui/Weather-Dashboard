import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Weather App", page_icon="☀️")

WMO_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
}

def get_wmo(code):
    return WMO_CODES.get(code, "Unknown weather condition")

def wind_direction(degree):
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    index = int(degree / 45) % 8
    return directions[index]

def geocode(city):
    r = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city, "count": 5, "language": "en", "format": "json"},
        timeout=8,
    )
    r.raise_for_status()
    return r.json().get("results", [])

def fetch_weather(lat, lon):
    r = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat,
            "longitude": lon,
            "current": (
                "temperature_2m,apparent_temperature,"
                "relative_humidity_2m,wind_speed_10m,"
                "wind_direction_10m,precipitation,weathercode,uv_index"
            ),
            "hourly": "temperature_2m,precipitation_probability",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
            "timezone": "auto",
            "forecast_days": 7,
        },
        timeout=8,
    )
    r.raise_for_status()
    return r.json()


# ── Streamlit UI ──────────────────────────────────────────
st.title("☀️ Weather App")
st.markdown("Enter a city name to get the current weather and forecast.")

city_input = st.text_input("Enter a City name", placeholder="New York, London, Paris")
unit = st.radio("Select Temperature Unit", ("Celsius", "Fahrenheit"), horizontal=True)

if not city_input:
    st.warning("Please enter a city name to get the weather information.")
    st.stop()

with st.spinner("Fetching location data..."):
    try:
        locations = geocode(city_input)
        if not locations:
            st.error("No locations found. Please try a different city name.")
            st.stop()
    except requests.RequestException as e:
        st.error(f"Error fetching data: {e}")
        st.stop()

options = [
    f"{r['name']}, {r.get('admin1', '')}, {r['country']}"
    for r in locations
]

# ✅ Fixed: pass strings directly — avoids None index bug
chosen = st.selectbox("Select a location", options)
if chosen is None:
    st.info("Please select a location from the dropdown.")
    st.stop()

chosen_index = options.index(chosen)
loc = locations[chosen_index]

with st.spinner("Fetching weather data..."):
    try:
        weather_data = fetch_weather(loc["latitude"], loc["longitude"])
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        st.stop()

cur = weather_data["current"]
daily = weather_data["daily"]
hourly = weather_data["hourly"]

def fmt(c):
    return round(c * 9 / 5 + 32, 1) if unit == "Fahrenheit" else c

st.divider()
desc = get_wmo(cur["weathercode"])
st.subheader("current weather")
st.metric("Temperature", f"{fmt(cur['temperature_2m'])}°{unit[0]}",f"Feels like {fmt(cur['apparent_temperature'])}°{unit[0]}")

col1,col2,col3,col4 = st.columns(4)
col1.metric(":cloudy: Humidity", f"{cur['relative_humidity_2m']}%")
col2.metric(":wind: Wind Speed", f"{fmt(cur['wind_speed_10m'])} m/s")
col3.metric(":droplet: Precipitation", f"{cur['precipitation']} mm")      
col4.metric(":sunny: UV Index", f"{cur['uv_index']}")