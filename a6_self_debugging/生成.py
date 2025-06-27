import os
import re
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from .model import query_openai, get_db_model
import os
import sys
import weaviate
from sentence_transformers import SentenceTransformer


# 添加模块路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 初始化

def generate_sql_model66(Professional_vocabulary,similar_records,class_names,user_question_type,tisi, user_question, model_name):
    try:
        # 生成SQL提示
        prompt_t =tisi+ f"""
        油田相关术语：{Professional_vocabulary}；
        用户问题：{user_question}；
        用户问题类型：{user_question_type}；
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
            print("自生成response", response)
        else:
            response = ""  # 如果没有匹配到，返回空字符串
        return response
    except Exception as e:
        print(f"Error during SQL generation: {e}")
        return None

# models, debug_count = get_db_model(1)
# model = SentenceTransformer('D:/my_langchain/myProject1/text2vec-base-chinese')
# client = weaviate.Client("http://localhost:8080")
# user_question = "获取“material_appropriation”表中所有类型为“领用”的记录。"
# print(models)
# model_name=models[0][0]
# print(model_name)
# tisi="您是一位Text-to-SQL专家，擅长将自然语言问题转换为SQL查询语句。请根据以下信息生成SQL语句，确保语句准确、高效，并符合SQL语法规范。"
# a= generate_sql_model66(tisi,user_question,model,client,model_name)
