<template>
  <a-card :title="data.cmd">
    <a-list bordered>
      <a-list-item v-for="(item, index) in data.list" :key="index"
        >{{ item.name }}
        <template #actions>
          <a-switch
            :checked="item.value === 'on'"
            @click="toggleClick(item)"
            v-if="
              index === 0 &&
              [
                'input_boolean',
                'light',
                'switch',
                'fan',
                'automation',
                'climate',
              ].includes(item.domain)
            "
          />
          <span v-else>
            {{ item.value }}
          </span>
        </template>
      </a-list-item>
    </a-list>
  </a-card>
</template>
<script lang="ts">
import { defineComponent } from "vue";

export default defineComponent({
  props: {
    data: {
      type: Object,
      default() {
        return {
          cmd: "",
          text: "",
          list: [],
        };
      },
    },
    hass: {},
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
          service_data: { entity_id: item.entity_id },
        })
        .then((res) => {
          console.log(res);
        });
    },
  },
});
</script>
