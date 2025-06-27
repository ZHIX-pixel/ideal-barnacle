import os
import re
import sys

from .model import query_openai


# 初始化
def generate_sql_model100(sql, model_name):
    try:
        # 生成SQL提示
        prompt_t =f"""
        您是一位Text-to-SQL专家，擅长对SQL语句进行语法检查。请根据语法检查SQL语句。若出现语法错误请修改
        生成的SQL：{sql}；
        请按照以下格式输出：sql""
        """
        print("Generated prompt for SQL:", prompt_t)
        response = query_openai(model_name, prompt_t)
        try:
            sql_query = re.search(r'sql\n(.*?)\n', response, re.DOTALL)
            if sql_query:
                response = sql_query.group(1).strip()  # 提取匹配的内容并去除首尾空白字符
            else:
                response = ""  # 如果没有匹配到，返回空字符串
            print("response_语法检查:", response)
        except Exception as e:
            print(f"response_语法检查: {e}")
        zhipu_AI_out = response if response is not None else ""
        return zhipu_AI_out

    except Exception as e:
        print(f"Error during SQL generation: {e}")
        return None

# models, debug_count = get_db_model(1)
# model_name=models[0][0]
# sql="SELECT * FROM material_appropriation WHERE type = '领用';"
# sql_query= generate_sql_model100(sql,model_name)
