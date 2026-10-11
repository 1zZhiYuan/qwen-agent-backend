# =========================
# web_search.py
# 联网搜索工具
# =========================


# 【移动6】
import os


# 【移动7】
from dashscope import Generation


# 【移动8】
from dotenv import load_dotenv


# 【新增7】
# config.py 在 tools 文件夹的上一层，
# 仍然可以直接这样导入
from config import SEARCH_MODEL


# 【移动9】
load_dotenv()


# 【移动10】
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


        for index, item in enumerate(
            search_results[:5],
            start=1
        ):

            result = {

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