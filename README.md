# 语音小助手

一个在Home Assistant里使用的简单中文语音控制插件

[![badge](https://img.shields.io/badge/Home-Assistant-%23049cdb)](https://www.home-assistant.io/)
[![badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
![visit](https://visitor-badge.laobi.icu/badge?page_id=shaonianzhentan.conversation&left_text=visit)

[![badge](https://img.shields.io/badge/Conversation-语音小助手-049cdb?logo=homeassistant&style=for-the-badge)](https://github.com/shaonianzhentan/conversation)
[![badge](https://img.shields.io/badge/Windows-家庭助理-blue?logo=windows&style=for-the-badge)](https://www.microsoft.com/zh-cn/store/productId/9n2jp5z9rxx2)
[![badge](https://img.shields.io/badge/wechat-微信控制-6cae6a?logo=wechat&style=for-the-badge)](https://github.com/shaonianzhentan/ha_wechat)
[![badge](https://img.shields.io/badge/android-家庭助理-purple?logo=android&style=for-the-badge)](https://github.com/shaonianzhentan/ha_app)


[![badge](https://img.shields.io/badge/QQ交流群-61417349-76beff?logo=tencentqq&style=for-the-badge)](https://qm.qq.com/cgi-bin/qm/qr?k=aoYbEJzQ8MiieLhvQfhE_Ck1vLENuErf&jump_from=webapi&authKey=FT+TXsLXVNUtYY9G0q82vrBTxVT8axAg2C/tP9U1x9JioabEAbzVB7sPVGy/nIHN)

## 配置

安装完成后重启HA，刷新一下页面，在集成里搜索`语音小助手`

[![Add Integration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=conversation_assistant)

## 支持指令
- 开关设备
- 灯光亮度
- `light名称` `红|橙|黄|绿|青|蓝|紫`色
- `触发` `自动化|按钮|脚本|警报控制面板`
- `激活|启动|启用`场景
- 支持媒体播放器
- 支持空调

### 音乐

- 播放、暂停、上一曲、下一曲
- 声音小点、小点声音、小一点声音、声音小一点
- 声音大点、大点声音、大一点声音、声音大一点
- 播放每日推荐
- 我想听`歌名`
- 我想听`歌手`的歌
- 播放歌单`歌单名称`
- 播放电台`电台名称`
- 播放专辑`喜马拉雅专辑名称`

### 日历

- `一个时间点`提醒我`要做的事`
- `八点半`提醒我`洗碗`

### 电视（待实现）

- 我想看 `中央一台`
- 更多...

### 小爱音箱（待实现）

- 小爱`打开卫生间的灯`
- 小艾`打开卫生间的灯`

### 广播电台（待实现）

- 中央人民广播电台
- 仙桃人民广播电台
- 更多...

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
<img src="https://github.com/shaonianzhentan/image/raw/main/ha_wechat/pay_alipay.png" align="left" height="160" alt="支付宝" title="支付宝">  |  <img src="https://github.com/shaonianzhentan/image/raw/main/ha_wechat/pay_wechat.png" align="left" height="160" alt="微信支付" title="微信">

#### 关注我的微信订阅号，了解更多HomeAssistant相关知识
<img src="https://ha.jiluxinqing.com/img/wechat-channel.png" height="160" alt="HomeAssistant家庭助理" title="HomeAssistant家庭助理"> 

---
**在使用的过程之中，如果遇到无法解决的问题，付费咨询请加Q`635147515`**