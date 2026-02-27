import './assets/main.css'
import "tailwindcss";

import Toast from "vue-toastification";
import "vue-toastification/dist/index.css";
import Vue3Toastify, { toast, type ToastContainerOptions } from 'vue3-toastify';

// import { createYmaps } from 'vue-yandex-maps';

import App from './App.vue'
import router from './router'
import { createApp } from 'vue'
import { createPinia } from 'pinia'

const app = createApp(App)

app
.use(Vue3Toastify, {
  autoclose: 3000,
  position: toast.POSITION.BOTTOM_RIGHT
} as ToastContainerOptions)
  .use(router)
  .use(Toast)
  .use(createPinia())
  // .use(createYmaps({
  //   apikey: '3f8f0af1-723b-47db-b868-be798083bba6',
  // }));

app.mount('#app')
