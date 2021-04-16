<template>
  <a-card title="我想看司藤" size="small">
    <a-card title="获取所有状态值">
      <a-card-grid style="width: 25%; text-align: center">第一集</a-card-grid>
      <a-card-grid style="width: 25%; text-align: center">第二集</a-card-grid>
      <a-card-grid style="width: 25%; text-align: center">第一集</a-card-grid>
      <a-card-grid style="width: 25%; text-align: center">第一集</a-card-grid>
      <a-card-grid style="width: 25%; text-align: center">第一集</a-card-grid>
      <a-card-grid style="width: 25%; text-align: center">第一集</a-card-grid>
      <a-card-grid style="width: 25%; text-align: center">第一集</a-card-grid>
      <a-card-grid style="width: 25%; text-align: center">第一集</a-card-grid>
    </a-card>
  </a-card>
</template>
<script lang="ts">
import { defineComponent } from "vue";
export default defineComponent({
  props: {
    data: Object,
  },
});
</script>