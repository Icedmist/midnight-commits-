"""
Weather API Consumer
Fetch and display weather data from OpenWeatherMap API
"""

import requests
import json
from typing import Dict, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WeatherClient:
    """OpenWeatherMap API client"""

    BASE_URL = "https://api.openweathermap.org/data/2.5"
    
    def __init__(self, api_key: str):
        """Initialize with API key"""
        self.api_key = api_key
        self.session = requests.Session()

    def get_current_weather(self, city: str, units: str = "metric") -> Optional[Dict]:
        """Get current weather for a city"""
        try:
            url = f"{self.BASE_URL}/weather"
            params = {
                "q": city,
                "appid": self.api_key,
                "units": units
            }
            response = self.session.get(url, params=params, timeout=5)
            response.raise_for_status()
            logger.info(f"✅ Got weather for {city}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ API Error: {e}")
            return None

    def get_forecast(self, city: str, units: str = "metric") -> Optional[Dict]:
        """Get 5-day forecast"""
        try:
            url = f"{self.BASE_URL}/forecast"
            params = {
                "q": city,
                "appid": self.api_key,
                "units": units
            }
            response = self.session.get(url, params=params, timeout=5)
            response.raise_for_status()
            logger.info(f"✅ Got forecast for {city}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ API Error: {e}")
            return None

    def get_by_coordinates(self, lat: float, lon: float, units: str = "metric") -> Optional[Dict]:
        """Get weather by coordinates"""
        try:
            url = f"{self.BASE_URL}/weather"
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": units
            }
            response = self.session.get(url, params=params, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ API Error: {e}")
            return None

    def format_weather(self, data: Dict) -> str:
        """Format weather data for display"""
        if not data:
            return "No data available"
        
        city = data.get("name", "Unknown")
        temp = data.get("main", {}).get("temp", "N/A")
        feels_like = data.get("main", {}).get("feels_like", "N/A")
        humidity = data.get("main", {}).get("humidity", "N/A")
        pressure = data.get("main", {}).get("pressure", "N/A")
        description = data.get("weather", [{}])[0].get("description", "N/A")
        wind_speed = data.get("wind", {}).get("speed", "N/A")
        
        return f"""
🌍 {city}
📊 Temperature: {temp}°C (feels like {feels_like}°C)
💧 Humidity: {humidity}%
🌪️  Wind Speed: {wind_speed} m/s
🔽 Pressure: {pressure} hPa
📝 Condition: {description.title()}
"""

    def close(self) -> None:
        """Close session"""
        self.session.close()


def demo_weather():
    """Demo weather client"""
    api_key = "YOUR_API_KEY_HERE"  # Get from openweathermap.org
    
    client = WeatherClient(api_key)
    
    cities = ["London", "New York", "Tokyo"]
    
    for city in cities:
        weather = client.get_current_weather(city)
        if weather:
            print(client.format_weather(weather))
    
    client.close()


if __name__ == "__main__":
    print("🌤️ Weather API Consumer\n")
    
    print("Setup:")
    print("1. Get free API key from: https://openweathermap.org/api")
    print("2. pip install requests")
    print("3. Replace 'YOUR_API_KEY_HERE' with your key")
    print("\nFeatures:")
    print("✓ Current weather")
    print("✓ 5-day forecasts")
    print("✓ Coordinates lookup")
    print("✓ Multiple units (metric/imperial)")
