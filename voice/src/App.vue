<template>
  <a-card
    size="small"
    v-for="(item, index) in list"
    :key="index"
    :title="item.cmd"
  >
    <component
      :is="item.name"
      :data="item.data"
      :hass="hass"
      :load="loadData"
    />
  </a-card>
  <div style="
      position: fixed;
      bottom: 0;
      left: 0;
      width: 100%;
      padding: 10px;
      background: white;
    ">
    <a-input
      placeholder="请输入文字命令"
      v-model:value.trim="msg"
      @keydown.enter="sendMsgKeydown"
      :disabled="loading"
    >
      <template #prefix>
        <BarsOutlined type="user" />
      </template>
      <template #suffix>
        <a-tooltip :title="isVoice ? '自动发送' : '手动发送'">
          <span @click="toggleVoiceClick">
            <AudioOutlined
              style="color: rgba(0, 0, 0, 0.45)"
              v-if="isVoice"
            />
            <EditOutlined
              style="color: rgba(0, 0, 0, 0.45)"
              v-else
            />
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
  Connection
} from "home-assistant-js-websocket";
import { throttle } from "lodash";
import {
  BarsOutlined,
  AudioOutlined,
  EditOutlined
} from "@ant-design/icons-vue";
import { defineComponent, ref } from "vue";
import CardMessage from "./components/CardMessage.vue";
import CardVideo from "./components/CardVideo.vue";
import CardState from "./components/CardState.vue";
import CardLoading from "./components/CardLoading.vue";

export default defineComponent({
  components: {
    BarsOutlined,
    AudioOutlined,
    EditOutlined,
    CardMessage,
    CardVideo,
    CardState,
    CardLoading
  },
  setup: () => {
    let list = ref<Array<any>>([]);
    let hass: Connection = null;
    return {
      hass,
      list,
      isVoice: ref<boolean>(false)
    };
  },
  data() {
    return {
      msg: "",
      loading: false,
      throttle: throttle(
        () => {
          this.sendMsg(this.msg);
        },
        2000,
        { leading: false, trailing: true }
      )
    };
  },
  watch: {
    msg(val) {
      if (val && this.isVoice) {
        this.throttle();
      }
    }
  },
  provide() {
    return {
      callService: this.callService
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
          saveTokens: data => {
            localStorage["hassTokens"] = JSON.stringify(data);
          }
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
      getUser(connection).then(user => {
        console.log("Logged in as", user);
        // 获取当前组件版本
        connection
          .sendMessagePromise({ type: "get_states" })
          .then((res: any) => {
            let entity = res.find(
              ele => ele.entity_id === "conversation.voice"
            );
            let query = new URLSearchParams(location.search);
            let ver = entity.attributes["version"];
            // 如果版本不一样，则跳转到最新版本
            if (query.get("ver") != ver) {
              location.search = `?ver=${ver}`;
            } else {
              this.list.push({
                name: "CardMessage",
                cmd: `HomeAssistant服务连接成功`,
                data: {
                  text: `【${
                    user.name
                  }】你好，欢迎使用语音小助手，当前版本${ver}`
                }
              });
            }
          });
      });
    },
    async callService(serviceName, service_data = {}) {
      let arr = serviceName.split(".");
      const result = await this.hass.sendMessagePromise({
        type: "call_service",
        domain: arr[0],
        service: arr[1],
        service_data
      });
      console.log(result);
      return result;
    },
    // 获取当前数据
    async loadData({ entity_list }) {
      // 延时一秒获取数据
      await this.sleep(1);
      const states = await this.hass.sendMessagePromise({ type: "get_states" });
      // 获取当前实体
      const arr = states
        .filter(ele => entity_list.includes(ele.entity_id))
        .map(ele => {
          ele["domain"] = ele.entity_id.split(".")[0];
          return ele;
        });
      let list = [];
      // 单个实体
      if (arr.length === 1) {
        const { attributes, state, domain, entity_id } = arr[0];
        list = Object.keys(attributes).map(key => {
          return {
            domain,
            entity_id,
            name: key,
            value: attributes[key]
          };
        });
        list.unshift({
          domain,
          entity_id,
          name: attributes.friendly_name,
          value: state,
          isAction: true
        });
      } else {
        list = arr.map(state => {
          return {
            domain: state.domain,
            entity_id: state.entity_id,
            name: state.attributes.friendly_name,
            value: state.state,
            isAction: true
          };
        });
      }
      return list;
    },
    scrollIntoView() {
      setTimeout(() => {
        const sv = document.querySelector("#app .ant-card:nth-last-child(2)");
        sv && sv.scrollIntoView({ behavior: "smooth" });
      }, 500);
    },
    sendMsgKeydown(event) {
      const { msg, isVoice } = this;
      if (msg && !isVoice) {
        this.sendMsg(msg);
      }
    },
    async sleep(s) {
      return new Promise(resolve => {
        setTimeout(resolve, s * 1000);
      });
    },
    sendMsg(msg) {
      this.msg = "";
      const comData = {
        name: "CardLoading",
        cmd: msg,
        data: {
          text: "",
          list: []
        }
      };
      this.list.push(comData);

      // 发送指令
      this.loading = true;
      this.hass
        .sendMessagePromise({
          conversation_id: `${Math.random()
            .toString(16)
            .substr(2, 10)}${Math.random()
            .toString(16)
            .substr(2, 10)}`,
          text: msg,
          type: "conversation/process"
        })
        .then(({ speech }: any) => {
          // console.log(speech);
          comData.data.text = speech.plain.speech;
          const extra_data = speech.plain.extra_data;
          // 更多信息
          if (extra_data) {
            const entity_list = extra_data.data;
            comData.name = "CardState";
            comData.data.list = entity_list;
          } else {
            comData.name = "CardMessage";
          }
          this.list[this.list.length - 1] = JSON.parse(JSON.stringify(comData));
        })
        .finally(() => {
          this.loading = false;
        });
      this.scrollIntoView();
    },
    toggleVoiceClick() {
      this.isVoice = !this.isVoice;
    }
  }
});
</script>

<style>
#app {
  padding: 10px 10px 50px 10px;
}
#app .ant-card {
  margin-bottom: 10px;
}
</style>