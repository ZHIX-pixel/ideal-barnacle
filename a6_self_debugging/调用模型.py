from transformers import BertTokenizer, BertForSequenceClassification
import torch


# 定义推理函数
def classify_user_question(question, db_schema=None):
    model_name = 'D:/my_langchain/myProject1/000attempt/a4_User_query_type/bert训练/results/checkpoint-16890'

    # 使用local_files_only=True确保从本地加载
    tokenizer = BertTokenizer.from_pretrained(model_name, local_files_only=True)
    model = BertForSequenceClassification.from_pretrained(model_name, local_files_only=True)

    # 标签映射（确保与训练时使用的标签一致）
    label_map = {0: '简单查询', 1: '嵌套查询', 2: '多表查询', 3: '聚合查询'}

    # 处理输入问题
    schema_info = ""
    if db_schema:
        # 如果数据库模式有提供，拼接数据库模式信息
        for table_name, columns in db_schema.items():
            if isinstance(columns, list):
                schema_info += f"表名: {table_name} 列名: {', '.join(columns)} "
            else:
                schema_info += f"表名: {table_name} 列名: {columns} "

    # 编码输入
    inputs = tokenizer(question, schema_info, padding=True, truncation=True, max_length=64, return_tensors='pt')

    # 模型推理
    with torch.no_grad():
        outputs = model(**inputs)

    # 获取预测的标签
    predicted_label = torch.argmax(outputs.logits, dim=-1).item()

    # 返回分类结果
    return label_map[predicted_label]


# 示例
# question = "查询油田Z在2023年第一季度的每个月的平均日产油量，按月份排序。"
# a = generate_sql_model110(question)
# print(a)
