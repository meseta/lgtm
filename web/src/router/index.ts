import Vue from 'vue'
import VueRouter, { RouteConfig } from 'vue-router'
import Home from '../views/Home.vue'
import store from '@/store'

Vue.use(VueRouter)

const routes: Array<RouteConfig> = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { title: 'LGTM' }
  },
  // {
  //   path: '/profile',
  //   name: 'Profile',
  //   component: Profile,
  //   meta: {
  //     title: 'LGTM Profile',
  //     requiresAuth: true,
  //   }
  // },
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})


// navigation guard, deal with setting title also
router.beforeEach((to, from, next) => {
  document.title = to.meta.title

  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)

  if (requiresAuth && !store.getters['auth/isAuthenticated']) {
    store.commit('alert/showError', 'Please log in');
    next('/');
  } else {
    next();
  }
})


export default router
