from datetime import datetime
import hashlib
import jieba
import weaviate
import json
import os
from zhipuai import ZhipuAI
from .baidu_request_finally import get_content_using_xpath, output_results
from .weiji_request_finally import get_page_info
from .zhipu_model import get_response_from_model
from googletrans import Translator


def get_hash(word):
    """
    计算给定词语的哈希值
    :param word: 词语
    :return: 计算出的哈希值
    """
    return hashlib.sha256(word.encode('utf-8')).hexdigest()


def extract_terms(zhipu_AI_out):
    """
    从智普AI输出中提取油田术语。
    :param zhipu_AI_out: 智普AI的原始输出
    :return: 提取的油田术语列表
    """
    start = zhipu_AI_out.find('[') + 1
    end = zhipu_AI_out.find(']')
    array_str = zhipu_AI_out[start:end]
    word_list = [item.strip() for item in array_str.split(',')]
    return word_list


def query_word_info(word, client):
    """
    根据哈希值查询油田知识库中的信息。
    :param word: 查询的词语
    :param client: Weaviate客户端
    :return: 查询结果
    """
    word_hash = get_hash(word)
    response = (
        client.query
        .get("Oilfield_Knowledge_Base_all", ['name', 'english_name', 'explain', 'annotation'])
        .with_where({
            "path": ["hash"],  # 查询哈希字段
            "operator": "Equal",  # 精确匹配
            "valueString": word_hash  # 精确匹配的哈希值
        })
        .with_limit(2)  # 返回个数（TopK），这里选择返回2个
        .do()
    )
    return response


def translate_word(word, dest_lang='en'):
    """
    使用 Google Translate API 翻译词语。
    :param word: 要翻译的词语
    :param dest_lang: 目标语言，默认为英文 ('en')
    :return: 翻译后的结果，失败时返回 None
    """
    translator = Translator()
    try:
        translated = translator.translate(word, dest=dest_lang)
        if translated.text:  # 检查是否有有效的翻译结果
            return translated.text
        else:
            return f"Translation not available for {word}"  # 返回默认信息
    except Exception as e:
        print(f"Error during translation: {e}")
        return f"Translation failed for {word}"  # 返回失败信息


def output_results(word):
    """
    输出翻译的英文名称，若翻译失败，则返回相应的错误信息。
    :param word: 要查询的词语
    :return: 翻译后的英文名称
    """
    translated_word = translate_word(word)
    if translated_word and translated_word != f"Translation failed for {word}":
        return translated_word
    else:
        return "No English translation available"  # 如果翻译失败，返回默认值

def get_max_object_id(client, class_name):
    result = client.query.get(class_name, ["object_id"]).with_additional(["id"]).do()
    # 获取所有的object_id并提取最大值
    object_ids = [item['object_id'] for item in result['data']['Get'][class_name]]
    if object_ids:
        return max(object_ids)  # 返回最大值
    else:
        return 0  # 如果没有数据，返回 0

def get_additional_info(word,client):
    """
    获取词语的额外信息，包括概念和效果。
    :param word: 查询的词语
    :return: 相关信息（字典格式）
    """
    # baidu
    content, concept, effect = get_content_using_xpath(word)
    english_name = output_results(word)
    result_entry = {}

    if content != "":
        result_entry = {
            "name": word,  # 关键词作为名称
            "english_name": english_name,  # 英文翻译
            "explain": concept,  # 结合概念和内容
            "annotation": effect  # 作用或解释
        }
        # 存baidu
        current_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        max_object_id = get_max_object_id(client, 'Oilfield_Knowledge_Base_all')
        new_object_id = max_object_id + 1
        new_data = {
            "object_id": new_object_id,
            "name": word,  # 关键词作为名称
            "english_name": english_name,  # 英文翻译
            "explain": concept,  # 结合概念和内容
            "annotation": effect,  # 作用或解释
            "created_at": current_time
        }
        client.data_object.create(
            data_object=new_data,
            class_name='Oilfield_Knowledge_Base_all'
        )

    else:
        page_info = get_page_info(word)
        if page_info['Brief Introduction'] == "No content found":
            # 存weiji
            current_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
            max_object_id = get_max_object_id(client, 'Oilfield_Knowledge_Base_all')
            new_object_id = max_object_id + 1
            new_data = {
                "object_id": new_object_id,
                "name": word,  # 关键词作为名称
                "english_name": english_name,  # 英文翻译
                "explain": concept,  # 结合概念和内容
                "annotation": effect,  # 作用或解释
                "created_at": current_time
            }
            client.data_object.create(
                data_object=new_data,
                class_name='Oilfield_Knowledge_Base_all'
            )
            result_entry = {
                "name": word,  # 关键词作为名称
                "english_name": page_info['english_name'],  # 英文翻译
                "explain": page_info['Brief Introduction']
            }
        else:
            result_entry = {
                "name": word,
                "english_name": "",
                "explain": ""
            }
    return result_entry


# 主函数
def main(user_question, client, api_key="f7a0186af1f5730d592e6bb15b7e9961.3i3qcCyOf2VeWUVs"):
    # 使用jieba分词
    with open("D:/my_langchain/myProject1/000attempt/a1_Knowledge_base/docement/mydict.txt", "r",
              encoding="utf-8") as f:
        jieba.load_userdict(f)

    words = jieba.cut(user_question)
    cutresult = list(words)
    print("分词结果：", cutresult)

    # 根据不同问题生成不同的提示词
    prompt_t = f"""
        假设您是油田领域的专家，请帮我从分词后的内容中油田领域相关的术语。
        下面是分词后的内容：{cutresult}
        请以数组形式输出分词后产生的油田术语，只保留油田领域的术语。
        只能输出石油领域的术语。
        按照:extracted_terms=[,,,]的形式输出
        """

    # 获取智普AI响应
    zhipu_AI_out = get_response_from_model(prompt_t, api_key)
    print("zhipu_AI_out：", zhipu_AI_out)

    # 提取术语
    word_list = extract_terms(zhipu_AI_out)
    if '' in word_list:
        return ''
    all_results = []
    for word in word_list:
        print(f"查询词: {word}")
        # 查询知识库
        response = query_word_info(word, client)

        result_entry = {"query_word": word, "results": []}

        if response['data']['Get']["Oilfield_Knowledge_Base_all"]:
            for item in response['data']['Get']["Oilfield_Knowledge_Base_all"]:
                result_entry["results"].append({
                    "name": item.get('name', ''),
                    "english_name": item.get('english_name', ''),
                    "explain": item.get('explain', ''),
                    "annotation": item.get('annotation', '')
                })
        else:
            # 获取额外信息
            additional_info = get_additional_info(word,client)
            result_entry["results"].append(additional_info)

            # 检查是否有有效结果
            if any(result.get("explain", "") != "" and result.get("annotation", "") != "" for result in
                   result_entry["results"]):
                all_results.append(result_entry)

    return all_results


# 用户问题
# client = weaviate.Client("http://localhost:8080")
# user_question = "查询油田Z在2023年第一季度的每个月的平均日产油量，按月份排序。"
# main(user_question, client, api_key="f7a0186af1f5730d592e6bb15b7e9961.3i3qcCyOf2VeWUVs")
