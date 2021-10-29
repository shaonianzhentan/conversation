class VoiceRecognition {

    constructor() {
        this.hotwords = 'Hey Google'
        this.isMobile = 'ontouchend' in document.body
        this.init()
    }

    async init() {
        if (this.isMobile) {
            await this.loadScript('https://cdn.jsdelivr.net/gh/xiangyuecn/Recorder@master/recorder.wav.min.js')
        }

        await this.loadScript('https://unpkg.zhimg.com/@picovoice/porcupine-web-en-worker/dist/iife/index.js')
        await this.loadScript('https://unpkg.zhimg.com/@picovoice/web-voice-processor/dist/iife/index.js')
        this.startPorcupine()
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
                    if (this.isMobile) {
                        this.initVoiceRecorder()
                    } else {
                        if (!this.recognition) {
                            this.initRecognition()
                        }
                        this.recognition.start()
                    }
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

    // 初始化录音
    initVoiceRecorder() {
        const recorder = Recorder({ type: "wav", sampleRate: 16000 });
        recorder.open(() => {
            recorder.start();
            this.startListening()
            let step = 4
            let timer = setInterval(() => {
                step -= 1
                this.setListeningText(`正在聆听中...${step}秒`)
                if (step <= 0) {
                    clearInterval(timer)
                    // 录音结束
                    recorder.stop(async (blob, duration) => {
                        recorder.close();
                        if (duration > 2000) {
                            window.VOICE_RECOGNITION.startPorcupine()
                            // 上传识别
                            const body = new FormData();
                            body.append("wav", blob);
                            const res = await fetch('/xunfei-api/stt', {
                                method: 'post',
                                body
                            }).then(res => res.json())
                            if (res.code == 0) {
                                this.callService('conversation.process', { text: res.data })
                                this.toast(res.data)
                            }else{
                                this.toast(res.msg)
                            }
                            this.stopListening()
                        } else {
                            this.toast('提示：当前录音时间没有2秒', -1)
                        }
                    }, (msg) => {
                        this.toast("录音失败:" + msg);
                    });
                }
            }, 1000)
        }, (msg, isUserNotAllow) => {
            console.log((isUserNotAllow ? "UserNotAllow，" : "") + "无法录音:" + msg);
            // 如果没有权限，则显示提示
            if (isUserNotAllow) {
                this.toast('无法录音：' + msg)
            }
        });
        this.recognition = recorder
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

if (location.protocol == 'https:') {
    window.VOICE_RECOGNITION = new VoiceRecognition()
}