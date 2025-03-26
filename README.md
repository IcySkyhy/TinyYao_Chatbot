<!--
SPDX-FileCopyrightText: HuYan, Dept. of Automation , Tsinghua University
SPDX-License-Identifier: MIT
-->

# 伍小遥 TinyYao_release_v1.0.0 
<h5 align = "center">基于 DeepSeek API 开发的 Chatbot 网页应用</h5>

## 功能介绍
代码应用样例可以访问http://183.172.124.17:5000/，此处不再赘述
- 服务器开启时间为**6:00-23:50**
- 由于信号波动偶尔可能断连，请稍后（1分钟左右）再试
- 在该实例中 Chatbot 的设定为一个可爱的学习小助手
- WeChat 开发者接口不可用，因为当前网络阻断了 80 端口
- 请不要对服务器进行攻击

## 快速开始
### 环境依赖
```
click==8.1.8
dotenv==0.9.9
Flask==3.1.0
python-dotenv==1.0.1
requests==2.32.3
six==1.17.0
urllib3==2.3.0
```
可以使用Python虚拟环境
```bash
python3 -m venv venv
source venv/bin/activate
```
### 变量设置
1. 环境变量设置
需要将你的 API_KEY 设置到环境变量`.env`中
```bash
cd /your/project/path/
echo "DEEPSEEK_API_KEY=YOUR_OWN_API_KEY" >> .env
```
2. 对前端和后端的 Customization 进行设置
```Python
data = {
                "messages": [
                    {"role": "system", "content": "此处设置chatbot回复的风格"},
                    {"role": "user", "content": Content}
                ],
                "model": "deepseek-chat"  # "deepseek-reasoner" 
            }
```
和
```Html
<h1>Hi，我是xxxxChatBot，请问有什么可以帮你？</h1> // 设置个性化欢迎语
```
### 启动服务器
根据你的需求选择访问端口，默认为 80 端口，其他端口要在 IP 之后加端口后缀
```bash
flask run --host=0.0.0.0 --port=5000
```
可以本地调试或者直接访问http://<your_ipv4>:<your_port>/