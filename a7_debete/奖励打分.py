import concurrent
import os
import re
import sys
from .model import query_openai
from .reward import reward_function


def generate_sql_modification_prompt(a, sql_query, user_question, Professional_vocabulary, user_question_type,
                                     class_names, similar_records, model_feedback):
    """通用函数：生成修改SQL的提示"""
    return f"""
    假设您是油田领域的text-to-sql专家，请根据其他模型的意见修改SQL。
    SQL：{sql_query}；
    用户问题：{user_question}；
    相关术语：{Professional_vocabulary}；
    用户问题查询类型：{user_question_type}；
    数据库结构：{class_names}；
    相似示例：{similar_records}；
    其他模型的意见：{model_feedback}
    奖励函数：{a}
    请把您的修改后的SQL按照以下格式输出：sql=""
    请保证sql""中没有换行
    例如：sql"select * from user;"
    """

def process_sql_generation1(user_question, sql_query, Professional_vocabulary, user_question_type,
                           class_names, similar_records, max_iterations,model1,model2):
    """
    处理SQL生成的整个过程，包括两模型交替反馈和修改生成SQL，直到SQL一致或达到最大循环次数。

    Parameters:
    - user_question: 用户的自然语言问题
    - sql_query: 初始生成的SQL查询
    - Professional_vocabulary: 专业词汇
    - user_question_type: 用户问题的查询类型
    - class_names: 数据库表名
    - similar_records: 相似记录
    - max_iterations: 最大迭代次数

    Returns:
    - 最终生成的SQL查询
    """
    iteration = 1
    sql_query1=""
    sql_query2=""
    while iteration < max_iterations:
        # 创建并发送请求到模型一（zhipu）和模型二（deepseek）并行
        prompt_t1 = f"""
            假设您是油田领域的text-to-sql专家，请帮我根据以下信息检查一下其他模型生成的SQL。
            SQL：{sql_query}；
            用户问题：{user_question}；
            相关术语：{Professional_vocabulary}；
            用户问题查询类型：{user_question_type}；
            数据库结构：{class_names}；
            相似示例：{similar_records}；
            请把您的意见按照以下格式输出：意见=""
        """

        # 同步获取两个模型的反馈
        zhipu_feedback = query_openai(model1, prompt_t1)
        deepseek_feedback = query_openai(model2, prompt_t1)

        print(f"第{iteration}轮 - 模型一的意见")
        print(zhipu_feedback)
        print("---------------------------")

        print(f"第{iteration}轮 - 模型二的意见")
        print(deepseek_feedback)
        print("---------------------------")

        # 计算奖励并进行并行
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_a = executor.submit(reward_function, sql_query, user_question, zhipu_feedback, deepseek_feedback)
            a = future_a.result()
        print("奖励函数如下")
        print(a)

        # 生成并请求模型一根据模型二的反馈修改SQL
        prompt_t2_zhipu = generate_sql_modification_prompt(a, sql_query, user_question, Professional_vocabulary,
                                                           user_question_type, class_names, similar_records,
                                                           zhipu_feedback)
        zhipu_modified_sql = query_openai(model1, prompt_t2_zhipu)
        sql_query1 = zhipu_modified_sql.split('=', 1)[1].strip('\"')
        print(f"第{iteration + 1}轮 - 模型一根据模型二的意见修改后的结果")
        print(sql_query1)
        print("---------------------------")

        # 计算奖励
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_b = executor.submit(reward_function, sql_query, user_question, zhipu_feedback, deepseek_feedback)
            b = future_b.result()
        print("奖励函数如下")
        print(b)

        # 生成并请求模型二根据模型一的反馈修改SQL
        prompt_t2_deepseek = generate_sql_modification_prompt(a, sql_query, user_question, Professional_vocabulary,
                                                              user_question_type, class_names, similar_records,
                                                              deepseek_feedback)
        deepseek_modified_sql = query_openai(model2, prompt_t2_deepseek)
        sql_query2 = deepseek_modified_sql.split('=', 1)[1].strip('\"')
        print(f"第{iteration + 1}轮 - 模型二根据模型一的意见修改后的结果")
        print(sql_query2)
        print("---------------------------")

        # 检查是否达成一致
        if sql_query1 == sql_query2:
            print("模型生成的SQL一致，终止循环。")
            return sql_query1
        sql_query = sql_query1

        iteration += 1
    else:
        print("达到最大循环次数，终止循环。")
        print("执行打分机制")
        try:
            # 生成SQL提示
            prompt_t = f"""
            您是一位Text-to-SQL专家，擅长对SQL语句进行打分。请根据为下面两个SQL语句根据用户问题打分，最后输出分数最高的SQL
            用户问题：{user_question}；
            相关术语：{Professional_vocabulary}；
            用户问题查询类型：{user_question_type}；
            数据库结构：{class_names}；
            相似示例：{similar_records}；
            SQL1：{sql_query1}；
            SQL2：{sql_query2}；
            请按照以下格式输出：sql""
            请保证sql""中没有换行
            例如：sql"select * from user;"
            """
            print("Generated prompt for SQL:", prompt_t)
            response = query_openai("deepseek-r1-distill-qwen-32b", prompt_t)
            sql_query = re.findall(r'sql"(.*?)"', response, re.DOTALL)
            if sql_query:
                response = sql_query[0].strip()
            else:
                response = ""  # 如果没有匹配到，返回空字符串
            return response
        except Exception as e:
            return "打分机制出错了"


# user_question = "找出“material_appropriation”表中所有申请人是王强的记录"
# sql_query = "SELECT * FROM material_appropriation WHERE fdsf = '王强'"
# Professional_vocabulary = ""
# user_question_type = "简单查询"
# class_names = "material_appropriation"
# similar_records = ""
# max_iterations = 4
#
# models, debug_count = get_db_model(1)
# model_name1=models[0][0]
# model_name2=models[1][0]
# model_name1=model_name1.lower()
# model_name2=model_name2.lower()
# final_sql=process_sql_generation(user_question, sql_query, Professional_vocabulary, user_question_type,
#                            class_names, similar_records, max_iterations,model_name1,model_name2)
# print("最终生成的SQL:")
# print(final_sql)