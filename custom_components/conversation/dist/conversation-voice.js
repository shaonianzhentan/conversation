class VoiceRecognition {

    constructor() {
        this.hotwords = 'Hey Google'
    }

    loadScript(src) {
        return new Promise((resolve) => {
            const js = document.createElement('script')
            js.src = src
            js.onload = () => {
                resolve()
            }
            document.body.appendChild(js)
        })
    }

    get hass() {
        return document.querySelector('home-assistant').hass
    }

    fire(type, data) {
        const event = new Event(type, {
            bubbles: true,
            cancelable: false,
            composed: true
        });
        event.detail = data;
        const ha = document.querySelector('home-assistant')
        ha && ha.dispatchEvent(event);
    }

    callService(service_name, service_data = {}) {
        let arr = service_name.split('.')
        let domain = arr[0]
        let service = arr[1]
        this.hass.callService(domain, service, service_data)
    }

    // 通知
    toast(message) {
        this.fire("hass-notification", { message })
    }

    async startPorcupine() {
        const { hotwords } = this
        console.log('加载中，请等待...')
        const porcupineWorker = await PorcupineWebEnWorker.PorcupineWorkerFactory.create(
            [{ builtin: hotwords, sensitivity: 0.65 }]
        );
        porcupineWorker.onmessage = (msg) => {
            console.log(msg)
            switch (msg.data.command) {
                case 'ppn-keyword':
                    // Porcupine keyword detection
                    console.log("Porcupine detected " + msg.data.keywordLabel);
                    this.stopPorcupine()
                    // 开始执行语音识别
                    if (!this.recognition) {
                        this.initRecognition()
                    }
                    this.recognition.start()
                    break;
                default:
                    break;
            }
        };
        try {
            const webVp = await WebVoiceProcessor.WebVoiceProcessor.init({
                engines: [porcupineWorker]
            });
            this.webVp = webVp
            this.porcupineWorker = porcupineWorker
            setTimeout(() => {
                // console.log('语音助手准备好了')
                this.toast(`语音助手准备好了，对我说${hotwords}，唤醒我吧`)
            }, 1500)
        } catch (ex) {
            console.error(ex)
        }
    }

    stopPorcupine() {
        this.webVp.release()
        this.porcupineWorker.postMessage({ command: "release" })
    }


    // 初始化语音识别
    initRecognition() {
        let listenText = '';
        let recognition = new webkitSpeechRecognition();
        recognition.lang = 'cmn-Hans-CN';
        recognition.continuous = true;
        recognition.interimResults = true;

        recognition.onstart = () => {
            console.log('开始')
            this.startListening()
        }

        recognition.onerror = (event) => {
            this.stopListening()
            this.toast("语音识别出现错误")
        };

        recognition.onend = () => {
            this.stopListening()
            window.VOICE_RECOGNITION.startPorcupine()
        }

        recognition.onresult = (event) => {
            const result = event.results;
            if (typeof (result) == 'undefined') {
                console.log("gg---");
                return;
            }
            listenText = ''
            let final_transcript = '';
            for (let i = event.resultIndex; i < result.length; i++) {
                const transcript = result[i][0].transcript;
                if (result[i].isFinal) {
                    final_transcript += transcript
                } else {
                    listenText += transcript;
                }
            }
            // 一句话识别完毕
            if (final_transcript != "") {
                console.log(final_transcript)
                this.callService('conversation.process', { text: final_transcript })
                recognition.stop();
                return;
            }
            console.log(listenText)
            this.setListeningText(listenText)
        }
        this.recognition = recognition
    }

    // 开始监听
    startListening() {
        const div = document.createElement('div')
        div.classList.add('conversation-voice')
        div.innerHTML = `
            <div class="conversation-voice-bg"></div>
            <div class="conversation-voice-text">正在聆听中...</div>
            <style>
                .conversation-voice-bg {
                    width: 100%;
                    height: 100vh;
                    position: fixed;
                    background: rgba(0, 0, 0, .8);
                }
                .conversation-voice-text {
                    color: white;
                    font-size: 20px;
                    text-align: center;
                    position: fixed;
                    top: 40%;
                    width: 100%;
                }
            </style>
        `
        document.body.appendChild(div)
    }

    // 设置监听内容
    setListeningText(text) {
        document.querySelector('.conversation-voice-text').textContent = text
    }

    // 停止监听
    stopListening() {
        const cv = document.querySelector('.conversation-voice')
        if (cv) {
            cv.remove()
        }
    }
}

(async function () {
    if (location.protocol == 'https:') {
        const vf = new VoiceRecognition()
        await vf.loadScript('https://unpkg.com/@picovoice/porcupine-web-en-worker/dist/iife/index.js')
        await vf.loadScript('https://unpkg.com/@picovoice/web-voice-processor/dist/iife/index.js')
        vf.startPorcupine()
        window.VOICE_RECOGNITION = vf
    }
})();