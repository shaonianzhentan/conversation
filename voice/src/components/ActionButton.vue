<template>
    <a-switch
        v-if="[
                'input_boolean',
                'light',
                'switch',
                'fan',
                'automation',
                'climate',
              ].includes(domain)
            "
        :checked="value === 'on'"
        @click="toggleClick"
    />
    <a-button
        v-else-if="[
                'script',
                'scene',
                'automation'
              ].includes(domain)"
        type="link"
        @click="triggerClick"
    >触发</a-button>
    <span v-else>
        {{ value }}
    </span>
</template>
<script>
export default {
  props: {
    domain: {},
    value: {}
  },
  data() {
    return {};
  },
  methods: {
    toggleClick() {
      this.$emit("toggle");
      this.$message.success("切换成功");
    },
    triggerClick() {
      this.$emit("trigger");
      this.$message.success("触发成功");
    }
  }
};
</script>

