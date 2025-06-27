import os
import re
import sys
import concurrent.futures
import weaviate
from sentence_transformers import SentenceTransformer
from zhipuai import ZhipuAI
from .case_Similar import search_similar_records
from .调用模型 import classify_user_question
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import a00_model.main as model1
import a00_model.main2 as model2
import a3_Pattern_chaining.main2 as main2
from .Professional_vocabulary_search import main  # 导入main函数
# 添加模块路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# 初始化
def validate_weaviate_response(response):
    """增强版Weaviate响应验证"""
    if not isinstance(response, dict):
        return False
    if 'errors' in response:
        print(f"Weaviate错误响应: {response['errors']}")
        return False
    return bool(
        response.get('data', {}).get('Get', {}).get('MaterialAppropriation')
    )

def generate_sql_payload_v3(user_question, class_names, similar_records, professional_vocab):
    """稳定版提示模板生成"""
    sections = [
        "请直接根据以下信息生成SQL查询：",
        f"\n【原始问题】\n{user_question}"
    ]

    # 动态构建专业术语部分
    if professional_vocab and isinstance(professional_vocab, list) and len(professional_vocab) > 0:
        sections.append(f"\n【相关术语】\n" + ", ".join(professional_vocab))

    # 数据库结构处理
    db_section = []
    if class_names:
        for table_info in class_names:
            if isinstance(table_info, str) and '表名：' in table_info:
                db_section.append(table_info)
    if db_section:
        sections.append(f"\n【数据库结构】\n" + "\n".join(db_section))
    else:
        sections.append("\n【数据库结构】\n无可用表结构信息")

    # 相似案例处理
    if similar_records and isinstance(similar_records, list):
        sections.append(f"\n【参考案例】\n" + "\n".join(f"- {ex}" for ex in similar_records[:2]))

    sections.append('\n输出要求：直接给出可执行SQL，使用以下格式：sql="..."')
    return "\n".join(sections)


def safe_search_similar_records(question, client, top_k, model):
    """安全查询相似记录"""
    try:
        response = client.query.get(
            "MaterialAppropriation", ["properties"]
        ).with_near_text({"concepts": [question]}).with_limit(top_k).do()

        if not validate_weaviate_response(response):
            print(f"无效的Weaviate响应结构: {response}")
            return []

        records = response['data']['Get']['MaterialAppropriation']
        return [str(r) for r in records] if records else []
    except Exception as e:
        print(f"相似记录查询失败: {str(e)}")
        return []

def parse_sql_response(raw_response):
    """增强版响应解析"""
    if not raw_response:
        return "未生成有效SQL"

    # 清理多余内容
    clean_response = re.sub(r'"resource_metrics": \[.*?\]', '', raw_response)

    # 尝试多种匹配模式
    patterns = [
        r'sql="(.*?)"(?!.*sql=)',  # 捕获最后一个sql=语句
        r'sql=\s*"(.*?)"',
        r'```sql\n(.*?)\n```'
    ]

    for pattern in patterns:
        matches = re.findall(pattern, clean_response, re.DOTALL)
        if matches:
            sql = matches[0].strip()
            # 基础验证
            if sql.lower().startswith("select") and "from" in sql.lower():
                return sql
    return "未生成有效SQL"


def generate_sql_model1(user_question, model, client):
    """
    生成SQL查询的方法。
    """
    result_template = {
        "sql": "",
        "metadata": {
            "classes_searched": [],
            "similar_records_found": 0,
            "professional_terms": 0,
            "error": None
        }
    }

    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # 并行任务处理
            futures = {
                executor.submit(main, user_question, client): "vocab",
                executor.submit(safe_search_similar_records, user_question, client, 2, model): "records",
                executor.submit(main2.process_user_question, user_question, 0.8, 0.8, client): "classes"
            }

            professional_vocab = []
            similar_records = []
            class_names = []

            # 统一处理任务结果
            for future in concurrent.futures.as_completed(futures):
                task_type = futures[future]
                try:
                    result = future.result()
                    if task_type == "vocab":
                        professional_vocab = result if isinstance(result, list) else []
                    elif task_type == "records":
                        similar_records = result if isinstance(result, list) else []
                    elif task_type == "classes":
                        class_names = result if isinstance(result, list) else []
                except Exception as e:
                    print(f"子任务 {task_type} 执行失败: {str(e)}")

            # 构建稳定提示
            prompt = generate_sql_payload_v3(
                user_question,
                class_names,
                similar_records,
                professional_vocab
            )
            print("优化后的提示模板:\n", prompt)

            # 获取模型响应
            raw_response = model1.get_response_from_model_chushi(
                prompt,
                api_key="f7a0186af1f5730d592e6bb15b7e9961.3i3qcCyOf2VeWUVs"
            )
            print("原始模型响应:", raw_response)

            # 解析SQL
            final_sql = parse_sql_response(raw_response)

            # 构建返回结果
            result_template.update({
                "sql": final_sql,
                "metadata": {
                    "classes_searched": [cn for cn in class_names if isinstance(cn, str)],
                    "similar_records_found": len(similar_records),
                    "professional_terms": len(professional_vocab),
                    "prompt_version": "v3.2"
                }
            })

            # 确保返回值格式与调用者一致
            return (
                final_sql,
                professional_vocab,
                user_question,
                "",
                class_names,
                similar_records
            )

    except Exception as e:
        error_msg = f"SQL生成流程异常: {str(e)}"
        print(error_msg)
        result_template["metadata"]["error"] = error_msg
        return (
            "未生成有效SQL",
            [],
            user_question,
            "",
            [],
            []
        )
def generate_sql_model2(user_question,model,client):
    """
    生成SQL查询的方法。

    :param user_question: 用户问题
    :return: 返回生成的SQL查询
    """
    try:
        # 使用 ThreadPoolExecutor 来执行并行任务
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # 并行任务：石油领域专业词汇与相似例子检索
            future_professional_vocabulary = executor.submit(main, user_question, client)
            future_similar_records = executor.submit(search_similar_records, user_question, client, 2, model)

            # 获取结果
            Professional_vocabulary = future_professional_vocabulary.result()
            similar_records = future_similar_records.result()

            # 继续进行模式链接与用户查询类型识别
            future_class_names = executor.submit(main2.process_user_question, user_question, 0.8, 0.8, client)
            # future_user_question_type = executor.submit(classify_user_question, user_question)

            class_names = future_class_names.result()
            # user_question_type = future_user_question_type.result()

            # 生成SQL提示
            prompt_t = f"""
            假设您是油田领域的text-to-sql专家，请帮我根据以下信息生成用户问题对应的SQL。
            相关术语：{Professional_vocabulary}；
            用户问题：{user_question}；
            数据库结构：{class_names}；
            相似示例：{similar_records}；
            请按照以下格式输出：sql=""
            """
            print("Generated prompt for SQL:", prompt_t)

            # 获取SQL响应
            zhipu_AI_out = model2.deepseek_chat_chushi(prompt_t)
            print("ZhipuAI SQL Response:", zhipu_AI_out)
            zhipu_AI_out = zhipu_AI_out if zhipu_AI_out is not None else ""
            Professional_vocabulary = Professional_vocabulary if Professional_vocabulary is not None else ""
            user_question = user_question if user_question is not None else ""
            user_question_type =""
            class_names = class_names if class_names is not None else ""
            similar_records = similar_records if similar_records is not None else ""
            return zhipu_AI_out, Professional_vocabulary, user_question, user_question_type, class_names, similar_records

    except Exception as e:
        print(f"Error during SQL generation: {e}")
        return "", "", "", "", [], []
