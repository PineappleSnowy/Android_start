import threading
import base64
import datetime
import hashlib
import hmac
import json
from urllib.parse import urlparse
import ssl
from datetime import datetime
from time import mktime
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time

import cv2
import websocket  # 使用websocket_client
import gradio as gr

appid = "3c1ed4b2"  # 填写控制台中获取的 APPID 信息
api_secret = "MWJlZmU0NTdhNGIwMjYyYmM5YjI4NWYz"  # 填写控制台中获取的 APISecret 信息
api_key = "24b916c096bda93d9da64ae6909cd35f"  # 填写控制台中获取的 APIKey 信息

imageunderstanding_url = "wss://spark-api.cn-huabei-1.xf-yun.com/v2.1/image"  # 图片理解云端环境的服务地址
spark_url = "ws://spark-api.xf-yun.com/v3.1/chat"  # 星火大模型3.1云端环境的服务地址
text = []
answer = ""
domain = ""


class WsParam(object):
    # 初始化
    def __init__(self, APPID, APIKey, APISecret, url_):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.host = urlparse(url_).netloc
        self.path = urlparse(url_).path
        self.img_or_chat_url = url_

    # 生成url
    def create_url(self):
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + self.host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + self.path + " HTTP/1.1"

        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()

        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = f'api_key="{self.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'

        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": self.host
        }
        # 拼接鉴权参数，生成url
        url = self.img_or_chat_url + '?' + urlencode(v)
        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        return url


# 收到websocket错误的处理
def on_error(ws, error):
    print("### error:", error)


# 收到websocket关闭的处理
def on_close(ws, one, two):
    print(" ")


# 收到websocket连接建立的处理
def on_open(ws):
    run_thread = threading.Thread(target=run, args=(ws,))
    run_thread.start()


def run(ws, *args):
    data = json.dumps(gen_params(appid_=ws.appid, question=ws.question))
    ws.send(data)


# 收到websocket消息的处理
def on_message(ws, message):
    # print(message)
    data = json.loads(message)
    code = data['header']['code']
    if code != 0:
        print(f'请求错误: {code}, {data}')
        ws.close()
    else:
        choices = data["payload"]["choices"]
        status = choices["status"]
        content = choices["text"][0]["content"]
        print(content, end="")
        global answer
        answer += content
        if status == 2:
            ws.close()


def gen_params(appid_, question):
    """
    通过appid和用户的提问来生成请参数
    """
    data = {
        "header": {
            "app_id": appid_,
            # "uid": "12345"
        },
        "parameter": {
            "chat": {
                "domain": domain,
                "temperature": 0.5,
                "top_k": 4,
                "max_tokens": 2048,
                "auditing": "default"
            }
        },
        "payload": {
            "message": {
                "text": question
            }
        }
    }
    return data


def main_image(appid_, api_key_, api_secret_, Imageunderstanding_url, imagedata, question):
    wsParam = WsParam(appid_, api_key_, api_secret_, Imageunderstanding_url)
    websocket.enableTrace(False)
    wsUrl = wsParam.create_url()
    ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close, on_open=on_open)
    ws.appid = appid
    ws.imagedata = imagedata
    ws.question = question
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})


def main_chat(appid_, api_key_, api_secret_, Spark_url, question):
    wsParam = WsParam(appid_, api_key_, api_secret_, Spark_url)
    websocket.enableTrace(False)
    wsUrl = wsParam.create_url()
    ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close, on_open=on_open)
    ws.appid = appid
    ws.question = question
    ws.domain = domain
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})


def getText(role, content):
    jsoncon = {"role": role, "content": content}
    text.append(jsoncon)
    return text


def getlength(text_):
    length = 0
    for content in text_:
        temp = content["content"]
        leng = len(temp)
        length += leng
    return length


def checklen(text_):
    while getlength(text_[1:]) > 8000:
        del text_[1]
    return text_


def image_understanding(img_):
    """
    notice: 传入的图片文件必须是前缀+数字+类型的命名形式，且需以start_index开始连续命名，如"picture_0.jpg"、"images/picture_1.jpg"

    initial_prompt: "请你用客观、真实、简洁的语言概括这幅图片所包含的信息。"

    :param img_: 传入的图片
    :return: 对逐张图片的描述组成的列表
    """
    global answer, domain
    domain = "image"
    answer_list = []
    ret, buffer = cv2.imencode('.jpg', img_)
    imagedata = buffer.tobytes()
    text.append({"role": "user", "content": str(base64.b64encode(imagedata), 'utf-8'), "content_type": "image"})
    Input = "请你用客观、真实、简洁的语言概括这幅图片所包含的信息。"
    question = checklen(getText("user", Input))
    main_image(appid, api_key, api_secret, imageunderstanding_url, imagedata, question)
    answer_list.append(answer)
    answer = ""
    text.clear()
    return answer_list[0]


def gradio_realize():
    interface = gr.Interface(fn=image_understanding,
                             title="视界之声Agent——环境信息提取",
                             description="传入一张图片，你将得到一段对图片信息的详细的自然语言描述！",
                             inputs=[gr.Image()],
                             outputs="text"
                             )

    interface.launch()


if __name__ == "__main__":
    gradio_realize()
