import json
import os
from datetime import datetime, timedelta, timezone

import boto3
import pyexcel
import requests

IST = timezone(timedelta(hours=5, minutes=30))


class CityWeather:
    def __init__(self, name, data):
        self.name = name
        self.temp = data["main"]["temp"]
        self.min_temp = data["main"]["temp_min"]
        self.max_temp = data["main"]["temp_max"]
        self.description = data["weather"][0]["description"]
        self.feels_like = data["main"]["feels_like"]
        self.pressure = data["main"]["pressure"]
        self.humidity = data["main"]["humidity"]
        self.visibility = data["visibility"]

    def _format_temp(self):
        self.temp = round(self.temp - 273.15, 2)
        self.min_temp = round(self.min_temp - 273.15)
        self.max_temp = round(self.max_temp - 273.15)
        self.feels_like = round(self.feels_like - 273.15)


def main(event, context):
    cities = json.loads(os.environ["CITIES"])

    API_KEY = os.getenv("API_KEY")

    WEATHER_URL = os.getenv("WEATHER_URL")
    GEO_URL = os.getenv("GEO_URL")

    sheet_data = [["Weather Data", str(datetime.now())]]
    sheet_data.append(
        [
            "Name",
            "Temperature(°C)",
            "Min Temperature(°C)",
            "Max Temperature(°C)",
            "Description",
            "Feels Like(°C)",
            "Pressure(hPa)",
            "Humidity(%)",
            "Visibility(m)",
        ]
    )
    for city in cities:
        city_data = requests.get(GEO_URL, params={"q": city, "appid": API_KEY})
        city_data_dict = json.loads(city_data.content)
        params = {
            "lat": city_data_dict[0]["lat"],
            "lon": city_data_dict[0]["lon"],
            "appid": API_KEY,
        }
        city_weather = requests.get(WEATHER_URL, params=params)
        city_weather_content = json.loads(city_weather.content)
        city_obj = CityWeather(city, data=city_weather_content)
        city_obj._format_temp()
        sheet_data.append(list(vars(city_obj).values()))

    file_name = datetime.now(IST).strftime("%Y%m%d-%H%M%S")

    sheet = pyexcel.Sheet(sheet_data)
    sheet.save_as(f"/tmp/{file_name}.xlsx")

    client = boto3.client("s3")
    BUCKET_NAME = os.getenv("BUCKET_NAME")
    DIR_PREFIX = os.getenv("DIR_PREFIX")

    try:
        client.upload_file(
            f"/tmp/{file_name}.xlsx", BUCKET_NAME, f"{DIR_PREFIX}/{file_name}.xlsx"
        )

    except Exception as e:
        raise e

    finally:
        if os.path.exists(f"/tmp/{file_name}.xlsx"):
            os.remove(f"/tmp/{file_name}.xlsx")

    return {
        "statusCode": 200,
        "body": "Current Weather for multiple cities have been updated!",
    }
