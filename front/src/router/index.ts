import { createRouter, createWebHistory } from 'vue-router'
import ContactForm from '@/views/contactForm/ContactForm.vue'
import EventsPage from '@/views/admin/EventsPage.vue'
import ContacsPage from '@/views/admin/ContacsPage.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'contact',
      component: ContactForm,
    },
    {
      path: '/events',
      name: 'events',
      component: EventsPage
    },
    {
      path: '/events/:id/contacts',
      name: 'contactPage',
      component: ContacsPage,
      props: (route) => ({ id: Number(route.params.id) }),
    },
    {
      path: '/contact/:id?',
      name: 'contactEdit',
      component: ContactForm,
      props: (route) => ({ id: (route.params.id) }),
    }
  ],
})

export default router
