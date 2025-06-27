import os
import re
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from .model import query_openai
import os
import sys
import weaviate
from sentence_transformers import SentenceTransformer

# 初始化

def generate_sql_model77(Professional_vocabulary,similar_records,class_names,user_question_type,user_question,sql,model_name):
    try:

        # 生成SQL提示
        prompt_t =f"""
        您是一位Text-to-SQL专家，擅长检查生成的SQL语句。请根据以下信息检查生成的SQL语句。
        相关术语：{Professional_vocabulary}；
        用户问题：{user_question}；
        生成的SQL：{sql}；
        用户问题查询类型：{user_question_type}；
        数据库结构：{class_names}；
        相似示例：{similar_records}；
        请按照以下格式输出：sql""
        请保证sql""中没有换行
        例如：sql"select * from user;"
        """

        response = query_openai(model_name, prompt_t)
        sql_query = re.findall(r'sql"(.*?)"', response, re.DOTALL)
        if sql_query:
            response = sql_query[0].strip()
            print("自检查response", response)
        else:
            response = ""  # 如果没有匹配到，返回空字符串
        zhipu_AI_out = response if response is not None else ""
        return zhipu_AI_out

    except Exception as e:
        print(f"Error during SQL generation: {e}")
        return None

# models, debug_count = get_db_model(1)
# model = SentenceTransformer('D:/my_langchain/myProject1/text2vec-base-chinese')
# client = weaviate.Client("http://localhost:8080")
# user_question = "获取“material_appropriation”表中所有类型为“领用”的记录。"
# model_name=models[0][0]
# sql="SELECT * FROM material_appropriation WHERE type = '领用';"
# sql_query= generate_sql_model77(user_question,sql,model,client,model_name)
# if(sql==sql_query):
#     print("正确")
# else:
#     print("错误")