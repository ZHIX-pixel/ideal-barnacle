import pymysql
from openai import OpenAI
from opentelemetry import trace, metrics
from opentelemetry.sdk.metrics import MeterProvider, Counter, Histogram
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader
from loguru import logger
import sentry_sdk
from sentry_sdk import capture_exception
import time
from zhipuai import ZhipuAI
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")
metric_reader = PeriodicExportingMetricReader(ConsoleMetricExporter(), export_interval_millis=5000)
# 初始化 Sentry
sentry_sdk.init(
    dsn="https://6c8b78005e6cf1e5aaa74761179f9871@o4508606767300608.ingest.us.sentry.io/4508606797774848",
    traces_sample_rate=1.0,
)


meter_provider = MeterProvider(metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)
meter = meter_provider.get_meter(__name__)

# 初始化 OpenTelemetry tracer
tracer = trace.get_tracer(__name__)  # 获取 tracer 实例
# 初始化 OpenAI 客户端
client = OpenAI(
    base_url='https://qianfan.baidubce.com/v2',  # 替换为正确的 URL
    api_key='bce-v3/ALTAK-OjJ7ldNhHGsHB3sZlj7Kg/823e35647fe3e3e7df1acf7f163f1d8c3643a6aa'
)

def get_db_model(id):
    # 连接数据库
    connection = pymysql.connect(
        host='localhost', user='root', password='123456', database='sys', charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = connection.cursor()

    # 查询 self_method
    cursor.execute('SELECT self_method FROM user WHERE id = %s', (id,))
    self_method = cursor.fetchone()

    # 提取字符串内容
    content = self_method['self_method']
    print("原始内容：", content)

    # 初始化结果
    models = []
    debug_count = None

    # 按分号分割字符串
    parts = content.split('；')  # 使用中文分号分割

    # 遍历分割后的部分
    for part in parts:
        part = part.strip()  # 去掉多余的空格
        if '--' in part:
            # 提取模型和方法
            model, method = part.split('--')
            if model.startswith('模型选择:'):
                model = model[len('模型选择:'):].strip()
            models.append((model.strip(), method.strip()))
        elif '自调试次数:' in part:
            # 提取自调试次数
            debug_count = part.split(':')[1].replace('次。', '').strip()
    return models, debug_count
def query_openai(model_name, prompt):
    try:
        response = client.chat.completions.create(
            model=model_name.lower(),  # 将模型名称转换为小写
            messages=[
                {
                    "role": "user",
                    "content": prompt  # 传递提示词
                }
            ]
        )
        logger.info(f"Request to AI model with prompt: {prompt}")  # 记录请求
        response_content = response.choices[0].message.content
        logger.info(f"Response from AI model: {response}")
        return response_content
    except Exception as e:
        print(f"调用 OpenAI 接口时发生错误：{e}")
        return None

# a,b=get_db_model(1)
# for model_name, description in a:
#     print(f"处理模型：{model_name}，描述：{description}")
# print(a)
# print(b)