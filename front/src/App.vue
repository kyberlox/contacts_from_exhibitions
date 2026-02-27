<template>
<div class="grid grid-rows-[auto_1fr_auto] min-h-screen overflow-scroll">
  <HeaderV />
  <main>
    <RouterView />
  </main>
  <!-- <FooterV /> -->
</div>
</template>

<script lang="ts">
import HeaderV from "@/components/LayoutHeader.vue";
import { defineComponent, onMounted } from 'vue';
// import Api from "./utils/Api";

export default defineComponent({
  components: {
    HeaderV,
  },
  setup() {

    // onMounted(() => {
    //   const postBody = { "id": "1", "fio": { "last_name": "Иванов", "first_name": "Иван", "middle_name": "Иванович" }, "department": "Отдел продаж", "position": "Менеджер", "session_id": "session_token_123" }

    //   Api.post('login', postBody)
    // })

    return {

    }
  }
})
</script>