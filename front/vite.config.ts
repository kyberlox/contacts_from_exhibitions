import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import tailwindcss from '@tailwindcss/vite'
import svgLoader from 'vite-svg-loader'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
    tailwindcss(),
    svgLoader()
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  // server: {
  //   host: "0.0.0.0",
  //   port: 4173,
  //   proxy: {
  //     '': {
  //       target: 'http://exhibitions.kyberlox.ru/',
  //       changeOrigin: true,
  //       secure: false
  //     }
  //   }
  // },
  // preview: {
  //   allowedHosts: ['meeting.mosckba.ru']
  // },

  css: {
    preprocessorOptions: {
      scss: {
        api: 'modern-compiler',
      }
    }
  },
})
