## Geass

### 1、环境

- 项目服务端主要基于 `python` + `tornado` + `mongodb` + `redis` 开发
- 项目前端主要基于 `jquery` + `requirejs` + `art-template` 开发

环境搭建 (以ubuntu 为例)：

mongodb 安装: <https://docs.mongodb.org/manual/tutorial/install-mongodb-on-ubuntu/>

``` shell
// pymongo 安装

sudo pip install pymongo    // 也可以尝试用apt安装
```

``` shell
// redis 安装

sudo apt-get install redis-server
sudo apt-get install python-redis
```

``` shell
// tornado 安装

sudo pip install tornado==3.2.2     // 目前服务器使用版本3.2.2，你也可以尝试使用其他版本
```

``` shell
// 安装微信和七牛相关SDK

sudo pip install qiniu
sudo pip install wechat-sdk
```

使用方法

``` shell
// 进入到 geass-server 目录下

touch __test__          // 主目录下存在 __test__ 文件时以测试模式启动服务
cd rest-server
sudo python main.py     // 默认端口8888

```

### 2、基础架构

  主目录结构

  ```
  ├── cache/                // 缓存模块，未完善
  ├── config/               // 统一配置
  ├── db/
  │   ├── base.py           // pymongo部分方法封装，处理数据一致 (通过models中的db映射)、格式化结果等
  │   ├── conn.py
  │   ├── __init__.py
  │   └── setting.py
  ├── doc/
  ├── helpers/
  │   ├── base.py           // 其他 helper 中共同用到的部分提了一层出来
  │   ├── __init__.py       // 把 MODEL_SLOTS 中指定的类实例化存到一个 dict (继承自 dict 的 Helper 类) 中，该 dict 作为 helpers 模块的全局变量存在
  │   ├── setting.py
  │   ├── topic/
  │   ├── user/
  │   └── wechat/
  ├── log/
  ├── models/
  │   ├── base.py           // 继承自 db，提供 get_all、get_one 方法
  │   ├── __init__.py
  │   ├── setting.py
  │   ├── topic/            // 具体的 db 映射，下同
  │   └── user/
  ├── README.md
  ├── rest-server/          // 参看 rest-server 目录结构
  ├── script/               // 工具脚本
  ├── test/                 // 测试脚本
  ├── utils/
  │   ├── escape.py         // 一堆格式化、类型转换方法封装
  │   ├── httputil.py
  │   ├── __init__.py
  │   ├── session.py        // 定义 session 相关类，提供接口访问和存储 session 中数据
  │   └── util.py
  └── wechat-server/        // 公众号服务，未启用
  ```

rest-server 目录结构

  ```
  ├── apps/
  │   ├── base.py           // 主要是对 tornado.web.RequestHandler 做了一层封装
  │   ├── __init__.py       // 生成url 与 handler 映射
  │   ├── setting.py
  │   ├── topic/
  │   │   ├── app.py        // 具体业务接口
  │   │   ├── base.py       // 对 base.py 中的BaseHandler 再做一层封装 (可选)
  │   │   └── __init__.py   // topic 下 的url 与 handler 映射
  │   ├── user/
  │   └── user_server/
  ├── daemon.sh             // 使服务在后台运行，通过 nohup
  ├── main.py
  ├── restart.sh
  ├── setting.py            // APPLICATION 配制项
  ├── static/               // 参看 static 目录结构
  └── templates/            // 模板，通过 tornado 渲染，内容中<script type="text/html">为 art-template 模板
  ```

static 目录结构

  ```
  ├── css/
  ├── favicon
  ├── font
  ├── img
  ├── js
  ├── robots.txt
  └── src
      ├── css/
      └── js/
          ├── build.js                  // r.js 配置文件
          ├── config.js                 // requirejs config 配置
          ├── module/
          │   ├── imageCompresser.js    // 图片压缩
          │   ├── JPEGEncoder.js
          │   ├── jpegMeta.js
          │   ├── thread.js             // 共用方法封装
          │   ├── uploadImg.js          // 图片上传模块
          │   └── util.js               // jquery 扩展，定义一些常用方法
          └── vendor/
  ```

------

文档有待继续完善，发现有遗误请直接修改
