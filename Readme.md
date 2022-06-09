# BlastWithCaptcha

爆破带有验证码认证的请求

- 本地ocr [ddddocr](https://github.com/sml2h3/ddddocr)
- 多线程

## 使用方法

1. 拉取和配置环境

```shell
git clone https://github.com/AbelChe/BlastWithCaptcha.git
cd BlastWithCaptcha

pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```



2. 请求文件

以账号密码登录认证为例

- blast.txt

从burpsuite等工具中复制登录的请求包到blast.txt

在get或post参数中标记需要爆破的参数位置，如下所示，爆破username password 以及验证码 validCode

使用`$<index>$`标记，注意这里需要按照index的顺序设置config.yaml字典列表的顺序

设置字典列表时，验证码位置忽略顺延即可

这里1 2 3位置的对应关系：1、2对应config.yml的`target.WORDDICT_LIST`，3对应`target.CAPTCHA_INDEX`

```
POST /api/login HTTP/1.1
Host: example.com.test
Cookie: SESSION=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Content-Length: 61
Sec-Ch-Ua: " Not A;Brand";v="99", "Chromium";v="102", "Microsoft Edge";v="102"
Accept: application/json, text/plain, */*
Content-Type: application/json;charset=UTF-8
Sec-Ch-Ua-Mobile: ?0
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36
Sec-Ch-Ua-Platform: "macOS"
Origin: https://example.com.test
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: cors
Sec-Fetch-Dest: empty
Referer: https://example.com.test/
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6
Connection: close

{"username":"$<1>$","password":"$<2>$","validCode":"$<3>$"}
```

- captcha.txt

直接复制burpsuite中请求验证码的数据包即可

```
GET /captcha.jpg HTTP/1.1
Host: example.com.test
Cookie: SESSION=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Sec-Ch-Ua: " Not A;Brand";v="99", "Chromium";v="102", "Microsoft Edge";v="102"
Sec-Ch-Ua-Mobile: ?0
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36
Sec-Ch-Ua-Platform: "macOS"
Accept: image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: no-cors
Sec-Fetch-Dest: image
Referer: https://example.com.test/
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6
Connection: close


```

另外，**无需**考虑`blast.txt`和`captcha.txt`的cookie对应关系，程序会自动生成新回话



3. 配置

配置文件`config.yml`

```yaml
system:
  PROXY: # 上行代理 例如 127.0.0.1:8080
  REQUEST_RETRIES: 5 # requests 的重试
  ONCETIME_THREAD_POOL_SIZE: 100 # 并发数
  THREAD_POOL_SIZE: 10 # 线程池最大线程数
  TRYAGAIN_TIMES: 3 # 验证码识别失败重试次数
  USERAGENT: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 #自定义user-agent
  LFLAG: '$<' # 左标志符号
  RFLAG: '>$' # 右标志符号
  SSL_VERIFY: FALSE # requests verify配置，默认即可

ocr:
  CAPTCHA_REGEX: '.*(\w{4})' # 对ocr识别的结果进行提取
  CAPTCHA_REGEX_GETVALUE_INDEX: 1 # 搭配CAPTCHA_REGEX使用，获取其正则表达式结果位置，从1开始

target:
  CAPTCHA: captcha.txt # 验证码请求文本文件，默认即可
  CAPTCHA_DATATYPE: RAW # 验证码返回数据类型，可选择 原始图片:RAW base64编码:BASE64 自定义获取数据:CUSTOM
  CAPTCHA_CUSTOM_GETFLAG: 'image"\:"(.*?)"' # 搭配CAPTCHA_DATATYPE值为CUSTOM使用，正则表达式提取数据
  BLAST: blast.txt # 爆破的请求文本文件，默认即可
  CAPTCHA_INDEX: 3 # 验证码的位置，标志位从1开始
  WORDDICT_LIST: # 字典路径，需要注意顺序与BLAST文件中标记的顺序对应
    - /Users/AbelChe/SecTools/worddicts/fuzzDicts/userNameDict/top500.txt
    - /Users/AbelChe/SecTools/worddicts/Blasting_dictionary/top100password.txt
  SSL: True # 使用https与否
  CAPTCHA_ERROR_FLAG: # 判断验证码错误的文本标志，正则表达式
    - 验证码错误
    - 请输入正确验证码
    - 验证码异常
  CAPTCHA_ERROR_CODE: # 判断验证码错误的状态码
    - 500
    - 502
    - 403
  LOGIN_ERROR_FLAG: # 判断认证失败的标志，正则表达式
    - 用户名.?密码错误
    - 登录信息不正确
    - 验证失败
  LOGIN_ERROR_CODE: # 判断认证失败的状态码
    -
  LOGIN_SUCCESS_FLAG: # 判断登录成功的文本标志，正则表达式
    - 登录成功
  LOGIN_SUCCESS_CODE: # 判断登录成功的状态码
    - 200
    - 302
    - 301
```



4. 启动

需要python>=3.7

```shell
python BlastWithCaptcha.py
```



## 效果如下

![image-20220609101916330](Readme_resource/image-20220609101916330.png)



## TODO

- [ ] 插件（类似burp爆破的payload processing）
- [ ] 带有id的验证码
- [ ] GUI

## 使用的项目

- [https://github.com/sml2h3/ddddocr](https://github.com/sml2h3/ddddocr)
- https://github.com/psf/requests
- https://github.com/requests/toolbelt