import re

import pymysql
from .model import query_openai
def generate_sql_model99(sql_query, user_question, model_name):
        try:
            # 构造提示
            prompt = (f"请评估以下 SQL 查询和用户问题之间的语义骨架相似度，并给出一个评分（0到1，1表示完全相同，0表示完全不相关）。\n\nSQL 查询：{sql_query}\n用户问题：{user_question}\n\n相似度评分："
                      f"例如:相似度评分：0.95")
            # 调用 OpenAI 的 GPT 模型
            response = query_openai(model_name, prompt)
            try:
                match = re.search(r"相似度评分：(\d+(\.\d+)?)", response)
                similarity_score = match.group(1)
            except Exception as e:
                return f"评估语义骨架相似度时发生错误：{e}"
            # 提取评分
            return similarity_score

        except Exception as e:
            return f"评估语义骨架相似度时发生错误：{e}"


# models, debug_count = get_db_model(1)
# model_name=models[0][0]
# print(generate_sql_model99("SELECT * FROM material_appropriation WHERE type = '领用';","获取“material_appropriation”表中所有类型为“领用”的记录。",model_name))