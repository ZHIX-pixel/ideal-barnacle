import requests
from lxml import etree
from googletrans import Translator
import opencc
# 创建翻译器对象
translator = Translator()

# 翻译英文单词
def translate_word(word, dest_lang='en'):
    translation = translator.translate(word, dest=dest_lang)
    return translation.text
# 获取网页内容的函数
def get_content_using_xpath(keyword):
    # 构建请求URL
    url = f"https://baike.baidu.com/item/{keyword}"

    # 发送请求并获取响应
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 如果响应码不为 200，会抛出异常
    except requests.RequestException as e:
        return f"Failed to retrieve content: {e}", None, None

    # 解析页面
    html = etree.HTML(response.text)
    # 使用给定的 XPath 提取内容
    content = html.xpath('/html/body/div[1]/div/div[2]/div[2]/div/div[1]/div/div[3]//text()')
    if content:
        # 将内容拼接为字符串
        joined_content = ''.join(content).strip()

        # 按照逗号分割字符串，提取概念和作用
        split_content = joined_content.split('，')

        concept = split_content[0] if len(split_content) > 0 else ''
        effect = split_content[1] if len(split_content) > 1 else ''

        # 返回概念、作用以及完整内容
        return joined_content.strip(), concept.strip(), effect.strip()
    else:
        # 如果没有内容，尝试第二个 XPath 查询
        content = html.xpath('/html/head/meta[4]//@content')
        if content:
            # 处理内容，取第一个逗号之前和逗号之间的部分
            split_content = content[0].split('。')
            concept = split_content[0] if len(split_content) > 0 else ''
            effect = split_content[1] if len(split_content) > 1 else ''
            return content[0].strip(), concept.strip(), effect.strip()
        else:
            return "", "", ""

def output_results(keyword):
    translated_word = translate_word(keyword)
    return translated_word

# if __name__ == "__main__":
#     keyword = "注水井"
#     content, concept, effect = get_content_using_xpath(keyword)
#     translated_word=output_results(keyword)
#     print("translated_word:", translated_word)
#     print("Concept:", concept)
#     print("Content:", content)
#     print("Effect:", effect)
