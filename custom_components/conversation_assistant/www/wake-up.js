
let WakeUpStorageObject = {}
try {
    WakeUpStorageObject = JSON.parse(localStorage['wake-up'])
} catch { }
window.WakeUpStorage = new Proxy(WakeUpStorageObject, {
    get(target, property) {
        return target[property]
    },
    set(target, property, value) {
        target[property] = value
        localStorage['wake-up'] = JSON.stringify(target)
        return true
    }
})

if (WakeUpStorage.switch && (location.protocol == 'https:' || location.hostname == 'localhost')) {
    import('/www-conversation/wake-up.es.js.gz')
    // Overly complicated console tag.
    const conInfo = { header: "%c≡ wake-up".padEnd(27), ver: "%cversion *DEV " };
    const br = "%c\n";
    const maxLen = Math.max(...Object.values(conInfo).map((el) => el.length));
    for (const [key] of Object.entries(conInfo)) {
        if (conInfo[key].length <= maxLen) conInfo[key] = conInfo[key].padEnd(maxLen);
        if (key == "header") conInfo[key] = `${conInfo[key].slice(0, -1)}⋮ `;
    }
    const header =
        "display:inline-block;border-width:1px 1px 0 1px;border-style:solid;border-color:#424242;color:white;background:#03a9f4;font-size:12px;padding:4px 4.5px 5px 6px;";
    const info = "border-width:0px 1px 1px 1px;padding:7px;background:white;color:#424242;line-height:0.7;";
    console.info(conInfo.header + br + conInfo.ver, header, "", `${header} ${info}`);
};

// 添加预览
customElements.whenDefined("hui-view").then(() => {

    customElements.define('lovelace-wake-up', class extends HTMLElement {

        constructor() {
            super()

            this.keywords = [
                "Alexa",
                "Americano",
                "Picovoice",
                "Bluebery",
                "Bumblebee",
                "Computer",
                "Grapefruit",
                "Grasshopper",
                "Hey Google",
                "Hey Siri",
                "Jarvis",
                "Okay Google",
                "Picovoice",
                "Porcupine",
                "Terminator"
            ]
            this.render()

        }

        // 创建界面
        render() {
            const shadow = this.attachShadow({ mode: 'open' });
            shadow.innerHTML = `
                <style>
                    .card-header,
                    .header-footer{
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    }
                    ha-select,ha-textfield{width:100%;}
                    .tips{display:none;}
                    .hide ha-switch,
                    .hide ha-select{
                        display:none;
                    }
                    .hide .tips{
                        display:block;
                    }
                </style>
                <ha-card>
                    <h1 class="card-header">
                        <div class="name">语音唤醒</div>
                        <ha-switch></ha-switch>
                    </h1>
                    <div id="states" class="card-content">
                        <ha-select label="唤醒词">   
                            ${this.keywords.map((word) => `<mwc-list-item value="${word}">${word}</mwc-list-item>`).join('')}
                        </ha-select>
                        <div class="tips">
                            当前环境不支持语音唤醒，请使用<b>https</b>协议访问
                            <br/>
                            <a href="${location.href.replace('http://', 'https://')}" target="ha">
                                ${location.href.replace('http://', 'https://')}
                            </a>
                        </div>
                        <ha-textfield label="控制命令"></ha-textfield>
                    </div>
                    <div class="header-footer footer">
                        <div class="name">语音答复</div>
                        <ha-switch></ha-switch>
                    </div>
                </ha-card>`
            const input = shadow.querySelector('ha-textfield')
            input.onkeypress = (event) => {
                if (event.keyCode == 13) {
                    const text = input.value.trim()
                    if (text != '') {
                        this.callService('conversation.process', { text })
                        this.toast('执行成功')
                    }
                    input.value = ''
                }
            }

            if (!(location.protocol == 'https:' || location.hostname == 'localhost')) {
                shadow.querySelector('ha-card').classList.add('hide')
                return
            }

            // 语音唤醒
            const toggle = shadow.querySelector('.card-header ha-switch');
            if(typeof WakeUpStorage.switch == 'boolean') toggle.checked = WakeUpStorage.switch;

            toggle.onchange = () => {
                WakeUpStorage.switch = toggle.checked
                this.toast('刷新页面生效')
            }

            // 语音答复
            const toggleSpeech = shadow.querySelector('.header-footer ha-switch');
            if(typeof WakeUpStorage.speech == 'boolean') toggleSpeech.checked = WakeUpStorage.speech;

            toggleSpeech.onchange = () => {
                WakeUpStorage.speech = toggleSpeech.checked
            }

            // 唤醒词
            const hey = shadow.querySelector('ha-select')
            const wakeUpKey = WakeUpStorage.key
            if (wakeUpKey) {
                hey.value = wakeUpKey
            }

            hey.onchange = () => {
                if (hey.value) {
                    if (hey.value != WakeUpStorage.key) {
                        this.toast('唤醒词刷新页面生效')
                    }
                    WakeUpStorage.key = hey.value
                }
            }
        }

        setConfig(config) {

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

        // 通知
        toast(message) {
            this.fire("hass-notification", { message })
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
            this.hass.callService(domain, service, service_data)
        }

    });

    window.customCards = window.customCards || [];
    window.customCards.push({
        type: "lovelace-wake-up",
        name: "语音唤醒",
        preview: true,
        description: "语音唤醒控制"
    });
})