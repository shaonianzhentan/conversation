<template>
  <a-list bordered>
    <a-list-item
      v-for="(item, index) in list"
      :key="index"
    >{{ item.name }}
      <template #actions>
        <a-switch
          v-if="[
                'input_boolean',
                'light',
                'switch',
                'fan',
                'automation',
                'climate',
              ].includes(item.domain)
            "
          :checked="item.value === 'on'"
          @click="toggleClick(item)"
        />
        <a-button
          v-else-if="[
                'script',
                'scene',
                'automation'
              ].includes(item.domain)"
          type="link"
          @click="triggerClick(item)"
        >触发</a-button>
        <span v-else>
          {{ item.value }}
        </span>
      </template>
    </a-list-item>
  </a-list>
</template>
<script lang="ts">
import { defineComponent, ref } from "vue";

export default defineComponent({
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
  inject: ["callService"],
  async mounted() {
    this.list = await this.load({ entity_list: this.data.list });
  },
  methods: {
    toggleClick(item) {
      console.log(item);
      const { entity_id, domain, value } = item;
      item.value = value === "on" ? "off" : "on";
      // 发送指令
      this.callService(`${domain}.turn_${item.value}`, {
        entity_id
      });
    },
    // 触发
    triggerClick({ domain, entity_id }) {
      if (domain === "script") {
        this.callService(entity_id);
      } else if (domain === "automation") {
        this.callService("automation.trigger", { entity_id });
      }
    }
  }
});
</script>
