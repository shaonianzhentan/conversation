# conversation

在HA里使用的官方语音助手修改增强版

[![badge](https://img.shields.io/badge/Home-Assistant-%23049cdb)](https://www.home-assistant.io/)
[![badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
![visit](https://visitor-badge.laobi.icu/badge?page_id=shaonianzhentan.conversation&left_text=visit)

[![badge](https://img.shields.io/badge/Conversation-语音小助手-049cdb?logo=homeassistant&style=for-the-badge)](https://github.com/shaonianzhentan/ha_wechat)
[![badge](https://img.shields.io/badge/Windows-家庭助理-blue?logo=windows&style=for-the-badge)](https://www.microsoft.com/zh-cn/store/productId/9n2jp5z9rxx2)
[![badge](https://img.shields.io/badge/wechat-微信控制-6cae6a?logo=wechat&style=for-the-badge)](https://github.com/shaonianzhentan/ha_wechat)
[![badge](https://img.shields.io/badge/android-家庭助理-purple?logo=android&style=for-the-badge)](https://github.com/shaonianzhentan/ha_app)


> 官方文档：https://www.home-assistant.io/integrations/conversation/

## 配置

在`configuration.yaml`中添加以下配置
```yaml
# 语音小助手（高级用法请参考官方文档）
conversation:
```

## 支持指令
- 开关设备
- 灯光亮度
- `light名称` `红|橙|黄|绿|青|蓝|紫`色
- `触发` `自动化|按钮|脚本|警报控制面板`
- `激活|启动|启用`场景
- 支持媒体播放器
- 支持空调

## 执行脚本
- 执行脚本（脚本名称=语音文本）
- 自定义回复定义 `customize.yaml`
```yaml
script.1652361988272:
  reply: '回复内容，支持模板语法{{ now() }}'
```
- 正则匹配
```yaml
script.1652361988272:
  reply: 'OK, 灯已经设为{{ color }}'
  intents:
    - 把灯设为{color}
    - 把灯设成{color}
```

> 微信回复

图文信息
```yaml
script.1652361988272:
  reply: 将url参数删除，图文信息会不可点击
  extra_data:
    type: wx-image
    picurl: https://ha.jiluxinqing.com/img/wechat.png
    url: https://ha.jiluxinqing.com
```

音乐链接
```yaml
script.1652361988272:
  reply: 注意，url音乐链接中不能包含&字符
  extra_data:
    type: wx-music
    url: http://music.163.com/song/media/outer/url?id=563563649.mp3
```

> Node-Red 和 自动化
- 监听`conversation`事件，命令文本参数：`text`

## 功能

- 语音唤醒
- 文本控制

## 如果这个项目对你有帮助，请我喝杯<del style="font-size: 14px;">咖啡</del>奶茶吧😘
|支付宝|微信|
|---|---|
<img src="https://ha.jiluxinqing.com/img/alipay.png" align="left" height="160" width="160" alt="支付宝" title="支付宝">  |  <img src="https://ha.jiluxinqing.com/img/wechat.png" align="left" height="160" width="160" alt="微信支付" title="微信">


#### 关注我的微信订阅号，了解更多HomeAssistant相关知识
<img src="https://ha.jiluxinqing.com/img/wechat-channel.png" height="160" alt="HomeAssistant家庭助理" title="HomeAssistant家庭助理"> 

---
**在使用的过程之中，如果遇到无法解决的问题，付费咨询请加Q`635147515`**