
from .model import query_openai
import os
import re
import sys

import pymysql
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

connection = pymysql.connect(
    host='localhost', user='root', password='123456', database='lhr', charset='utf8mb4'
)
cursor = connection.cursor()

def compute_bert_similarity(text1, text2):
    # 加载预训练的 BERT 模型
    model = SentenceTransformer('D:/my_langchain/myProject1/text2vec-base-chinese')
    # 获取句子的向量表示
    embeddings = model.encode([text1, text2])
    # 计算Cosine相似度
    similarity = cosine_similarity([embeddings[0]], [embeddings[1]])
    return similarity[0][0]

def user_question_similarity(text1, sql):
    prompt_t1 = f"""
        假设您是油田领域的text-to-sql专家，请帮我检查一下用户问题和SQL是否语义相同。
        SQL：{sql}；
        用户问题：{text1}；
        若语义相同，请输出：判断=语义相同
        若语义不相同，请输出：判断=语义不相同
        """
    response = query_openai("deepseek-r1-distill-qwen-32b", prompt_t1)
    if "语义相同" in response:
        a="语义相同"
        return a
    else:
        a="语义不相同"
        return a

# 奖励函数
# 定义奖励函数
def reward_function(sql_query,user_question, opinion_model_1, opinion_model_2):
    rewards = {
        "语义一致性奖励(语义相同为1，语义不相同为0)": 0,
        "比较模型之间的反馈(反馈相同为1，反馈不相同为0)": 0,
        "执行正确性奖励(执行正确为1，执行不正确为0)": 0,
        "结构合理性奖励(包含SELECT关键字加0.2，包含WHERE条件加0.3，结尾包含分号加0.5)": 0,
        "执行效率奖励": 0
    }

    # 语义一致性奖励：简单地比较生成的SQL与用户问题的匹配程度,模型校验
    q=user_question_similarity(user_question,sql_query)

    if "语义相同" in q:
        rewards["语义一致性奖励(语义相同为1，语义不相同为0)"] = 1
    else:
        rewards["语义一致性奖励(语义相同为1，语义不相同为0)"] = 0

    # 反馈一致性奖励：比较当前生成SQL与其他模型的反馈一致性 比较意见可以用余玹相似度
    similarity_score = compute_bert_similarity(opinion_model_1, opinion_model_2)
    if similarity_score > 0.7:
        rewards["比较模型之间的反馈(反馈相同为1，反馈不相同为0)"] = 1  # 如果SQL查询符合批评反馈，奖励1分

    # 执行正确性奖励：通过实际执行SQL查询检查执行结果
    try:
        cursor.execute(sql_query)
        rewards["执行正确性奖励(执行正确为1，执行不正确为0)"] = 1  # 如果执行成功，增加奖励
    except pymysql.MySQLError as e:
        rewards["执行正确性奖励(执行正确为1，执行不正确为0)"] = "0"+str(e)  # 执行失败，不增加奖励

    # 结构合理性奖励：检查SQL的结构是否符合标准
    # 1. 包含SELECT关键字
    if "SELECT" in sql_query:
        rewards["结构合理性奖励(包含SELECT关键字加0.2，包含WHERE条件加0.3，结尾包含分号加0.5)"] += 0.2
    # 2. 包含WHERE条件
    if "WHERE" in sql_query:
        rewards["结构合理性奖励(包含SELECT关键字加0.2，包含WHERE条件加0.3，结尾包含分号加0.5)"] += 0.3
    # 3. 结尾包含分号
    if sql_query.strip().endswith(";"):
        rewards["结构合理性奖励(包含SELECT关键字加0.2，包含WHERE条件加0.3，结尾包含分号加0.5)"] += 0.5

    # 执行效率奖励：如果SQL包含过多的嵌套或JOIN，罚分
    rewardsexecution_efficiency = 0
    # 1. 检查嵌套深度
    nested_queries = re.findall(r"\(SELECT", sql_query, re.IGNORECASE)
    nested_depth = len(nested_queries)
    if nested_depth > 2:  # 如果有超过2层嵌套查询，认为效率较低
        rewardsexecution_efficiency -= 0.1
    elif nested_depth == 0:
        rewardsexecution_efficiency += 0.2  # 如果没有嵌套查询，效率较高
    # 2. 检查涉及的表数量
    table_count = len(re.findall(r"FROM\s+(\S+)", sql_query, re.IGNORECASE))
    if table_count > 3:  # 超过3个表，查询复杂度较高，可能影响效率
        rewardsexecution_efficiency -= 0.1
    else:
        rewardsexecution_efficiency += 0.2  # 表的数量较少，认为查询效率较高
    # 3. 检查是否使用了聚合函数
    aggregate_functions = re.findall(r"\b(COUNT|SUM|AVG|MAX|MIN|GROUP BY|DISTINCT)\b", sql_query, re.IGNORECASE)
    if aggregate_functions:
        rewardsexecution_efficiency -= 0.4  # 如果使用了聚合函数，认为效率较低，扣分
    rewards["执行效率奖励"] = rewardsexecution_efficiency

    return rewards
