# conversation

在HA里使用的官方语音助手修改增强版

[![hacs_badge](https://img.shields.io/badge/Home-Assistant-%23049cdb)](https://www.home-assistant.io/)
![visit](https://visitor-badge.glitch.me/badge?page_id=shaonianzhentan.conversation&left_text=visit)

[![ha_badge](https://img.shields.io/badge/Windows-家庭助理-blue?logo=windows&style=for-the-badge)](https://www.microsoft.com/zh-cn/store/productId/9n2jp5z9rxx2)

> 官方文档：https://www.home-assistant.io/integrations/conversation/

## 配置
```yaml
# 语音小助手（高级用法请参考官方文档）
conversation:
```

启动调试服务
```yaml
service: logger.set_level
data:
  custom_components.conversation: debug
```

小度-小米空气净化器模式控制

[![导入蓝图](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Fshaonianzhentan%2Fconversation%2Fblob%2Fmain%2Fblueprints%2Fxiaodu_fan.yaml)

小度-小米飞利浦灯泡色温模式控制

[![导入蓝图](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Fshaonianzhentan%2Fconversation%2Fblob%2Fmain%2Fblueprints%2Fxiaodu_philips_light.yaml)

天猫精灵-晾衣架照明控制

[![导入蓝图](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Fshaonianzhentan%2Fconversation%2Fblob%2Fmain%2Fblueprints%2Ftmall_hanger_light.yaml)

## 云音乐指令（需要配合云音乐播放器使用）

- 我想听xxx的歌
- 播放(电台|歌单|歌曲|专辑)xxx
- 下一曲
- 上一曲
- 播放音乐
- 暂停音乐
- 声音小点、小点声音、小一点声音、声音小一点
- 声音大点、大点声音、大一点声音、声音大一点

## 指令
- `打开|开启|启动|开下|开一下|关闭|关掉|关上|关下|关一下|切换` `所有开关|所有的开关|全部开关|全部的开关|所有灯|所有的灯|全部灯|全部的灯`
- `打开|开启|启动|开下|开一下|关闭|关掉|关上|关下|关一下|切换` `x灯xx灯xxx灯`
- `打开|开启|启动|开下|开一下|关闭|关掉|关上|关下|关一下|切换` `fan名称|climate名称|switch名称|light名称|input_boolean名称|media_player名称`
- 把 `fan名称|climate名称|switch名称|light名称|input_boolean名称|media_player名称` `打开|开启|启动|开下|开一下|关闭|关掉|关上|关下|关一下`
- 把 `light名称` `调成|设为|设置为|调为` `红|橙|黄|绿|青|蓝|紫|粉|白|紫红|橄榄|随机` 色
- 把 `light名称` `调成|设为|设置为|调为` `随机|闪光|闪烁|颜色闪烁|彩虹|跑马灯|扫描|烟火` 模式
- 把 `light名称` 的亮度 `调成|调到|调为|设为` `1-100的数字`
- `media_player名称` `播放|暂停|下一曲|上一曲`
- 执行脚本 `script名称`
- `执行|触发|打开|关闭|切换`自动化`automation名称`
- `查看|查询` `Entity名称`的状态
- `查看|查询` `Entity名称`
- `Entity名称`的状态

## 摄像监控
- 查看xxx的画面

## 执行脚本
- 执行脚本（脚本名称=语音文本）

## node-red 和 自动化
- 监听ha_voice_text_event事件
- text: 语音文本

## 更新日志

### v1.5.6
- 适配小爱自定义技能退出的问题
- 测试网页语音唤醒识别
- 删除讯飞语音识别相关代码
- 支持media_player控制
- 解决HA新版异常问题
- 优化Windows应用语音识别文本解析问题

### v1.5
- 注意：`修改了配置文件格式，必需要重新配置`
- 新增python_script服务
- 新增电视频道解析
- 支持【开一下、开下、关一下、关下】命令
- 测试小度音箱控制电视功能
- 新增小度控制电视频道蓝图
- 新增小度控制小米空气净化器模式蓝图（睡眠模式、自动模式、智能模式）
- 新增小度控制小米灯泡色温控制蓝图
- 新增小度控制小米灯泡模式蓝图（照明模式、休闲/放松模式、阅读模式、夜灯模式）
- 修复小度查询电视状态异常的问题
- 支持小度自定义组合场景
- 支持天猫精灵部分电视频道
- 支持天猫精灵媒体播放器控制
- 支持天猫精灵http接入服务
- 修复小度http接入服务异常问题

### v1.4.3
- 重构语音控制页面
- 测试天猫精灵2.0接入
- 删除电影电视剧相关功能
- 修复无法创建长令牌的问题
- 完善天猫精灵控制晾衣架功能
- 完善小度音箱控制空调功能

### v1.4.1
- 支持天猫精灵自定义技能
- 增加新命令`把【实体名称】【开关命令】`
- 支持小度音箱

### v1.4
- 播放电视剧命令修改为`打开电视剧xxx`
- 新增`打开电影xxx`命令
- 使用小爱音箱查询状态时，记录语音内容
- 修复操作全部灯的时候，无法操作灯带的问题
- 集成语音文件识别服务（仅支持树莓派32位系统）
- 支持区域识别
- 支持fan开关
- 修复小爱同学查询异常的问题
### v1.3
- 解决不能操作所有灯和开关的问题
- 加入查看摄像监控的画面
- 修复`conversation.process`服务没作用的问题
- 升级`conversation`到官方最新版本
- 添加文本来源，区分内容是从哪里来的
- 当页面版本不一样时，自动跳转到最新版本页面
- 调整开关识别逻辑
- 更换新版图标
- 支持小爱同学自定义技能
- 支持灯光颜色控制（红、橙、黄、绿、青、蓝、紫、粉、白、紫红、橄榄、随机）
- 支持灯光亮度控制
- 支持灯光模式控制
- 支持电视投屏功能
- 记录语音文本
- 支持一次性打开关闭多个设备
- 支持语音结束后是否继续开麦控制
- 支持开启关闭同时操作
- 支持打开关闭空调设备
- 修复小爱同学不能退出的问题
- 加入互联网视频功能
- 小爱接口加入本机MAC标识，增强安全性
- 增加读取本地视频服务
- 修复无法匹配查询状态的问题

### v1.2
- 加入单独的聊天界面
- 支持`python_script.conversation`服务，接收`text`参数
- 优化聊天界面登录逻辑

### v1.1
- 优化代码结构
- 增加重载服务（修改配置不用重启）

### v1.0
- 当语音文本与脚本名称一致时，则触发脚本
- 语音文本匹配多个内容时，脚本名称使用=号分隔
- 定义ha_voice_text_event事件发送文本
- 语音支持：添加xxx到我的购物单
- 语音支持：我的购物单上有什么
- 集成聊天机器人

## 意图配置
注意：小爱自定义技能配置没有@符号
```
打开@{text}
启动@{text}
切换@{text}
触发@{text}
执行@{text}
播放@{text}
暂停@{text}
声音@{text}
把@{text}
开@{text}
关@{text}
查@{text}
下@{text}
上@{text}
小@{text}
我@{text}
```

## 小度自定义通用属性

```yaml
# 开关类型改为插座类型
xiaodu_type: SOCKET

# script模拟电视
xiaodu_name: 电视
xiaodu_domain: media_player

# sensor传感器
xiaodu_name: 温度传感器

xiaodu_name: 湿度传感器

# 摄像头（CAMERA、WEBCAM）
xiaodu_name: 摄像头
xiaodu_type: WEBCAM
xiaodu_domain: camera

# automation场景（打开、关闭）
xiaodu_name: 音乐模式
xiaodu_domain: scene

# automation场景（打开、关闭）
xiaodu_name: 音乐模式
xiaodu_domain: scene
```

> 小度开发相关文档

- [设备类型与模式表](https://dueros.baidu.com/didp/doc/dueros-bot-platform/dbp-smart-home/protocol/control-message_markdown#%E8%AE%BE%E5%A4%87%E7%B1%BB%E5%9E%8B%E4%B8%8E%E6%A8%A1%E5%BC%8F%E8%A1%A8)

## 天猫精灵2.0

- [开放平台](https://iot.aligenie.com/home)
- [开发文档](https://www.yuque.com/qw5nze/ga14hc/cmhq2c)

配置注意事项：`技能图文内容`要全部填写才能生效

```yaml
# 开关类型改为插座类型
tmall_type: outlet
```

## 相关问题

- 与智能音箱对接，域名必须为https。如果没有可联系我，提供HTTP转HTTPS代理服务
- 我的设备有限，所以支持不全，如有需要，可联系我添加

## 如果这个项目对你有帮助，请我喝杯<del style="font-size: 14px;">咖啡</del>奶茶吧😘
|支付宝|微信|
|---|---|
<img src="https://github.com/shaonianzhentan/ha-docs/raw/master/docs/img/alipay.png" align="left" height="160" width="160" alt="支付宝" title="支付宝">  |  <img src="https://github.com/shaonianzhentan/ha-docs/raw/master/docs/img/wechat.png" align="left" height="160" width="160" alt="微信支付" title="微信">



#### 关注我的微信订阅号，了解更多HomeAssistant相关知识
<img src="https://github.com/shaonianzhentan/ha-docs/raw/master/docs/img/wechat-channel.png" align="left" height="160" alt="HomeAssistant家庭助理" title="HomeAssistant家庭助理"> 