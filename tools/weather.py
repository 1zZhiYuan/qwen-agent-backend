# =========================
# weather.py
# 天气查询工具
# =========================


# 【移动4】
import requests


# 【移动5】
def get_weather(city):

    try:

        # =========================
        # 第一步：城市名称 → 经纬度
        # =========================

        geocoding_url = (
            "https://geocoding-api.open-meteo.com/v1/search"
        )


        geocoding_params = {
            "name": city,
            "count": 1,
            "language": "zh",
            "format": "json"
        }


        geocoding_response = requests.get(
            geocoding_url,
            params=geocoding_params,
            timeout=10
        )


        geocoding_response.raise_for_status()


        geocoding_data = (
            geocoding_response.json()
        )


        if not geocoding_data.get("results"):

            return f"没有找到城市：{city}"


        location = (
            geocoding_data["results"][0]
        )


        latitude = location["latitude"]

        longitude = location["longitude"]

        city_name = location["name"]


        # =========================
        # 第二步：经纬度 → 当前天气
        # =========================

        weather_url = (
            "https://api.open-meteo.com/v1/forecast"
        )


        weather_params = {
            "latitude": latitude,

            "longitude": longitude,

            "current": (
                "temperature_2m,"
                "apparent_temperature,"
                "precipitation,"
                "weather_code,"
                "wind_speed_10m"
            ),

            "timezone": "auto"
        }


        weather_response = requests.get(
            weather_url,
            params=weather_params,
            timeout=10
        )


        weather_response.raise_for_status()


        weather_data = (
            weather_response.json()
        )


        current = weather_data["current"]


        result = {
            "city": city_name,

            "temperature":
                current["temperature_2m"],

            "apparent_temperature":
                current["apparent_temperature"],

            "precipitation":
                current["precipitation"],

            "weather_code":
                current["weather_code"],

            "wind_speed":
                current["wind_speed_10m"]
        }


        return result


    except requests.exceptions.RequestException as e:

        return (
            f"天气查询失败，网络请求出现问题：{str(e)}"
        )


    except KeyError as e:

        return (
            f"天气查询失败，返回的数据格式异常，"
            f"缺少字段：{str(e)}"
        )


    except Exception as e:

        return (
            f"天气查询失败，发生未知错误：{str(e)}"
        )