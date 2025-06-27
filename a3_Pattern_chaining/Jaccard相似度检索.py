import weaviate
from fuzzywuzzy import fuzz  # 用于 Levenshtein 距离计算

# 定义函数来执行查询并返回相似条目
def search_similar_jaccard(query, threshold,client):
    # 初始化 Weaviate 客户端
    exclude_classes = ["Oilfield_Knowledge_Base_all", "Sample_library"]
    # 获取所有类的信息
    schema = client.schema.get()
    all_classes = [cls["class"] for cls in schema["classes"]]

    # 存储相似的条目，使用 set 来确保唯一性
    similar_entries = set()

    # 定义计算 Jaccard 相似度的函数
    def jaccard_similarity(str1, str2):
        # 将字符串转为集合（这里以字符集合为例）
        set1 = set(str1)
        set2 = set(str2)
        # 计算交集和并集
        intersection = set1.intersection(set2)
        union = set1.union(set2)

        # 返回 Jaccard 相似度
        return len(intersection) / len(union) if len(union) != 0 else 0

    # 遍历所有类
    for class_name in all_classes:
        # 排除指定类
        if class_name in exclude_classes:
            continue

        # 获取该类的字段信息
        class_properties = next(cls["properties"] for cls in schema["classes"] if cls["class"] == class_name)

        # 只提取字段名
        properties = [field["name"] for field in class_properties]

        # 计算类名与查询的Jaccard相似度
        class_name_similarity = jaccard_similarity(query, class_name)
        if class_name_similarity >= threshold:
            # 使用 tuple 来确保条目的唯一性
            similar_entries.add((
                class_name,
                class_name,  # 类名
                "class_name",  # 这里是类名
                class_name_similarity,
                "class_name"
            ))

        # 查询该类的数据
        results = client.query.get(class_name, properties).with_limit(100).do()

        # 检查查询结果
        if "data" in results and "Get" in results["data"]:
            data = results["data"]["Get"].get(class_name, [])

            # 遍历查询结果的每一条记录
            for entry in data:
                # 首先对字段名进行相似度计算
                for field in properties:
                    # 计算字段名与查询的Jaccard相似度
                    field_similarity = jaccard_similarity(query, field)

                    # 如果字段名的相似度超过阈值，保存该条目
                    if field_similarity >= threshold:
                        similar_entries.add((
                            class_name,
                            field,  # 这里是属性名
                            field,  # 属性名
                            field_similarity
                        ))

                    # 获取该字段的值
                    field_value = entry.get(field, "")

                    # 强制转换为字符串类型，避免非字符串字段的错误
                    field_value = str(field_value)

                    if field_value:  # 只有当字段值非空时才计算相似度
                        # 计算字段值与查询的Jaccard相似度
                        jac_similarity = jaccard_similarity(query, field_value)

                        # 如果相似度高于阈值，保存该条目
                        if jac_similarity >= threshold:
                            similar_entries.add((
                                class_name,
                                field_value,  # 这里是字段值
                                field,  # 属性名
                                jac_similarity
                            ))

    return similar_entries


# if __name__ == "__main__":
#     a=search_similar_entries("age")
#     print(a)