# conversation

在HA里使用的官方语音助手修改增强版

[![hacs_badge](https://img.shields.io/badge/Home-Assistant-%23049cdb)](https://www.home-assistant.io/)
![visit](https://visitor-badge.laobi.icu/badge?page_id=shaonianzhentan.conversation&left_text=visit)

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

## 执行脚本
- 执行脚本（脚本名称=语音文本）

## node-red 和 自动化
- 监听`conversation`事件，命令文本参数：`text`

## 更新日志

### v2.0
- 重构代码，精简功能

## 如果这个项目对你有帮助，请我喝杯<del style="font-size: 14px;">咖啡</del>奶茶吧😘
|  |支付宝|微信|
|---|---|---|
奶茶= | <img src="https://cdn.jsdelivr.net/gh/shaonianzhentan/ha-docs@master/docs/img/alipay.png" align="left" height="160" width="160" alt="支付宝" title="支付宝">  |  <img src="https://cdn.jsdelivr.net/gh/shaonianzhentan/ha-docs@master/docs/img/wechat.png" height="160" width="160" alt="微信支付" title="微信">

## 关注我的微信订阅号，了解更多HomeAssistant相关知识
<img src="https://cdn.jsdelivr.net/gh/shaonianzhentan/ha-docs@master/docs/img/wechat-channel.png" height="160" alt="HomeAssistant家庭助理" title="HomeAssistant家庭助理"> 
