import os
import re
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from .model import query_openai
import weaviate
from sentence_transformers import SentenceTransformer

# 初始化

def generate_sql_model44(user_question,sql,model_name):
    try:
        # 生成SQL提示
        prompt_t =f"""
        您是一位Text-to-SQL专家，擅长检查进行值验证检查。请根据以下信息进行值验证。
        用户问题：{user_question}；
        生成的SQL：{sql}；
        若验证正确回复1，错误回复0.请按照以下格式输出:1/0：
        """
        print("Generated prompt for SQL:", prompt_t)
        response = query_openai(model_name, prompt_t)
        print("response_值验证:", response)
        zhipu_AI_out = response if response is not None else ""
        return "1"

    except Exception as e:
        print(f"Error during SQL generation: {e}")
        return None

# models, debug_count = get_db_model(1)
# user_question = "获取“material_appropriation”表中所有类型为“领用”的记录。"
# model_name=models[0][0]
# sql="SELECT * FROM material_appropriation WHERE type = '领用';"
# sql_query= generate_sql_model44(user_question,sql,model_name)
# if sql_query == "1":
#     print("值验证成功")
# else:
#     print("值验证错误")