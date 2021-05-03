import Vue from "vue";
import Vuetify from "vuetify/lib/framework";

import settings from "../settings";

const themes = settings.colors.vuetify_themes;

Vue.use(Vuetify);

export default new Vuetify({
  theme: {
    options: {
      customProperties: true
    },
    themes
  }
});
