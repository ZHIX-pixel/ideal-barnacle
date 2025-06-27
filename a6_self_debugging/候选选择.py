import os
import re
import sys

import weaviate

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import a3_Pattern_chaining.main2 as main2
from .model import query_openai
def generate_sql_model33(client,Candidate_result, user_question,model_name):
    class_names = main2.process_user_question(user_question, 0.8, 0.8, client)
    prompt_t = f"""
        假设您是油田领域的text-to-sql专家，请根据以下信息帮我从候选用户问题和sql选择一条最正确的sql。
        请一定要从候选用户问题和sql中选择一条。
        请一定要从候选用户问题和sql中选择一条。
        请一定要从候选用户问题和sql中选择一条。
        注意表和列都用英文
        候选用户问题和sql：{Candidate_result}；
        用户问题：{user_question}；
        数据库结构：{class_names}；
        请按照以下格式输出：sql""
        请保证sql""中没有换行
        例如：sql"select * from user;"
    """
    # 获取SQL响应
    response = query_openai(model_name, prompt_t)
    sql_query = re.findall(r'sql"(.*?)"', response, re.DOTALL)
    if sql_query:
        response = sql_query[0].strip()
        return response
    else:
        response = ""  # 如果没有匹配到，返回空字符串
        return "错误"

# models, debug_count = get_db_model(1)
# model_name=models[0][0]
# user_question = "获取“material_appropriation”表中所有类型为“领用”的记录。"
# Candidate_result="""```json
# [
#     [
#         "获取“material_appropriation”表中所有类型为“领用”的记录。",
#         "SELECT * FROM material_appropriation WHERE type = '领用';"
#     ],
#     [
#         "查找“material_appropriation”表中类型为“领用”的所有记录。",
#         "SELECT * FROM material_appropriation WHERE type = '领用';"
#     ],
#     [
#         "在“material_appropriation”表中查询所有类型为“领用”的条目。",
#         "SELECT * FROM material_appropriation WHERE type = '领用';"
#     ],
#     [
#         "列出“material_appropriation”表中所有类型为“领用”的记录信息。",
#         "SELECT * FROM material_appropriation WHERE type = '领用';"
#     ],
#     [
#         "请给出“material_appropriation”表中所有类型为“领用”的记录详情。",
#         "SELECT * FROM material_appropriation WHERE type = '领用';"
#     ]
# ]
# ```"""
# client = weaviate.Client("http://localhost:8080")
# sql_query= generate_sql_model33(client,Candidate_result,user_question,model_name)
# print(sql_query)