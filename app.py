#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@FileName:   app.py
@Author:     HuYan, Dept. of Automation , Tsinghua University
@Date:       2025-03-20
@License:    MIT
@Description: 
    一个简单的Flask后端，用于调用DeepSeek API实现定制化聊天功能
"""

from flask import Flask, request, jsonify, make_response, render_template
import os
import requests
from dotenv import load_dotenv
import time
import xml.etree.cElementTree as ET
import hashlib

load_dotenv()  # 加载.env文件中的环境变量
app = Flask(__name__)

# 配置API密钥（从环境变量读取，注意一定一定不要将API_KEY硬编码在代码中）
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
API_ENDPOINT = "https://api.deepseek.com/v1/chat/completions" 

########################################################################################
# 首页路由
########################################################################################
@app.route('/')
def index():
    return render_template('index.html')  # 会自动查找templates目录下的html渲染网页

########################################################################################
# 微信公众号开发接口，如无需要可以删去
# 注意！注意！注意！微信公众号自动回复的开发接口需要你的服务器支持80端口访问；
# 另外有一个硬伤是处理消息时限为5s，如果超时会导致消息发送失败，所以其实不建议在这里使用DeepSeek API，自寻他法吧（狗头）
########################################################################################
@app.route('/wechat',methods=['GET','POST'])
def wechat():                             # 获取携带的 signature、timestamp、nonce、echostr
    if request.method == 'GET':
        signature = request.args.get("signature", "")
        timestamp= request.args.get("timestamp", "")
        nonce= request.args.get("nonce", "")
        echostr= request.args.get("echostr", "")
        print(signature, timestamp, nonce, echostr)
        token="History"     # 自定义token，与微信公众号的设置保持一致！！！
        data =[token, timestamp, nonce]
        data.sort()         #三个参数拼接成一个字符串并进行sha1加密
        temp = ''.join(data)
        sha1= hashlib.sha1(temp.encode('utf-8'))
        hashcode=sha1.hexdigest()
        print(hashcode)     #对比获取到的signature与根据上面token生成的hashcode，如果一致，则返回echostr，对接成功
        if hashcode == signature:
            return echostr
        else:
            return "error"
    else:
        xmlData = ET.fromstring(request.stream.read())
        msg_type = xmlData.find('MsgType').text
        if msg_type == 'text':
            ToUserName = xmlData.find('ToUserName').text
            FromUserName = xmlData.find('FromUserName').text
            Content = xmlData.find('Content').text
            # 调用DeepSeek API
            headers = {
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "messages": [
                    {"role": "system", "content": "此处设置chatbot回复的风格"},
                    {"role": "user", "content": Content}
                ],
                "model": "deepseek-chat"  # "deepseek-reasoner" 
            }
            response = requests.post(API_ENDPOINT, headers=headers, json=data)
            response.raise_for_status()  
            if response.status_code == 200:
                api_data = response.json()
                Content = api_data['choices'][0]['message']['content']  # ← 这里提取content
            else:
                Content = "404：API调用失败"
        else:
            Content = "" # 其他类型消息不回复
        reply = '''
        <xml>
        <ToUserName><![CDATA[%s]]></ToUserName>
        <FromUserName><![CDATA[%s]]></FromUserName>
        <CreateTime>%s</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[%s]]></Content>
        </xml>
        ''' # 微信的数据包格式为xml，这点需要注意
        Response = make_response(reply % (FromUserName, ToUserName, str(int(time.time())), Content))
        Response.content_type = 'application/xml'
        return Response

########################################################################################
# 网页聊天接口，后端主体逻辑
########################################################################################
@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get('message')
        
        # DeepSeek API 的数据格式
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "messages": [
                {"role": "system", "content": "你是清华大学自xx班的学习小助手兼班级吉祥物，名字叫xxx，你是大家学习工作的好伙伴，所以回复的时候一定要幽默可爱哦！可以加一些表情和可爱的语气词，比如“喵”“呀”“嘿嘿”等。"},
                {"role": "user", "content": user_message}
            ],
            "model": "deepseek-reasoner"  # "deepseek-chat"，这里可以选择不同的模型，reasoner慢一点
        }
        response = requests.post(API_ENDPOINT, headers=headers, json=data)
        response.raise_for_status()  # 检查HTTP错误
        if response.status_code == 200:
            api_data = response.json()
            content = api_data['choices'][0]['message']['content']  # ← 这里提取content，如果需要reasoner的思维链自行查看文档解决
            return jsonify({
                "content": content  # ← 必须是未渲染的原始Markdown，前端会自动渲染；当然也可以自行调试prompt让模型不输出Markdown
            })
        else:
            return jsonify({"error": "API调用失败"}), 500
        # return jsonify(response.json()) # 返回API的原始数据，方便调试
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # 本地调试端口5000，80也可用，但需要root权限，自行设置


