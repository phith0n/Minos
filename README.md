# Minos社区
一个基于Tornado/Mongodb/Redis的简约社区系统。

### 特点
 - 简单：去除传统社区中多数不常用到的功能，保留精华。（这里向 http://zone.wooyun.org 学习）  
 - 高效：  
	 - mongodb：数据库设计合理，以空间换取时间，尽量减少数据库查询次数。  
	 - 异步：tornado+motor全异步库，增加web高并发访问效率  
	 - redis：抛弃php中以文件形式保存session的做法，以redis内存数据库保存session，增加速度。  
 - 安全：  
	 - CSP：全站默认开启CSP，以新一代的前端安全策略防御前端安全问题（包括XSS/CSRF/Clickjacking等）。  
	 - Secure by default原则：使用默认的安全机制，所有业务逻辑问题为安全让步。不符合安全的业务都没有被加入Minos。tornado框架及其安全理念对Minos的安全有突出贡献。  
	 - 注入漏洞：tornado不允许嵌套解析，用户通过GET/POST传入的参数只是字符串，不会成为list或dict，所以正常情况下不会造成mongodb的注入。  
	 - 文件上传：python将不会去解析用户上传的任何文件。另外Minos在用户上传时仍然会检查后缀，为防止XSS。  
	 - XSS漏洞：Tornado框架原则上所有输出在模板里的变量都会经过“HTML实体化”，包括单引号，一般情况下不会存在XSS漏洞。另外，社区帖子内容为富文本，将经过富文本过滤器Python-XSS-Filter（ https://github.com/phith0n/python-xss-filter ）过滤并输出。  
	 - CSRF漏洞：Tornado框架在开启xsrf\_cookies后，所有POST表单如果没有Token将不会被接受。Minos默认开启xsrf\_cookies，并且所有增删改查操作均通过POST进行。  
	 - 密码存储：Minos中，用户密码使用bcrypt库计算哈希后存入数据库，加密方法类似Wordpress，不能被简单破译。  
 - 稳定：作者女座的性格处理所有已知问题，不允许一个warning。Minos已在debian上稳定运行多日。
 - 响应式：框架AmazeUI是一个mobile first的前端框架，对于各种屏幕的适应性都很好，加上我在手机屏幕大小的情况下隐藏了很多不必要的功能，所以在手机端也能愉快地看文章啦~

### 架构简要说明
```
├── controller(所有控制器)
├── download(无用，暂时留着)
├── extends(第三方依赖库)
├── model(伪模块类，主要功能是数据库入库前检测)
├── static(静态文件，能够直接通过HTTP请求)
├── templates(模板)
├── util(通用函数与类库)
├── main.py(运行Server)
├── README.md(项目说明)
├── config.yaml.sample(配置文件示例)
└── requirements.txt(python库依赖)
```

### 安装与运行步骤
以下是安装步骤。  

 - 安装并运行Mongodb、Redis  
	 - Mongodb: https://www.mongodb.org/   
	 - Redis: http://redis.io/  
注意，Mongodb、redis请保持端口不要对外开放（监听127.0.0.1，而不是你的外网IP），或者设置密码。  
注意，mongodb版本需要在2.6及以上！不要直接apt-get安装mongodb，源里的版本普遍比较低！  

 - 下载Minos

从github下载最新版Minos源码。

	$ git clone https://github.com/phith0n/Minos.git
	$ cd Minos

 - 安装依赖项

		$ apt-get install libcurl4-openssl-dev
		$ pip install -r requirements.txt
 
安装中可能出现一些问题，主要原因是安装PIL/bcrypt等库的时候，可能会要求一些Linux下的依赖库。  
Mac下安装PIL出错：http://stackoverflow.com/questions/20325473/error-installing-python-image-library-using-pip-on-mac-os-x-10-9  
安装bcrypt出错：apt-get install build-essential libssl-dev libffi-dev python-dev   
http://stackoverflow.com/questions/22073516/failed-to-install-python-cryptography-package-with-pip-and-setup-py   
安装PIL出错：  
ImportError: The _imagingft C module is not installed  
http://stackoverflow.com/questions/4011705/python-the-imagingft-c-module-is-not-installed  
http://stackoverflow.com/questions/4984979/no-module-named-imagingft  
一个很怪的问题，我的解决方案是：  
pip install pil Pillow  
安装Pillow后就好了。  
PIP安装PIL失败：  
http://stackoverflow.com/questions/21242107/pip-install-pil-dont-install-into-virtualenv  
以上是我安装依赖库时遇到的错误和解决方法。依赖库的安装并不属于Minos安装的一部分，Minos需要的都是常见依赖库，相信很多机器上已经装过这些库了。  
有失败的再向我报告吧，共同解决。  

 - 编写配置文件

源码中有配置文件config.yaml.sample，以yaml语法编写。请根据.sample文件自行修改配置文件中的配置，并将其改名为config.yaml。  
配置文件详细说明见后面。  

 - 启动Mongodb、Redis、Minos

		nohup ./main.py --host=waf.science --port=8765 --url=http://waf.science &

\- \-host=domain 你的域名，如waf.science，默认为localhost  
\- \-port=port 你的端口，默认为8765  
 \- \-url=url 显示在前端的域名*，默认为“http://” + host + “:” + port  
 \-\-config=config 配置文件所在路径，默认为当前目录下的config.yaml，正常情况下无需修改
 
 \* 这里说明一下。Minos需要监听本地一个端口，默认为8765，则用户可以通过localhost:8765访问。但实际生产环境中，Minos一般搭建在内网，并通过nginx等服务器转发至外网，其URL可能是http://waf.science 。那么，url实际上是显示在前端HTML HEAD &lt;base&gt;中的地址，而host与port才是实际上Minos监听的地址。  
 如果你不用nginx做转发，想直接搭建Minos在外网服务器，那么只需./main.py --port=80 --url=http://yourdomain.com 即可。  

 - 运行后没有管理员。你可以在minos根目录下运行：  
	
	`python bin/initdb.py`

根据提示，输入管理员账号/密码即可新增一个管理员，并初始化数据库（主要是增加一些索引）  

### Config.yaml
配置文件详细说明。

数据库配置段：

	"database":
		"config": "mongodb://localhost:27017/" 
		"db": "minos"

 - config: Mongodb数据库连接语句，格式为：mongodb://user:pass@host:port/
 - db: 数据库名称

session配置段（redis）

	"session":
		"db": !!int "1"
		"host": "localhost"
		"port": !!int "6379"

 - db: redis数据库db（redis默认16个db，1就是其中的第2个），默认1
 - host: redis主机地址，默认localhost
 - port: redis端口号，默认6379
 - password: redis密码，没有则不用填写

全局配置段

```
"global":
  "captcha":
    "comment": !!bool "true"
    "login": !!bool "false"
    "register": !!bool "true"
  "cookie_secret": !!python/unicode "secret-key"
  "imagepath": "./static/upimg"
  "init_money": !!int "10"
  "invite_expire": !!int "604800"
  "register": !!python/unicode "open"
  "intranet": !!bool "false"
  "debug": !!bool "true"
  "site":
    "description": "站点描述"
    "keyword": "站点关键词"
    "webname": "站点名称"
  "email":
    "method": "none"
    "url": "https://api.mailgun.net/v3/domain"
    "key": "key-xxxxx"
    "sender": "root@domain"
```
global段中的所有配置项，均会被注册（覆盖默认的）成为tornado中settings的键。  

 - captcha: 配置在评论、注册、登录时，是否需要填写验证码。
 - cookie\_secret: Cookie认证密钥、全站加密密钥，请填写一个随机字符串，并不要被他人知道！！否则将会造成用户信息泄露。
 - imagepath: 图片上传相对地址
 - init_money: 用户注册后初始金币数
 - invite\_expire: 邀请码过期时间（单位秒）
 - register: 注册类型，有open、invite、close，分别为开放注册、邀请注册、关闭注册。
 - intranet: Minos是否运行于内网（是否为nginx转发），默认false
 - debug: 是否开启调试模式，默认false。  
 - site: 站点的页面配置，分别有站点名称、关键词、描述。  
 - email: 站点email配置，现仅有一种方式，mailgun。  

以上配置中，captcha、cookie\_secret、init\_money、register、site可以在管理员后台进行修改，所以不必在安装时填写。  
cookie\_secret在后台修改时，需要Minos下次启动才会生效，谨记。  

### 邮件配置
在config.yaml这一节中并没有详细说到email这一节点。  
email是Minos发送邮件的邮件服务器配置，Minos将在用户允许的情况下，在发送站内提醒的同时通过邮件进行提醒。在用户填写了邮箱的情况下，也可以通过邮箱来找回密码。  
现在暂时只支持调用maingun的API进行邮件的发送。Mailgun是国外一个非常好的免费邮件服务商，我们可以在mailgun获得一个API，通过HTTP请求发送邮件。  
Mailgun地址：https://mailgun.com/   
使用教程我就不多说了，Mailgun自己有详细说明。  

```
  "email":
    "method": "none"
    "url": "https://api.mailgun.net/v3/domain"
    "key": "key-xxxxx"
    "sender": "root@domain"
```

配置中，method的值为none时，将不发送邮件。  
method为mailgun，则使用mailgun的方式发送邮件。当使用mailgun的方式发送邮件时，你需要填写url、key，即为mailgun给你的API Base URL和API Key。  
sender是邮件中显示的发件人，格式可以邮箱，或者是类似如下：  

	Excited User <mailgun@domain.com>

格式：昵称 <邮箱>  

### 使用nginx进行反向代理
这是很重要的一章，我建议所有使用Minos的用户都使用nginx作为前端服务器。    
nginx简单配置如下（余下提高性能的配置自行设定）：  

```
location ^~ /static/
{
        root /home/wwwroot/minos;
        expires      30d;
}

location / {
        proxy_pass_header Server;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP  $remote_addr;
        proxy_pass         http://127.0.0.1:8765;
}
```

程序默认监听在8765端口，所以proxy_pass http://127.0.0.1:8765;  （你需要根据你指定的端口来配置）   
`proxy_set_header   X-Real-IP  $remote_addr;  `  
这个很重要，因为Minos运行在内网，所以在程序中获取的remote\_ip是网关(nginx)的IP，所以在这里我们一定要将真实IP通过X-Real-IP传递过去。  
同时，config.yaml中有一项为“intranet”（是否运行于内网），实际上就是影响IP获取的来源。如果intranet==True的话，IP将从X-Real-IP中获取。如果intranet==False的话，IP将直接从remote_ip获取。
所以我们需要将intranet设置为true。  

### 后续更新
请在非网站目录重新git clone一个minos（为防止更新程序出错破坏源代码），在这个minos根目录下执行其中的bin/update.py  

	python bin/update.py

则会自动调用git下载最新版Minos，完成后会提示用户输入网站目录，输入网站目录（如 /home/minos），则update.py会自动检查是否存在改动并进行覆盖更新。  
执行完成后，重启minos即可完成更新。  

### 注意事项
 1. Minos理论上支持py2/3，但实际上稳定运行于python2。而python3并没有测试。
 2. Minos不能也永远不会支持Windows环境，所以请不要在Windows下运行Minos。  
 3. Minos无需初始化数据库，直接运行mongodb即可，无需手工创建db、table等。  

### TODO
 1. 增加SMTP方式的邮件发送方法。
 2. 编写测试脚本，在py2/3环境下进行测试。
 3. 增加多语言支持。
 4. 增加网站底部自定义，使之可以填写：备案信息、统计代码等。

### LICENSE
开源协议：MPL  
请遵守MPL协议，对Minos进行二次开发与使用。  
你可以对Minos进行修改、使用，但版权属于原作者，未经作者许可不允许进行商业使用。  

![enter image description here](http://www.leavesongs.com/)