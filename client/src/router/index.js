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
    path: "/",
    name: "Home",
    component: () => import("../views/Home.vue")
  },
  {
    path: "/wizard",
    name: "Wizard",
    component: () => import("../views/Wizard.vue")
  },
  {
    path: "/my-data",
    name: "MyData",
    component: () => import("../views/MyData.vue")
  },
  {
    path: "/my-data/:id",
    name: "MyDataDetails",
    component: () => import("../views/MyDataDetails.vue")
  },
  {
    path: "/sign-up",
    name: "SignUp",
    component: () => import("../views/SignUp.vue")
  },
  {
    path: "/sign-up/confirmation",
    name: "SignUpConfirmation",
    component: () => import("../views/SignUpConfirmation.vue")
  },
  {
    path: "/log-in",
    name: "LogIn",
    component: () => import("../views/LogIn.vue")
  },
  {
    path: "/forgot-your-password",
    name: "ForgotYourPassword",
    component: () => import("../views/ForgotYourPassword.vue")
  },
  {
    path: "/welcome",
    name: "Welcome",
    component: () => import("../views/Welcome.vue")
  },
  {
    path: "/terms-and-conditions",
    name: "TermsAndConditions",
    component: () => import("../views/TermsAndConditions.vue")
  },
  {
    path: "/contact-us",
    name: "ContactUs",
    component: () => import("../views/ContactUs.vue")
  },
  {
    path: "/my-profile",
    name: "MyProfile",
    component: () => import("../views/MyProfile.vue")
  },
  {
    path: "*",
    name: "404",
    component: () => import("../views/404.vue")
  },
  //
  // Old Routes
  //

]

const router = new VueRouter({
  mode: 'history',
  //base: process.env.BASE_URL,
  routes
})

router.afterEach(() => {
  window.scrollTo(0, 0);
});

export default router
