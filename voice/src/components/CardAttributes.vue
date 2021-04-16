<template>
  <a-list bordered>
    <a-list-item
      v-for="(item, index) in list"
      :key="index"
    >{{ item.name }}
      <template #actions>
        <ActionButton
          :domain="item.domain"
          :value="item.value"
          @trigger="triggerClick(item)"
          @toggle="toggleClick(item)"
        />
      </template>
    </a-list-item>
  </a-list>
</template>
<script lang="ts">
import { defineComponent } from "vue";
import ActionButton from "./ActionButton.vue";

export default defineComponent({
  components: {
    ActionButton
  },
  props: {
    data: {
      type: Object,
      default() {
        return {
          cmd: "",
          text: "",
          list: []
        };
      }
    },
    hass: {},
    load: Function
  },
  data() {
    return {
      list: []
    };
  },
  async mounted() {
    this.list = await this.load({ entity_list: this.data.list });
  },
  methods: {
    toggleClick(item) {
      console.log(item);
      item.value = item.value === "on" ? "off" : "on";
      // 发送指令
      this.hass
        .sendMessagePromise({
          type: "call_service",
          domain: item.domain,
          service: `turn_${item.value}`,
          service_data: { entity_id: item.entity_id }
        })
        .then(res => {
          console.log(res);
        });
    }
  }
});
</script>
