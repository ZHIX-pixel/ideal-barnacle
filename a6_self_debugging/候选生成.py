
from .model import query_openai
def generate_sql_model22(Professional_vocabulary, user_question, user_question_type, class_names, similar_records,model_name):
    prompt_t = f"""
        假设您是油田领域的text-to-sql专家，请帮我根据以下信息生成五个用户问题对应的SQL。
        用户问题：{user_question}；
        相关术语：{Professional_vocabulary}；
        用户问题查询类型：{user_question_type}；
        数据库结构：{class_names}；
        相似示例：{similar_records}；
        请把生成结果用双层数组的形式输出，请输出每个用户问题对应的SQL
        例如：用户问题：获取“material_appropriation”表中所有类型为“领用”的记录。
             输出结果：
                sql_statements =[
                    [
                        "获取 `material_appropriation` 表中所有类型为‘领用’的记录。",
                        "SELECT * FROM material_appropriation WHERE type = '领用';"
                    ],
                    [
                        "从 `material_appropriation` 表中筛选出所有类型为‘领用’的记录。",
                        "SELECT * FROM material_appropriation WHERE type = '领用';"
                    ],
                    [
                        "请查询 `material_appropriation` 表中所有类型为‘领用’的条目。",
                        "SELECT * FROM material_appropriation WHERE type = '领用';"
                    ],
                    [
                        "能否列出 `material_appropriation` 表中所有类型为‘领用’的记录？",
                        "SELECT * FROM material_appropriation WHERE type = '领用';"
                    ],
                    [
                        "请提供 `material_appropriation` 表中所有类型为‘领用’的记录。",
                        "SELECT * FROM material_appropriation WHERE type = '领用';"
                    ]
                ]
    """
    # 获取SQL响应
    Candidate_result = query_openai(model_name, prompt_t)
    return Candidate_result


# models, debug_count = get_db_model(1)
# model_name=models[0][0]
# user_question = "获取“material_appropriation”表中所有类型为“领用”的记录。"
# user_question_type="简单查询"
# Professional_vocabulary=""
# class_names=""
# similar_records=""
# Candidate_result=generate_sql_model22(Professional_vocabulary, user_question, user_question_type, class_names, similar_records,model_name)
# print(Candidate_result)