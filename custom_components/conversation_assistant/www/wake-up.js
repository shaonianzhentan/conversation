let WakeUpStorageObject = {}
try {
  WakeUpStorageObject = JSON.parse(localStorage['wake-up'])
} catch { }
// 唤醒词
// WakeUpStorage.key
// WakeUpStorage.switch
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
  console.info(`浏览器语音唤醒词：${WakeUpStorage.key}`);
};

customElements.whenDefined('ha-panel-lovelace').then(() => {
  const LitElement = Object.getPrototypeOf(customElements.get("ha-panel-lovelace"));
  const html = LitElement.prototype.html;
  const css = LitElement.prototype.css;

  customElements.define('conversation-assistant', class extends LitElement {

    static get properties() {
      return {
        hass: { type: Object },
        stateObj: { type: Object },
        key: { type: String },
      }
    }

    static get styles() {
      return css``
    }

    constructor() {
      super()

      this.keywords = [
        "Alexa",
        "Americano",
        "Picovoice",
        // "Bluebery",
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
    }

    // 创建界面    
    render() {
      const isSupport = location.protocol == 'https:' || location.hostname == 'localhost'
      this.key = WakeUpStorage.key || 'Hey Google'
      const WAKE_UP_SWITCH = WakeUpStorage.switch === true

      return html`<ha-attributes .hass=${this.hass} .stateObj=${this.stateObj}></ha-attributes>
      <ha-list-item twoline hasMeta>
        <span>语音唤醒</span>
        <span slot="secondary">${isSupport ? '使用唤醒词在浏览器中语音唤醒控制' : html`当前环境不支持浏览器语音唤醒`}</span>
        <ha-switch slot="meta" 
          ?disabled=${!isSupport}
          ?checked=${WAKE_UP_SWITCH}
          @change=${this._switchChange.bind(this)}></ha-switch>
      </ha-list-item>
      ${isSupport && WAKE_UP_SWITCH ? this.keywords.map((word) =>
        html`<ha-list-item @click=${() => this._selectClick(word)} value="${word}" ?activated=${word == this.key}>${word}</ha-list-item>`) : ''}
`
    }

    _switchChange() {
      WakeUpStorage.switch = !WakeUpStorage.switch
      setTimeout(() => {
        location.reload()
      }, 0)
    }

    _selectClick(key) {
      if (key != WakeUpStorage.key) {
        this.toast(`唤醒词 ${key} 将在刷新页面后生效`)
      }
      WakeUpStorage.key = key
      this.key = key
    }

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

  });
})