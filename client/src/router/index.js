import Vue from "vue";
import VueRouter from "vue-router";
import Home from "../views/Home.vue";
import store from "../store/index"
import NETWORK_CONSTANTS from "./NETWORK_CONSTANTS";

const {
  HOME,
  WELCOME,
  MY_DATA,
  MY_DATA_DETAILS,
  WIZARD,
  SIGN_UP,
  LOGIN,
  CONTACT_US,
  MY_PROFILE,
  MOCK_DV,
  MORE_INFORMATION,
  TERMS_AND_CONDITIONS,
  FORGOT_YOUR_PASSWORD
} = NETWORK_CONSTANTS;

Vue.use(VueRouter);

const routes = [
  {
    path: HOME.PATH,
    name: HOME.NAME,
    component: Home
  },
  {
    path: `${WIZARD.PATH}/`,
    name: WIZARD.NAME,
    // dynamic segments start with a colon
    component: () => import("../views/Wizard.vue"),
    meta: {
      requiresAuth: true
    }
  },

  {
    path: MY_DATA.PATH,
    name: MY_DATA.NAME,
    component: () => import("../views/MyData.vue"),
    meta: {
      requiresAuth: true
    }
  },
  {
    path: `${MY_DATA_DETAILS.PATH}`,
    name: "MyDataDetails",
    component: () => import("../views/MyDataDetails.vue"),
    meta: {
      requiresAuth: true
    }
  },
  {
    path: SIGN_UP.PATH,
    name: SIGN_UP.NAME,
    component: () => import("../views/SignUp.vue")
  },
  {
    path: `${SIGN_UP.PATH}/confirmation`,
    name: "SignUpConfirmation",
    component: () => import("../views/SignUpConfirmation.vue")
  },
  {
    path: LOGIN.PATH,
    name: LOGIN.NAME,
    component: () => import("../views/LogIn.vue")
  },
  {
    path: FORGOT_YOUR_PASSWORD.PATH,
    name: FORGOT_YOUR_PASSWORD.NAME,
    component: () => import("../views/ForgotYourPassword.vue")
  },
  {
    path: WELCOME.PATH,
    name: WELCOME.NAME,
    component: () => import("../views/Welcome.vue"),
    meta: {
      requiresAuth: true
    }
  },
  {
    path: TERMS_AND_CONDITIONS.PATH,
    name: TERMS_AND_CONDITIONS.NAME,
    component: () => import("../views/TermsAndConditions.vue")
  },
  {
    path: CONTACT_US.PATH,
    name: CONTACT_US.NAME,
    component: () => import("../views/ContactUs.vue")
  },
  {
    path: MY_PROFILE.PATH,
    name: MY_PROFILE.NAME,
    component: () => import("../views/MyProfile.vue"),
    meta: {
      requiresAuth: true
    }
  },
  {
    path: MOCK_DV.PATH,
    name: MOCK_DV.NAME,
    component: () => import("../views/MockDV.vue")
  },
  {
    path: MORE_INFORMATION.PATH,
    name: MORE_INFORMATION.NAME,
    component: () => import("../views/MoreInformation.vue")
  },
  {
    path: "*",
    name: "NotFoundPage",
    component: () => import("../views/NotFoundPage.vue")
  }
];

const router = new VueRouter({
  mode: "history",
  // base: process.env.BASE_URL,
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (to.hash) {
      return {
        selector: to.hash,
        behavior: 'smooth',
      }
    }
  }
});

router.beforeEach((to, from, next) => {
  if (to.matched.some(record => record.meta.requiresAuth)
      && store.state.auth.token == null) next({name: NETWORK_CONSTANTS.LOGIN.NAME})
  else next()
})
router.afterEach(() => {
  window.scrollTo(0, 0);
});

export default router;
