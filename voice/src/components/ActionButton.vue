<template>
  <a-switch
    v-if="data.isAction && [
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
    v-else-if="data.isAction && [
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
          entity_id: "",
          isAction: false
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
      const { value, domain, entity_id } = this.data;
      // 发送指令
      this.callService(`${domain}.turn_${value === "on" ? "off" : "on"}`, {
        entity_id
      });
      this.$message.success("切换成功");
      this.$emit("toggle");
    },
    triggerClick() {
      const { domain, entity_id } = this.data;
      if (domain === "script") {
        this.callService(entity_id);
      } else if (domain === "automation") {
        this.callService("automation.trigger", { entity_id });
      }
      this.$message.success("触发成功");
      this.$emit("trigger");
    }
  }
};
</script>

