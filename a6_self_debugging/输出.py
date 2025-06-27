import os
import re
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from model import get_db_model
from model import query_openai
import os
import sys


# 初始化
def generate_sql_model120(sql, model_name):
    try:
        # 生成SQL提示
        prompt_t =f"""
        您是一位Text-to-SQL专家，擅长对SQL语句进行格式检查。请根据格式检查SQL语句。若出现格式错误请修改
        生成的SQL：{sql}；
        请按照以下格式输出：sql""
        请保证sql""中没有换行
        例如：sql"select * from user;"
        """
        response = query_openai(model_name, prompt_t)
        sql_query = re.findall(r'sql"(.*?)"', response, re.DOTALL)
        if sql_query:
            response = sql_query[0].strip()
            print("输出response", response)
        else:
            response = ""  # 如果没有匹配到，返回空字符串
        zhipu_AI_out = response if response is not None else ""
        return zhipu_AI_out

    except Exception as e:
        print(f"Error during SQL generation: {e}")
        return None

# models, debug_count = get_db_model(1)
# model_name=models[0][0]
# sql="SELECT * FROM material_appropriation WHERE type = '领用';"
# sql_query= generate_sql_model120(sql,model_name)
