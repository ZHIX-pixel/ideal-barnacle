import requests
import re
from googletrans import Translator
import opencc

# 创建翻译器对象
translator = Translator()


# 翻译英文单词
def translate_word(word, dest_lang='en'):
    translation = translator.translate(word, dest=dest_lang)
    return translation.text
def get_wikipedia_page_content(page_title):
    """从维基百科获取指定页面的简介"""
    url = "https://zh.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "titles": page_title,
        "prop": "extracts",
        "exintro": True,  # 获取页面简介
        "explaintext": True,  # 以纯文本格式返回
    }

    try:
        response = requests.get(url, params=params, timeout=100)
        response.raise_for_status()  # 检查请求是否成功
        data = response.json()

        pages = data.get("query", {}).get("pages", {})
        if not pages:
            return "No pages found in response."

        page_id = next(iter(pages))
        page_content = pages[page_id].get("extract", "No content available")

        return page_content
    except requests.RequestException as e:
        return f"Failed to retrieve data: {e}"


def safe_search(pattern, text):
    """安全的正则表达式搜索，返回匹配的第一组内容"""
    match = re.search(pattern, text)
    return match.group(1) if match else ""


def get_page_info(page_title):
    """获取指定页面的英文名称和简要介绍"""
    text = get_wikipedia_page_content(page_title)
    if text.startswith("Failed"):
        return text

    patterns = {
        "english": r"英語：([a-zA-Z]+)",  # 提取英語后面的部分
        "brief_introduction": r"^(.*?。.*?。)",  # 获取从文本开头到第一个句号“。”的内容
    }
    translated_word = translate_word(page_title)
    brief_introduction = safe_search(patterns['brief_introduction'], text)

    return {
        "Title": page_title,
        "english_name": translated_word,
        "Brief Introduction": brief_introduction
    }


# 示例：获取“生产井”页面的信息
if __name__ == "__main__":
    page_title = "石油"

    page_info = get_page_info(page_title)
    print(page_info)
    # print(f"Title: {page_info['Title']}")
    # print(f"Brief Introduction: {page_info['Brief Introduction']}")
