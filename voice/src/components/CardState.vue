<template>
  <template v-if="entity">
    <div
      v-if="entity.domain === 'media_player'"
      style="text-align: center;"
    >
      <a-space>
        <a-button
          type="primary"
          @click="musicEvent({service:'media_previous_track'})"
        >上一曲</a-button>
        <a-button
          type="primary"
          @click="musicEvent({service:'media_play_pause'})"
        >播放/暂停</a-button>
        <a-button
          type="primary"
          @click="musicEvent({service:'media_next_track'})"
        >下一曲</a-button>
      </a-space>
      <a-slider
        v-model:value="entity.volume_level"
        @afterChange="musicEvent({service:'volume_set'})"
      />
    </div>
  </template>
  <a-list bordered>
    <a-list-item
      v-for="(item, index) in list"
      :key="index"
    >{{ item.name }}
      <template #actions>
        <ActionButton
          :data="item"
          @toggle="toggleClick(item)"
        />
      </template>
    </a-list-item>
  </a-list>
</template>
<script lang="ts">
import { defineComponent, ref } from "vue";
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
      list: [],
      entity: null
    };
  },
  inject: ["callService"],
  async mounted() {
    const entity_list = this.data.list;
    this.list = await this.load({ entity_list });
    if (entity_list.length === 1) {
      const domain = entity_list[0].split(".")[0];
      if (domain === "media_player") {
        this.entity = {
          domain,
          entity_id: entity_list[0],
          volume_level:
            this.list.find(ele => ele.name === "volume_level").value * 100
        };
      }
    }
  },
  methods: {
    toggleClick(item) {
      item.value = item.value === "on" ? "off" : "on";
    },
    musicEvent({ service }) {
      const { entity_id, volume_level } = this.entity;
      let data = { entity_id };
      if (service === "volume_set") {
        data["volume_level"] = volume_level / 100;
      }
      this.callService(`media_player.${service}`, data);
      this.$message.success("操作成功");
    }
  }
});
</script>
