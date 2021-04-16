<template>
  <a-comment>
    <template #author><a>HomeAssistant</a></template>
    <template #avatar>
      <a-avatar
        src="https://www.home-assistant.io/images/home-assistant-logo.svg"
        alt="HomeAssistant"
      />
    </template>
    <template #content>
      <p>{{ data.text }}</p>
    </template>
  </a-comment>
</template>


<script>
import { defineComponent } from "vue";
export default defineComponent({
  props: {
    data: {
      type: Object,
      default() {
        return {
          cmd: "",
          text: ""
        };
      }
    }
  }
});
</script>