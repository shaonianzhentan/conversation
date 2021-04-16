<template>
  <component
    v-for="(item, index) in list"
    :key="index"
    :is="item.name"
    :data="item.data"
  />
  <div
    style="
      position: fixed;
      bottom: 0;
      left: 0;
      width: 100%;
      padding: 10px;
      background: white;
    "
  >
    <a-input
      placeholder="请输入文字命令"
      v-model:value="msg"
      @keydown="sendMsgKeydown($event)"
    >
      <template #prefix>
        <BarsOutlined type="user" />
      </template>
      <template #suffix>
        <a-tooltip :title="isVoice ? '自动发送' : '手动发送'">
          <span @click="toggleVoiceClick">
            <AudioOutlined style="color: rgba(0, 0, 0, 0.45)" v-if="isVoice" />
            <EditOutlined style="color: rgba(0, 0, 0, 0.45)" v-else />
          </span>
        </a-tooltip>
      </template>
    </a-input>
  </div>
</template>

<script lang="ts">
import {
  getUser,
  getAuth,
  createConnection,
  subscribeEntities,
  ERR_HASS_HOST_REQUIRED,
  Connection,
} from "home-assistant-js-websocket";
import { throttle } from "lodash";
import {
  BarsOutlined,
  AudioOutlined,
  EditOutlined,
} from "@ant-design/icons-vue";
import { defineComponent, ref } from "vue";
import CardMessage from "./components/CardMessage.vue";
import CardVideo from "./components/CardVideo.vue";
import CardState from "./components/CardState.vue";

export default defineComponent({
  components: {
    BarsOutlined,
    AudioOutlined,
    EditOutlined,
    CardMessage,
    CardVideo,
    CardState,
  },
  setup: () => {
    let list = ref<Array<any>>([]);
    let hass: Connection = null;
    return {
      hass,
      list,
      isVoice: ref<boolean>(false),
    };
  },
  data() {
    return {
      msg: "",
      throttle: throttle(
        () => {
          this.sendMsg(this.msg);
        },
        2000,
        { leading: false, trailing: true }
      ),
    };
  },
  created() {
    this.connect();
  },
  methods: {
    async connect() {
      let auth;
      try {
        // Try to pick up authentication after user logs in
        auth = await getAuth({
          loadTokens() {
            try {
              return JSON.parse(localStorage["hassTokens"]);
            } catch {}
          },
          saveTokens: (data) => {
            localStorage["hassTokens"] = JSON.stringify(data);
          },
        });
      } catch (err) {
        if (err === ERR_HASS_HOST_REQUIRED) {
          const hassUrl: any = prompt(
            "请输入要连接的HomeAssistant地址?",
            location.origin
          );
          // Redirect user to log in on their instance
          auth = await getAuth({ hassUrl });
        } else {
          alert(`Unknown error: ${err}`);
          return;
        }
      }
      const connection = await createConnection({ auth });
      // subscribeEntities(connection, (ent) => console.log(ent));
      if (location.search.includes("auth_callback=1")) {
        history.replaceState(null, "", location.pathname);
      }
      this.hass = connection;
      // 初始化登录信息
      getUser(connection).then((user) => {
        console.log("Logged in as", user);
        // 获取当前组件版本
        connection
          .sendMessagePromise({ type: "get_states" })
          .then((res: any) => {
            let entity = res.find(
              (ele) => ele.entity_id === "conversation.voice"
            );
            let query = new URLSearchParams(location.search);
            let ver = entity.attributes["version"];
            // 如果版本不一样，则跳转到最新版本
            if (query.get("ver") != ver) {
              location.search = `?ver=${ver}`;
            } else {
              this.list.push({
                name: "CardMessage",
                data: {
                  cmd: "HomeAssistant服务连接成功",
                  text: `【${user.name}】你好，欢迎使用语音小助手`,
                },
              });
            }
          });
      });
    },
    sendMsgKeydown(event) {
      const { msg, isVoice } = this;
      if (!msg) {
        return;
      }
      if (isVoice) {
        return this.throttle();
      }
      // 回车
      if (event.keyCode === 13) {
        this.sendMsg(msg);
      }
    },
    sendMsg(msg) {
      this.msg = "";
      // 发送指令
      this.hass
        .sendMessagePromise({
          conversation_id: `${Math.random()
            .toString(16)
            .substr(2, 10)}${Math.random().toString(16).substr(2, 10)}`,
          text: msg,
          type: "conversation/process",
        })
        .then(({ speech }: any) => {
          const data: any = {
            cmd: String(msg),
            text: speech.plain.speech,
          };
          this.list.push({
            name: "CardMessage",
            data,
          });
        });
    },
    toggleVoiceClick() {
      this.isVoice = !this.isVoice;
    },
  },
});
</script>

<style>
#app {
  padding: 10px;
}
#app .ant-card {
  margin-bottom: 10px;
}
</style>