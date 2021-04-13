import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from '../views/old/OldHome.vue'
import Login from '../views/old/Login.vue'
import Lost from '../views/old/Lost.vue'
import PasswordReset from "../views/old/PasswordReset"
import PasswordResetConfirm from "../views/old/PasswordResetConfirm"
import Register from "../views/old/Register"
import VerifyEmail from "../views/old/VerifyEmail"
import store from '../store'
import OldHome from "@/views/old/OldHome";

const redirectLogout = (to, from, next) => {
  store.dispatch('auth/logout')
      .then(() => next('/login'));
};

Vue.use(VueRouter)

const routes = [
  {
    path: '/old',
    name: 'Home',
    component: OldHome
  },
  {
    path: '/about',
    name: 'About',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: function () {
      return import(/* webpackChunkName: "about" */ '../views/old/About.vue')
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
