<template>
  <a-card :title="data.text" size="small">
    <a-card-grid
      size="small"
      style="width: 25%; text-align: center"
      v-for="(item, index) in data.list"
      :key="index"
      @click="showClick(item)"
      >{{ item.name }}</a-card-grid
    >
  </a-card>
</template>
<script lang="ts">
import { defineComponent } from "vue";
export default defineComponent({
  props: {
    data: Object,
  },
  inject: ["callService"],
  methods: {
    showClick(item) {
      const { entity_id } = this.data;
      if (entity_id) {
        this.callService("media_player.play_media", {
          media_content_type: "video",
          media_content_id: item.value,
          entity_id,
        });
        this.$message.success(`正在播放${item.name}`);
      } else {
        this.$message.error(`请先设置播放器`);
      }
    },
  },
});
</script>
<style scoped>
.ant-card-grid {
  padding: 14px;
}
</style>