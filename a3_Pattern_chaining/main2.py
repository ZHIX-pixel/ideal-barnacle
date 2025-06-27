import concurrent.futures
import weaviate
from .Jaccard相似度检索 import search_similar_jaccard
from .Levenshtein相似度检索 import search_similar_Levenshtein
from .Keyword_extraction11 import KeywordSimilarityExtractor

def merge_results(result1, result2):
    """
    合并 Jaccard 和 Levenshtein 相似度检索结果，去重并选择较大的相似度
    """
    merged_results = {}

    # 处理 result1 (Jaccard 相似度)
    for item in result1:
        if len(item) == 4:
            class_name, field, entry, similarity = item
            key = (class_name, field, entry)
            item_dict = {
                "class_name": class_name,
                "field": field,
                "entry": entry,
                "similarity": similarity
            }
        else:
            print(f"Skipping malformed result1 entry: {item}")
            continue

        if key not in merged_results:
            merged_results[key] = item_dict
        else:
            merged_results[key]["similarity"] = max(merged_results[key]["similarity"], item_dict["similarity"])

    # 处理 result2 (Levenshtein 相似度)
    for item in result2:
        if isinstance(item, tuple) and len(item) == 4:
            class_name, field, entry, lev_similarity = item
            key = (class_name, field, entry)
            item_dict = {
                "class_name": class_name,
                "field": field,
                "entry": entry,
                "similarity": lev_similarity
            }
        elif isinstance(item, dict):
            class_name = item["class_name"]
            field = item["field"]
            entry = item["entry"]
            lev_similarity = item["levenshtein_similarity"]
            key = (class_name, field, entry)
            item_dict = {
                "class_name": class_name,
                "field": field,
                "entry": entry,
                "similarity": lev_similarity
            }
        else:
            print(f"Skipping malformed result2 entry: {item}")
            continue

        if key not in merged_results:
            merged_results[key] = item_dict
        else:
            merged_results[key]["similarity"] = max(merged_results[key]["similarity"], item_dict["similarity"])

    # 转换回列表格式
    final_result = []
    for key, data in merged_results.items():
        final_result.append(data)

    return final_result


def process_user_question(question, jaccard_threshold, levenshtein_threshold, client):
    """
    封装的函数，接收用户问题和两个阈值，返回唯一的 class_name 列表
    """
    # 初始化 KeywordSimilarityExtractor
    api_key = "f7a0186af1f5730d592e6bb15b7e9961.3i3qcCyOf2VeWUVs"
    extractor = KeywordSimilarityExtractor(api_key)

    # 获取相似词及其翻译
    result = extractor.get_similar_words_and_translation(question)
    print("Keyword Extraction Result:", result)

    final_jaccard_results = []
    final_levenshtein_results = []

    # 使用 ThreadPoolExecutor 来并行执行两个检索任务
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # 提交两个检索任务到线程池
        futures = []
        for item in result:
            futures.append((executor.submit(search_similar_jaccard, item, jaccard_threshold, client), 'jaccard'))
            futures.append((executor.submit(search_similar_Levenshtein, item, levenshtein_threshold, client), 'levenshtein'))

        # 等待并收集结果
        for future, method in futures:
            result_data = future.result()
            if method == 'jaccard':
                final_jaccard_results.extend(result_data)
            elif method == 'levenshtein':
                final_levenshtein_results.extend(result_data)

    # 合并 Jaccard 和 Levenshtein 的结果
    merged_results = merge_results(final_jaccard_results, final_levenshtein_results)
    # 提取所有 unique class_name
    class_names = list(set(entry['class_name'] for entry in merged_results))
    class_attributes = {}
    for class_name in class_names:
        attributes = get_class_properties(class_name, client)
        class_attributes["表名："+class_name.lower()] = attributes
    print("class_attributes",class_attributes)
    return class_attributes
def get_class_properties(class_name,client):
    schema = client.schema.get()
    for cls in schema["classes"]:
        if cls["class"] == "other_information":
            continue
        if cls["class"] == class_name:
            return ["列名："+prop["name"] for prop in cls["properties"]]
    return []

# 使用示例
# if __name__ == "__main__":
#     user_question = "获取“material_appropriation”表中所有类型为“领用”的记录。"
#     jaccard_threshold = 0.85  # 设置 Jaccard 阈值
#     levenshtein_threshold = 0.85  # 设置 Levenshtein 阈值
#     client = weaviate.Client("http://localhost:8080")
#     class_names = process_user_question(user_question, jaccard_threshold, levenshtein_threshold, client)
#
#     # 打印 class_name 列表
#     print("Unique Class Names:", class_names)
