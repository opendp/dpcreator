import Vue, {createApp} from "vue";
import App from "./App.vue";
import router from "./router";
import axios from 'axios'
import GSignInButton from 'vue-google-signin-button'
import vuetify from "./plugins/vuetify";
import JsonViewer from 'vue-json-viewer'
import VTooltip from 'v-tooltip'
import { createStore } from "vuex";
// Create a new store instance or import from module.
const store = createStore({
    /* state, actions, mutations */
});
//Vue.use(VTooltip)
Vue.use(JsonViewer)
Vue.config.productionTip = false;
Vue.use(GSignInButton)
axios.defaults.xsrfHeaderName = 'X-CSRFToken';
axios.defaults.xsrfCookieName = 'csrftoken';
import VueWaypoint from "vue-waypoint";

Vue.use(VueWaypoint);

import titleMixin from './mixins/titleMixin'
import i18n from './i18n'

Vue.mixin(titleMixin)
/*
const app = new Vue({
  router,
  store,
  vuetify,
  i18n,
  render: h => h(App)
}).$mount("#app");
*/
createApp(App)
    .use(router)
    .use(store)
  //  .use(VTooltip)
    .use(vuetify)
    .use(i18n)
    .use(JsonViewer)
    .use(GSignInButton)
    .mount('#app')
window.app = app
