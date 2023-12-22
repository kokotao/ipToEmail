import json
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
import re
import os
import time
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import requests
from flask import Flask, jsonify

app = Flask(__name__)

# # 通过python启动命令行获取物理网卡ip地址（Use the Python CLI to obtain the IP address of the NIC）
output = os.popen("ipconfig /all").read()
if output:
    with open('详细网络信息.txt', 'w') as file:
        file.write(output)
result = re.findall(r"(([a-f0-9]{1,4}:){7}[a-f0-9]{1,4})", output, re.I)
result2 = requests.get('https://myip4.ipip.net').text
ip_addresses = []
ip_addr = ""
ip_addr += f"<div style='font-family: Arial, sans-serif; font-size: 17px; margin-bottom: 5px;'><strong>ipv4:</strong> {result2}</div>"
if result:
    for i in range(len(result)):
        ip_addresses.append(result[i][0])
    if ip_addresses:
        for i, ip in enumerate(ip_addresses, start=1):
            ip_addr += f"<div style='font-family: Arial, sans-serif; font-size: 14px; margin-bottom: 5px;'><strong>ipv6_{i}:</strong> {ip}</div>"
    else:
        ip_addr += "<div>No IPV6 address found.</div>"
else:
    ip_addr += "<div>No IPV6 match found.</div>"

# 配置文件名 留存前后网卡ip地址信息
config_file_name = '.historicalIP.json'
# 读取email_config JSON文件
with open('email_config.json', 'r') as file:
    email_config = json.load(file)
# 第三方 SMTP 服务
mail_host = email_config.get('mail_host')  # smtp server
mail_user = email_config.get('mail_user')  # Username
mail_pass = email_config.get('mail_pass')  # Authorization password, non-login password

sender = email_config.get('sender')  # sender_s_email_address
receivers = email_config.get('receivers')  # To receive e-mails, you can set up an e-mail address for any international service
# 获取当前时间
current_time = datetime.now()

# 格式化当前时间为字符串
formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
title = formatted_time + ':update_addrIp'  # The subject of the message
html_message = ''  # The content of message

def generate_news():
    try:
        response = requests.get('https://r.inews.qq.com/gw/event/pc_hot_ranking_list?ids_hash=&offset=0&page_size=50')
        data = response.json()
        idlist = data.get("idlist", [])
        newList = idlist[0].get('newslist', [])
        newsContent = ''
        newsContentTxt = ''
        for i, item in enumerate(newList, start=0):
            if i >= 1:
                title = item.get('title')
                url = item.get('url')
                nlpAbstract = item.get('nlpAbstract')
                ranking = item.get('ranking')
                newsContentTxt += f"{title}\n{nlpAbstract}\n"
                newsContent += f"<div style='font-family: Arial, sans-serif; font-size: 15px; margin-bottom: 5px;'><strong></strong>热度排行：{ranking} <a href='{url}' style='color: #0000FF; text-decoration: none;'>{title}<br></a><span style='font-size=10px;color:#a3aaaf'>{nlpAbstract}</span></br></div>"
        print(f"获取此刻新闻排行成功！总共: {str(i)}条")
        if newsContentTxt:
            with open('新闻副本.txt','w', encoding='utf-8') as file:
                file.write(newsContentTxt)
        return newsContent
    except Exception as e:
        print(f"Error fetching news ids: {str(e)}")
        return f"Error fetching news ids: {str(e)}"


# 检查配置文件及其权限
def check_configfile_exist():
    file_exist = os.access(config_file_name, os.F_OK)
    file_read = os.access(config_file_name, os.R_OK)
    file_write = os.access(config_file_name, os.W_OK)
    return {'file_exist': file_exist, 'file_read': file_read, 'file_write': file_write}


def generate_configfile(ip_addr):
    config_construct = {
        "ip_addr": ip_addr
    }
    with open(config_file_name, "w", encoding='utf-8') as fp:
        fp.write(json.dumps(config_construct, indent=4, ensure_ascii=False))
    fp.close()


def sendEmail():
    # message = MIMEText(html_message, 'plain', 'utf-8')  # 内容, 格式, 编码
    # multiple_message_contents
    message = MIMEMultipart()
    # the_content_of_a_single_message
    # message = MIMEText(html_message, "html")  # 内容, 编码
    message['From'] = "{}".format(sender)
    message['To'] = ",".join(receivers)
    message['Subject'] = title
    message.attach(MIMEText(html_message, "html"))
    # 添加附件1
    attachment_path = "详细网络信息.txt"
    attachment = open(attachment_path, "rb")
    part = MIMEBase("application", "octet-stream")
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f"attachment; filename= IpDetail.txt")
    message.attach(part)
    #添加附件2
    att1 = MIMEText(open('新闻副本.txt', 'rb').read(), 'base64', 'utf-8')  # 文件路径是这个代码附近的文件
    att1["Content-Type"] = 'application/octet-stream'
    att1["Content-Disposition"] = 'attachment; filename="newContentCopy.txt"'
    message.attach(att1)
    try:
        smtpObj = smtplib.SMTP_SSL(mail_host, 465)  # 启用SSL发信, 端口一般是465
        smtpObj.login(mail_user, mail_pass)  # 登录验证
        smtpObj.sendmail(sender, receivers, message.as_string())  # 发送
        print("mail has been send successfully.")
    except smtplib.SMTPException as e:
        print(e)

localtime = time.localtime(time.time())  # 打印本地时间
print("\n" + time.asctime(localtime))

if (ip_addr):
    ip_addrs = ip_addr
    # ip_addr = "ip_1 :" + my_ip_1 + "\n" + "ip_2 :" + my_ip_2

if (check_configfile_exist()['file_exist'] & check_configfile_exist()['file_write']):
    config_file = open(config_file_name, 'r', encoding='utf-8')
    read_context = json.load(config_file)
    old_ip = read_context['ip_addr']
    config_file.close()
    if (old_ip == ip_addrs):
        newsStr = generate_news()
        title = formatted_time + ':ip address is up-to-date'  # 邮件主题
        html_message = f"""
                       <html>
                         <body style="text-align: center;width: 500px;background-color: #fbf6ee8c;">
                         <p color:red>ip已经是最新的啦!</p>
                           <p style="color:#0000ff8c;text-align: center;font-size: 18px;"><strong>新闻热度排行榜</strong></p>
                            <div style="margin-bottom: 5px;padding: 2px;margin: 2px;background: #f0f8ff6e;">{newsStr}</div>
                            <strong>ipv4:</strong> {result2}</div>
                         </body>
                       </html>
                       """
        sendEmail()
        print("ip address is up-to-date")
    else:
        newsStr = generate_news()
        content = "old ip address is : " + old_ip + '\n' + "new ip address is : " + ip_addrs
        html_message = f"""
               <html>
                 <body style="text-align: center;width: 500px;background-color: #fbf6ee8c;">
                   <p style="color:#0000ff8c;text-align: center;font-size: 18px;"><strong>Old ip address is</strong></p>
                    <div style="margin-bottom: 5px;padding: 2px;margin: 2px;background: #f0f8ff6e;">{old_ip}</div>
                    <p style="color:blue;text-align: center;font-size: 18px;"><strong>New ip address is</strong></p>
                     <div style="margin-bottom: 5px;padding: 2px;margin: 2px;background: #f0f8ff6e;"> {ip_addrs}</div>
                    <div id="newsContainer" >
                    <p style="color: #0000ff8c; text-align: center; font-size: 18px;"><strong>新闻热度排行榜</strong></p>
                    <div style="margin-bottom: 5px; padding: 2px; margin: 2px; background: #f0f8ff6e;">
                         <!-- 这里插入新闻热度排行榜的内容，使用newsStr -->
                                {newsStr}
                                 </div>
                        </div>
                     <div stylt="text-align:right">时间：{formatted_time}</div>
                 </body>
               </html>
               """
        sendEmail()
        generate_configfile(ip_addrs)
else:
    generate_configfile(ip_addrs)
    newsStr = generate_news()
    html_message = f"""
                   <html>
                     <body style="text-align: center;width: 500px;background-color: #fbf6ee8c;">
                        <p style="color:blue;text-align: center;font-size: 18px;"><strong>Ip address is</strong></p>
                         <div style="margin-bottom: 5px;padding: 2px;margin: 2px;background: #f0f8ff6e;"> {ip_addrs}</div>
                        <div id="newsContainer" >
                        <p style="color: #0000ff8c; text-align: center; font-size: 18px;"><strong>新闻热度排行榜</strong></p>
                        <div style="margin-bottom: 5px; padding: 2px; margin: 2px; background: #f0f8ff6e;">
                             <!-- 这里插入新闻热度排行榜的内容，使用newsStr -->
                                    {newsStr}
                                     </div>
                            </div>
                         <div stylt="text-align:right">时间：{formatted_time}</div>
                     </body>
                   </html>
                   """
    sendEmail()
# @app.route('/get_news_ids', methods=['GET'])
# def get_news_ids_endpoint():
#     news_ids = generate_news()
#     return jsonify({"idlist": news_ids})
#
# if __name__ == '__main__':
#     app.run(debug=True)
