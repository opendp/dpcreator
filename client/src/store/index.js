import Vue from 'vue';
import Vuex from 'vuex';
import createLogger from 'vuex/dist/logger';
import createPersistedState from 'vuex-persistedstate';

import auth from './auth';
import password from './password';
import signup from './signup';
import dataverse from './dataverse'
import dataset from './dataset'
const debug = process.env.NODE_ENV !== 'production';

Vue.use(Vuex);

export default new Vuex.Store({
  modules: {
    auth,
    password,
    signup,
    dataverse,
    dataset
  },
  strict: debug,
  plugins: debug ? [createLogger(), createPersistedState({storage: window.sessionStorage})] : [createPersistedState({storage: window.sessionStorage})],
});
