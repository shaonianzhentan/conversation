class ConversationVoice extends HTMLElement {

    // 自定义默认配置
    static getStubConfig() {
        return { entity: "media_player.yun_yin_le" }
    }

    /*
     * 设置配置信息
     */
    setConfig(config) {
        if (!config.entity) {
            throw new Error('你需要定义一个实体');
        }
        this._config = config;
    }

    // 卡片的高度(1 = 50px)
    getCardSize() {
        return 3;
    }

    /*
     * 触发事件
     * type: 事件名称
     * data: 事件参数
     */
    fire(type, data) {
        const event = new Event(type, {
            bubbles: true,
            cancelable: false,
            composed: true
        });
        event.detail = data;
        this.dispatchEvent(event);
    }

    /*
     * 调用服务
     * service: 服务名称(例：light.toggle)
     * service_data：服务数据(例：{ entity_id: "light.xiao_mi_deng_pao" } )
     */
    callService(service_name, service_data = {}) {
        let arr = service_name.split('.')
        let domain = arr[0]
        let service = arr[1]
        this._hass.callService(domain, service, service_data)
    }

    // 通知
    toast(message) {
        this.fire("hass-notification", { message })
    }

    // 显示实体更多信息
    showMoreInfo(entityId) {
        this.fire('hass-more-info', { entityId })
    }

    /*
     * 接收HA核心对象
     */
    set hass(hass) {
        this._hass = hass
        if (this.isCreated === true) {
            this.updated(hass)
        } else {
            this.created(hass)
        }
    }

    // 创建界面
    created(hass) {

        /* ***************** 基础代码 ***************** */
        const shadow = this.attachShadow({ mode: 'open' });
        // 创建面板
        const ha_card = document.createElement('ha-card');
        ha_card.className = 'custom-card-panel'
        ha_card.innerHTML = `
            <input class="speech-text" type="text" placeholder="正在聆听中..." />
        `
        shadow.appendChild(ha_card)
        // 创建样式
        const style = document.createElement('style')
        style.textContent = `
            .custom-card-panel{}
        `
        shadow.appendChild(style);
        // 保存核心DOM对象
        this.shadow = shadow
        this.$ = this.shadow.querySelector.bind(this.shadow)
        // 创建成功
        this.isCreated = true

        /* ***************** 附加代码 ***************** */
        let { _config, $ } = this

        this.initRecognition()
    }

    // 更新界面数据
    updated(hass) {
        
    }

    // 初始化语音识别
    initRecognition() {
        var listenText = '';
        var recognition = new webkitSpeechRecognition();
        recognition.lang = 'cmn-Hans-CN';
        recognition.continuous = true;
        recognition.interimResults = true;

        recognition.onstart = function () {
            console.log('开始')
        }

        recognition.onerror = function (event) {
            console.log('错误')
        };

        recognition.onend = function () {
            console.log("识别结束，发送命令中...")
        }

        recognition.onresult = (event) => {
            var result = event.results;
            if (typeof (result) == 'undefined') {
                console.log("gg---");
                return;
            }
            listenText = '';
            var final_transcript = '';
            for (var i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    final_transcript += event.results[i][0].transcript;
                } else {
                    listenText += event.results[i][0].transcript;
                }
            }
            //一句话识别完毕
            if (final_transcript != "") {
                console.log(final_transcript)
                listenText = ''
                recognition.stop();
                return;
            }
            this.$('.speech-text').textContent = listenText
        }
    }
}

// 定义DOM对象元素
customElements.define('conversation-voice', ConversationVoice);

// 添加预览
window.customCards = window.customCards || [];
window.customCards.push({
    type: "conversation-voice",
    name: "语音小助手",
    preview: true,
    description: "语音识别、输入、监听"
});
