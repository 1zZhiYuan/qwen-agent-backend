# =========================
# tools.py
# 负责保存 Agent 使用的工具
# =========================


import os

from datetime import datetime

import requests

# 【新增1】
import dashscope

# 【新增2】
from dashscope import Generation

from dotenv import load_dotenv

# 【新增10】
from config import SEARCH_MODEL

load_dotenv()


# =========================
# 1. Python 工具函数
# =========================


def calculator(a, b):
    return a + b


def get_current_time():

    current_time = datetime.now()

    return current_time.strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def get_weather(city):

    try:

        # =========================
        # 第一步：城市 → 经纬度
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


# =========================================================
# Web Search Tool
# =========================================================


# 【修改3】
# 不再调用 Tavily
# 改成使用百炼官方联网搜索
def web_search(query):

    api_key = os.getenv(
        "DASHSCOPE_API_KEY"
    )


    if not api_key:

        return (
            "网页搜索失败："
            "没有读取到 DASHSCOPE_API_KEY"
        )


    try:

        search_messages = [
            {
                "role": "user",
                "content": query
            }
        ]

        response = Generation.call(
            api_key=api_key,

            # 【修改11】
            model=SEARCH_MODEL,

            messages=search_messages,

            enable_search=True,

            search_options={
                "forced_search": True,
                "enable_source": True
            },

            result_format="message"
        )


        if response.status_code != 200:

            return (
                "网页搜索失败："
                f"{response.code} - "
                f"{response.message}"
            )


        search_info = (
            response
            .output
            .search_info
        )


        search_results = (
            search_info["search_results"]
            if search_info
            else []
        )


        if not search_results:

            return "没有搜索到相关网页。"


        results = []


        # 【修改1】
        # enumerate 可以在遍历时，同时得到编号
        for index, item in enumerate(
            search_results[:5],
            start=1
        ):

            result = {

                # 【新增2】
                # 给每个来源一个编号
                "source_id": index,

                "title": item.get(
                    "title",
                    ""
                ),

                "url": item.get(
                    "url",
                    ""
                ),

                "content": item.get(
                    "snippet",
                    item.get(
                        "content",
                        ""
                    )
                )
            }


            results.append(
                result
            )


        return results


    except Exception as e:

        return (
            "网页搜索失败："
            f"{str(e)}"
        )


# =========================
# 2. Tool Registry
# =========================


tool_functions = {
    "calculator": calculator,

    "get_current_time": get_current_time,

    "get_weather": get_weather,

    "web_search": web_search
}


# =========================
# 3. Tool Schema
# =========================


tools = [
    {
        "type": "function",

        "function": {
            "name": "calculator",

            "description":
                "计算两个数字的加法",

            "parameters": {
                "type": "object",

                "properties": {
                    "a": {
                        "type": "number",
                        "description": "第一个数字"
                    },

                    "b": {
                        "type": "number",
                        "description": "第二个数字"
                    }
                },

                "required": [
                    "a",
                    "b"
                ]
            }
        }
    },


    {
        "type": "function",

        "function": {
            "name": "get_current_time",

            "description":
                "获取当前的日期和时间",

            "parameters": {
                "type": "object",

                "properties": {},

                "required": []
            }
        }
    },


    {
        "type": "function",

        "function": {
            "name": "get_weather",

            "description": (
                "查询指定城市当前的实时天气。"
                "当用户询问某个城市现在的天气、"
                "温度、降水或风速时使用这个工具。"
            ),

            "parameters": {
                "type": "object",

                "properties": {
                    "city": {
                        "type": "string",

                        "description": (
                            "需要查询天气的城市名称，"
                            "例如北京、上海、东京"
                        )
                    }
                },

                "required": [
                    "city"
                ]
            }
        }
    },


    {
        "type": "function",

        "function": {
            "name": "web_search",

            "description": (
                "搜索互联网获取最新或外部信息。"
                "当用户询问新闻、最新事件、"
                "实时发展或明确要求联网搜索时，"
                "使用此工具。"
            ),

            "parameters": {
                "type": "object",

                "properties": {
                    "query": {
                        "type": "string",

                        "description": (
                            "要搜索的关键词或问题。"
                        )
                    }
                },

                "required": [
                    "query"
                ]
            }
        }
    }
]