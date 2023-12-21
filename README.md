# ipToEmail

    python实现开机发送本机ip地址到指定邮件和获取新闻热榜前50一并发送

由来（Cause）：最近一直在使用ipv6地址远程桌面办公，使用的DDNS-GO作为域名动态代理，但有时候代理有一定的延时无法及时映射到域名上进行远程桌面；所以就想到用Python写一个自动化脚本在计算机启动的时候启动检测ip地址并发送到邮件里，我再拿到需要的ip地址直接进行远程桌面；
     

------



## First：

最开始是使用公共的网站获取ip地址但都不太稳定，最后想到CMD命令行可以 ipconfig查看信息
![image](https://github.com/kokotao/ipToEmail/assets/46886876/34e332e7-d08c-4987-8b45-77b249c21751)
·于是用Python os启动命令行获取物理网卡ip地址

		output = os.popen("ipconfig /all").read()
		if output:
	with open('详细网络信息.txt', 'w') as file:
	    file.write(output)
		result = re.findall(r"(([a-f0-9]{1,4}:){7}[a-f0-9]{1,4})", output, re.I)

## Secondly：

然后就是拼接邮件中的html页面
		

```python
`html_message =` f"""<html><body style="text-align: center;width: 500px;background-color: #fbf6ee8c;"><p style="color:#0000ff8c;text-align: center;font-size: 18px;"><strong>Old ip address is</strong></p><div style="margin-bottom: 5px;padding: 2px;margin: 2px;background: #f0f8ff6e;">{old_ip}</div><p style="color:blue;text-align: center;font-size: 18px;"><strong>New ip address is</strong></p><div style="margin-bottom: 5px;padding: 2px;margin: 2px;background: #f0f8ff6e;"> {ip_addrs}</div><div stylt="text-align:right">时间：{formatted_time}</div></body></html>`
               """`
```



## Thirdly:

接下来是如何发送邮件：

1. 邮箱配置*email_config JSON文件*

   ```json
   {
     "mail_host": "smtp.163.com",
     "mail_user": "KOKOTAO",
     "mail_pass": "XXXXXXX",
     "sender": "XXXX@163.com",
     "receivers": ["6666666@qq.com", "XXX@163.com"]
   }
   ```

   

   ```python
   # 读取email_config JSON文件
   with open('email_config.json', 'r') as file:
       email_config = json.load(file)
   # 第三方 SMTP 服务
   mail_host = email_config.get('mail_host')  # smtp server
   mail_user = email_config.get('mail_user')  # Username
   mail_pass = email_config.get('mail_pass')  # Authorization password, non-login password
   ```

   

2. 消息创建

```Python
# multiple_message_contents
message = MIMEMultipart()
# the_content_of_a_single_message
# message = MIMEText(html_message, "html")  # 内容, 编码
 # 添加附件1
    attachment_path = "详细网络信息.txt"
    attachment = open(attachment_path, "rb")
    part = MIMEBase("application", "octet-stream")
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f"attachment; filename= IpDetail.txt")
    message.attach(part)
 #添加附件2
```

3.发送消息

```python
 try:
        smtpObj = smtplib.SMTP_SSL(mail_host, 465)  # 启用SSL发信, 端口一般是465
        smtpObj.login(mail_user, mail_pass)  # 登录验证
        smtpObj.sendmail(sender, receivers, message.as_string())  # 发送
        print("mail has been send successfully.")
    except smtplib.SMTPException as e:
        print(e)
```

## Finally：

打包部署到Windows自启动

1. 打包为exe可执行文件

   使用pyinstaller工具进行打包

   命令如下：

   ```cmd
   pyinstaller -F ipToEmail.py
   ```

   之后会在文件夹主目录下生成dist文件夹中对应的exe文件

  ![image](https://github.com/kokotao/ipToEmail/assets/46886876/13b57d6c-8518-4035-a60e-30273cb13ea6)


2. 部署到Windows自启动

把改exe文件放在常用的程序文件夹中，保证配置邮箱json文件在同一层文件目录中

![image](https://github.com/kokotao/ipToEmail/assets/46886876/aaa6658d-3735-4262-acf3-ce9974eb997b)


最后新建一个启动快捷方式把其放在[C:\Users\youUserName\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup](C:\Users\youUserName\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup)

自启动路径下

![image](https://github.com/kokotao/ipToEmail/assets/46886876/2130ac3b-77f3-4bb4-b419-6246b406f05c)


这样电脑每次启动的时候就会自启动一次；

**效果：**

![image](https://github.com/kokotao/ipToEmail/assets/46886876/78a07e16-fa98-44df-96c2-7aa57ba91a43)

**另外**还抓取了最近的热榜新闻这样每天早晨开机顺道能看一下最近热闻啦！

![image](https://github.com/kokotao/ipToEmail/assets/46886876/4a7e94d5-fa86-41ab-9918-464af79ad958)
