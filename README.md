### Minos社区
一个基于Tornado/Mongodb/Redis的简约社区系统。

### Features
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

### Files
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

### Installation/Running

 - 安装并运行Mongodb、Redis  
	 - Mongodb: https://www.mongodb.org/   
	 - Redis: http://redis.io/  
注意，Mongodb、redis请保持端口不要对外开放（监听127.0.0.1，而不是你的外网IP），或者设置密码。  

 - 下载Minos

从github下载最新版Minos源码。

	$ git clone https://github.com/phith0n/Minos.git
	$ cd Minos

 - 安装依赖项

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
 
 \* 这里说明一下。Minos需要监听本地一个端口，默认为8765，则用户可以通过localhost:8765访问。但实际生产环境中，Minos一般搭建在内网，并通过nginx等服务器转发至外网，其URL可能是http://waf.science。那么，url实际上是显示在前端HTML HEAD &lt;base&gt;中的地址，而host与port才是实际上Minos监听的地址。  
 如果你不用nginx做转发，想直接搭建Minos在外网服务器，那么只需./main.py --port=80 --url=http://yourdomain.com 即可。  

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
 - cookie_secret: Cookie认证密钥、全站加密密钥，请填写一个随机字符串，并不要被他人知道！！否则将会造成用户信息泄露。
 - imagepath: 图片上传相对地址
 - init_money: 用户注册后初始金币数
 - invite_expire: 邀请码过期时间（单位秒）
 - register: 注册类型，有open、invite、close，分别为开放注册、邀请注册、关闭注册。
 - intranet: Minos是否运行于内网（是否为nginx转发），默认false
 - debug: 是否开启调试模式，默认false。
 - site: 站点的页面配置，分别有站点名称、关键词、描述。
 - email: 站点email配置，现仅有一种方式，mailgun。

以上配置中，captcha、cookie\_secret、init\_money、register、site可以在管理员后台进行修改，所以不必在安装时填写。
cookie\_secret在后台修改时，需要Minos下次启动才会生效，谨记。

