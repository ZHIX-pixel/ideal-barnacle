import weaviate
from fuzzywuzzy import fuzz

# 定义一个函数来搜索相似条目
def search_similar_Levenshtein(query, threshold,client):
    # 初始化 Weaviate 客户端
    exclude_classes = ["Oilfield_Knowledge_Base_all", "Sample_library"]
    # 获取所有类的信息
    schema = client.schema.get()
    all_classes = [cls["class"] for cls in schema["classes"]]

    # 存储相似的条目
    similar_entries = []

    # 遍历所有类
    for class_name in all_classes:
        # 跳过不需要检索的类
        if class_name in exclude_classes:
            continue

        # 计算类名与查询的 Levenshtein 相似度
        class_name_similarity = fuzz.ratio(query, class_name) / 100.0
        if class_name_similarity >= threshold:
            similar_entries.append({
                "class_name": class_name,
                "field": "class_name",  # 类名
                "entry": class_name,
                "levenshtein_similarity": class_name_similarity
            })

        # 获取该类的字段信息
        class_properties = next(cls["properties"] for cls in schema["classes"] if cls["class"] == class_name)

        # 只提取字段名
        properties = [field["name"] for field in class_properties]

        # 遍历字段名，计算字段名与查询的相似度
        for field in properties:
            field_name_similarity = fuzz.ratio(query, field) / 100.0
            if field_name_similarity >= threshold:
                similar_entries.append({
                    "class_name": class_name,
                    "field": field,
                    "entry": field,
                    "levenshtein_similarity": field_name_similarity
                })

        # 查询该类的数据
        results = client.query.get(class_name, properties).with_limit(100).do()

        # 检查查询结果
        if "data" in results and "Get" in results["data"]:
            data = results["data"]["Get"].get(class_name, [])

            # 遍历查询结果的每一条记录
            for entry in data:
                for field in properties:
                    field_value = entry.get(field, "")

                    # 强制转换为字符串类型，避免非字符串字段的错误
                    field_value = str(field_value)

                    if field_value:  # 只有当字段值非空时才计算相似度
                        # 计算 Levenshtein 距离相似度
                        lev_similarity = fuzz.ratio(query, field_value) / 100.0  # 转换为 0 到 1 之间的值

                        # 如果相似度高于阈值，保存该条目
                        if lev_similarity >= threshold:
                            similar_entries.append({
                                "class_name": class_name,
                                "field": field,
                                "entry": field_value,
                                "levenshtein_similarity": lev_similarity
                            })

    return similar_entries





# 如果此脚本是直接运行的，调用 main 函数
# if __name__ == "__main__":
#     similar_entries = search_similar_entries("age", 0.6)
#     print(similar_entries)
