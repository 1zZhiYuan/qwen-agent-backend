# =========================
# tools/__init__.py
# 统一管理和导出所有 Tool
# =========================


# 【新增8】
from .calculator import calculator


# 【新增9】
from .time_tool import get_current_time


# 【新增10】
from .weather import get_weather


# 【新增11】
from .web_search import web_search


# =========================
# 1. Tool Registry
# =========================


# 【移动11】
tool_functions = {
    "calculator": calculator,

    "get_current_time": get_current_time,

    "get_weather": get_weather,

    "web_search": web_search
}


# =========================
# 2. Tool Schema
# =========================


# 【移动12】
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