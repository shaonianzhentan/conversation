<template>
  <a-card :title="data.cmd">
    <a-list bordered>
      <a-list-item v-for="(item, index) in data.list" :key="index"
        >{{ item.name }}
        <template #actions>
          {{ item.value }}
        </template>
      </a-list-item>
    </a-list>
  </a-card>
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
          list: [],
        };
      },
    },
  },
  setup() {
    const checked = ref(false);
    return {
      checked,
    };
  },
});
</script>
