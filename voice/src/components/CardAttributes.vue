<template>
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
      list: []
    };
  },
  async mounted() {
    this.list = await this.load({ entity_list: this.data.list });
  },
  methods: {
    toggleClick(item) {
      item.value = item.value === "on" ? "off" : "on";
    }
  }
});
</script>
