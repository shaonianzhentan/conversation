<template>
  <a-card title="我想看司藤">
    <a-list bordered>
      <a-list-item>测试</a-list-item>
      <a-list-item
        >测试
        <template #actions> 10 </template>
      </a-list-item>
      <a-list-item
        >测试
        <template #actions>
          <a-switch v-model:checked="checked" />
        </template>
      </a-list-item>
    </a-list>
  </a-card>
</template>
<script lang="ts">
import { defineComponent, ref } from "vue";

export default defineComponent({
  props: {
    data: {},
  },
  setup() {
    const checked = ref(false);
    return {
      checked,
    };
  },
});
</script>
