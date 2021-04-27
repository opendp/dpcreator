import Vue from "vue";
import App from "./App.vue";
import router from "./router";
import store from './store'
import axios from 'axios'
import GSignInButton from 'vue-google-signin-button'
import vuetify from "./plugins/vuetify";

Vue.config.productionTip = false;
Vue.use(GSignInButton)
axios.defaults.xsrfHeaderName = 'X-CSRFToken';
axios.defaults.xsrfCookieName = 'csrftoken';
import VueWaypoint from "vue-waypoint";

Vue.use(VueWaypoint);

import titleMixin from './mixins/titleMixin'

Vue.mixin(titleMixin)

new Vue({
  router,
  store,
  vuetify,
  render: h => h(App)
}).$mount("#app");
