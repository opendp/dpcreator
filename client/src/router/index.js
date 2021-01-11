import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import Lost from '../views/Lost.vue'
import PasswordReset from "../views/PasswordReset"
import PasswordResetConfirm from "../views/PasswordResetConfirm"
import Register from "../views/Register"
import VerifyEmail from "../views/VerifyEmail"
import store from '../store'

const redirectLogout = (to, from, next) => {
  store.dispatch('auth/logout')
    .then(() => next('/login'));
};

Vue.use(VueRouter)

  const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/about',
    name: 'About',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: function () {
      return import(/* webpackChunkName: "about" */ '../views/About.vue')
    }
  },
    {
      path: '/login',
      name: 'Login',
      component: Login
    },
    {
      path: '/logout',
      beforeEnter: redirectLogout,
    },
    {
      path: '/password_reset',
      component: PasswordReset,
    },
    {
      path: '/password_reset/:uid/:token',
      component: PasswordResetConfirm,
    },
    {
      path: '/register',
      component: Register,
    },
    {
      path: '/register/:key',
      component: VerifyEmail,
    },

]

const router = new VueRouter({
  mode: 'history',
  //base: process.env.BASE_URL,
  routes
})

export default router
