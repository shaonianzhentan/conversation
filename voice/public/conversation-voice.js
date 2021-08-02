class VoiceRecognition {

    constructor() {
    }

    async startPorcupine() {
        console.log('加载中，请等待...')
        const porcupineWorker = await PorcupineWebEnWorker.PorcupineWorkerFactory.create(
            [{ builtin: "Jarvis", sensitivity: 0.65 }]
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
                console.log('初始化完成')
            }, 1000)
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
            console.log('错误')
            this.setListeningText('出现错误')
        };

        recognition.onend = function () {
            console.log("识别结束，发送命令中...")
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
                    background: rgba(0, 0, 0, .5);
                    filter: blur(10px);
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

document.addEventListener("DOMContentLoaded", function () {

    const vf = new VoiceRecognition()
    vf.startPorcupine()
    window.VOICE_RECOGNITION = vf

});