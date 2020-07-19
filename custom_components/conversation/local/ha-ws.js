class HaWebSocket {
    constructor() {
        this.url = `${location.protocol == 'https' ? 'wss' : 'ws'}://${location.host}/api/websocket`
        this.id = 0
        this.events = {
            message: []
        }
    }

    // 监听事件
    on(event, action) {
        if (Reflect.has(this.events, event)) {
            this.events[event].push(action.bind(this))
        }
    }

    // hassTokens
    get hassTokens() {
        try {
            return JSON.parse(localStorage['hassTokens'])
        } catch{
            location.href = '/'
        }
    }

    set hassTokens(value) {
        localStorage['hassTokens'] = JSON.stringify(value)
    }

    // 刷新token
    refresh_token() {
        let { refresh_token, clientId } = this.hassTokens
        fetch('/auth/token', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `grant_type=refresh_token&refresh_token=${refresh_token}&client_id=${clientId}`
        }).then(res => res.json()).then(res => {
            // 重新保存token
            this.hassTokens.access_token = res.access_token
            this.hassTokens = this.hassTokens
            // 重新登录
            this.reconnect()
        })
    }

    // 连接
    connect() {
        let { url } = this
        let ws = new WebSocket(url)
        this.ws = ws

        ws.onmessage = (res) => {
            let obj = JSON.parse(res.data)
            if (this.id <= obj.id) this.id = obj.id
            // console.log(obj)
            if (obj.type == 'auth_invalid') {
                this.refresh_token()
                return
            }
            // 触发事件
            this.events['message'].forEach(action => {
                action(obj)
            })
        }
        ws.onopen = () => {
            ws.send(JSON.stringify({
                "type": "auth",
                access_token: this.hassTokens.access_token
            }))
        }
    }

    // 重新连接
    reconnect() {
        try {
            this.ws.close()
        } catch{ }
        this.id = 0
        this.connect()
    }

    // 发送消息
    send(obj) {
        if ([2, 3].includes(this.ws.readyState)) {
            alert("连接断开了！点击重新连接")
            location.reload()
        } else {
            this.ws.send(JSON.stringify({
                id: this.id + 1,
                ...obj
            }))
        }
    }
}