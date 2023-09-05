import yaml
from sparkdesk_web.core import SparkWeb

with open('test.yaml', 'r') as file:
    data = yaml.safe_load(file)

config = data['xf']

sparkWeb = SparkWeb(
    cookie=config['cookie'],
    fd=config['fd'],
    GtToken=config['token']
)

def chat(text):
    print(sparkWeb.chat(text))

# single chat
chat('''你现在是一个智能家居助手，我需要你控制、查询家里的设备，知道吗？现在为将为你提供我家里相关区域的设备列表''')
# continue chat
sparkWeb.chat_stream()