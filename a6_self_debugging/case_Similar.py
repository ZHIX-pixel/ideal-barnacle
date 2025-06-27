import os
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import weaviate
def search_similar_records(query, client, top_n,model):
    """
    根据查询问题返回最相似的记录，包括 user_problem 和 corresponding_sql。

    :param query: 要查询的文本问题
    :param client: Weaviate 客户端实例
    :param top_n: 返回的最相似记录数
    :return: 返回一个包含最相似记录的列表，每个记录包括名称、相似度和对应的SQL
    """
    # 将查询问题转化为向量
    query_vector = model.encode([query])[0].tolist()

    # 构建查询向量
    nearVector = {'vector': query_vector}

    # 执行相似度查询，获取需要的字段（包括 user_problem, corresponding_sql, vector）
    response = (
        client.query
        .get("Sample_library", ['user_problem', 'corresponding_sql', '_additional {vector}'])  # 获取 user_problem, corresponding_sql 和向量
        .with_near_vector(nearVector)  # 使用向量检索
        .with_additional(['distance', 'vector'])  # 返回距离和向量
        .do()
    )

    # 获取返回结果
    results = response['data']['Get']["Sample_library"]
    if not results:
        return []
    # 提取查询结果的向量、名称和 SQL
    vectors = [result['_additional']['vector'] for result in results]
    names = [result['user_problem'] for result in results]
    sqls = [result['corresponding_sql'] for result in results]

    # 计算余弦相似度
    cosine_similarities = cosine_similarity([query_vector], vectors)

    # 排序并倒序显示（最相似的在前），只取前 top_n 个
    sorted_indices = np.argsort(cosine_similarities[0])[::-1][:top_n]  # 只取前 top_n 个

    # 返回最相似的前 top_n 个记录
    similar_records = []
    for idx in sorted_indices:
        similar_records.append({
            'name': names[idx],
            'cosine_similarity': cosine_similarities[0][idx],
            'corresponding_sql': sqls[idx]
        })

    return similar_records
