# zhipuai_model.py
from zhipuai import ZhipuAI

def get_response_from_model(prompt_t, api_key="f7a0186af1f5730d592e6bb15b7e9961.3i3qcCyOf2VeWUVs"):
    """
    调用智普AI API获取响应。
    :param prompt_t: 传递给智普AI的提示词
    :param api_key: 智普AI API密钥
    :return: 模型返回的响应内容
    """
    client = ZhipuAI(api_key=api_key)
    completion = client.chat.completions.create(
        model="glm-4-air",
        messages=[{"role": "system", "content": ""}, {"role": "user", "content": prompt_t}],
        temperature=0.1,
    )
    response = completion.choices[0].message.content
    return response
