# ipToEmail
    python实现开机发送本机ip地址到指定邮件和获取新闻热榜前50一并发送
由来（Cause）：最近一直在使用ipv6地址远程桌面办公，使用的DDNS-GO作为域名动态代理，但有时候代理有一定的延时无法及时映射到域名上进行远程桌面；所以就想到用Python写一个自动化脚本在计算机启动的时候启动检测ip地址并发送到邮件里，我再拿到需要的ip地址直接进行远程桌面；
     
First：最开始是使用公共的网站获取ip地址但都不太稳定，最后想到CMD命令行可以 ipconfig查看信息
![image](https://github.com/kokotao/ipToEmail/assets/46886876/34e332e7-d08c-4987-8b45-77b249c21751)
·于是用Python os启动命令行获取物理网卡ip地址

		output = os.popen("ipconfig /all").read()
		if output:
    with open('详细网络信息.txt', 'w') as file:
        file.write(output)
		result = re.findall(r"(([a-f0-9]{1,4}:){7}[a-f0-9]{1,4})", output, re.I)
Secondly：然后就是拼接邮件中的html页面
		html_message = f"""
               <html>
                 <body style="text-align: center;width: 500px;background-color: #fbf6ee8c;">
                   <p style="color:#0000ff8c;text-align: center;font-size: 18px;"><strong>Old ip address is</strong></p>
                    <div style="margin-bottom: 5px;padding: 2px;margin: 2px;background: #f0f8ff6e;">{old_ip}</div>
                    <p style="color:blue;text-align: center;font-size: 18px;"><strong>New ip address is</strong></p>
                     <div style="margin-bottom: 5px;padding: 2px;margin: 2px;background: #f0f8ff6e;"> {ip_addrs}</div>
                     <div stylt="text-align:right">时间：{formatted_time}</div>
                 </body>
               </html>
               """
