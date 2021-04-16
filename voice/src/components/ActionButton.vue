<template>
  <a-switch
    v-if="[
                'input_boolean',
                'light',
                'switch',
                'fan',
                'automation',
                'climate',
              ].includes(data.domain)
            "
    :checked="data.value === 'on'"
    @click="toggleClick"
  />
  <a-button
    v-else-if="[
                'script',
                'scene',
                'automation'
              ].includes(data.domain)"
    type="link"
    @click="triggerClick"
  >触发</a-button>
  <span v-else>
    {{ data.value }}
  </span>
</template>
<script>
export default {
  props: {
    data: {
      type: Object,
      default() {
        return {
          domain: "",
          value: "",
          entity_id: ""
        };
      }
    }
  },
  data() {
    return {};
  },
  inject: ["callService"],
  methods: {
    toggleClick() {
      this.$emit("toggle");
      const { value, domain, entity_id } = data;
      // 发送指令
      this.callService(`${domain}.turn_${value === "on" ? "off" : "on"}`, {
        entity_id
      });
      this.$message.success("切换成功");
    },
    triggerClick() {
      this.$emit("trigger");
      const { domain, entity_id } = data;
      if (domain === "script") {
        this.callService(entity_id);
      } else if (domain === "automation") {
        this.callService("automation.trigger", { entity_id });
      }
      this.$message.success("触发成功");
    }
  }
};
</script>

