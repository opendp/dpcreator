import auth from '../api/auth';
import session from '../api/session';
import {
  LOGIN_BEGIN,
  LOGIN_FAILURE,
  LOGIN_SUCCESS,
  LOGOUT,
  REMOVE_TOKEN, SET_TERMS_ACCEPTED,
  SET_TOKEN,
  SET_USER,
} from './types';

const TOKEN_STORAGE_KEY = 'TOKEN_STORAGE_KEY';
const isProduction = process.env.NODE_ENV === 'production';

const initialState = {
  authenticating: false,
  error: false,
  token: null,
  user: null,
  termsAccepted: false
};

const getters = {
  isAuthenticated: state => !!state.token,
  isTermsAccepted: state => state.termsAccepted,
  getUser: state => {
    return state.user
  },
};


const actions = {
  login({ commit }, { username, password }) {
    commit(LOGIN_BEGIN);
    return auth.login(username, password)
      .then(({ data }) => {
        commit(SET_TOKEN, data.key)
        commit(SET_USER, username)
      })
      .then(() => commit(LOGIN_SUCCESS))
      .catch((data) => {  commit(LOGIN_FAILURE); return Promise.reject(data)} );
  },
  googleLogin({commit}, token) {
    commit(LOGIN_BEGIN);
    return auth.googleLogin(token)
        .then(({data}) => {
          console.log('returned from googleLogin: ' + JSON.stringify(data))
          commit(SET_TOKEN, data.key)
          commit(LOGIN_SUCCESS);
          return Promise.resolve(data)
        })
        .catch((data) => {
          console.log(data);
          commit(LOGIN_FAILURE)
          return Promise.reject(data)
        });
  },
  logout({ commit }) {
    return auth.logout()
      .then(() => commit(LOGOUT))
      .finally(() => commit(REMOVE_TOKEN));
  },

  fetchUser({ commit,state }) {
    if (state.token!=null) {
      return auth.getAccountDetails()
          .then(response => {
            commit('SET_USER', response.data)
            return Promise.resolve()
          })
          .catch(error => {
            console.log('There was an error:', error.response)
            return Promise.reject(error)
          })
    } else {
      commit('SET_USER', null)
      return Promise.resolve()
    }
  },
  setTermsAccepted({commit, state}, termsAccepted) {
    commit('SET_TERMS_ACCEPTED', state, termsAccepted)
  },
  initialize({commit}) {
    const token = localStorage.getItem(TOKEN_STORAGE_KEY);

    if (isProduction && token) {
      commit(REMOVE_TOKEN);
    }

    if (!isProduction && token) {
      commit(SET_TOKEN, token);
    }
  },
};

const mutations = {
  [LOGIN_BEGIN](state) {
    state.authenticating = true;
    state.error = false;
  },
  [LOGIN_FAILURE](state) {
    state.authenticating = false;
    state.error = true;
  },
  [LOGIN_SUCCESS](state) {
    state.authenticating = false;
    state.error = false;
  },
  [LOGOUT](state) {
    state.authenticating = false;
    state.error = false;
    state.user = null;
  },
  [SET_TOKEN](state, token) {
    if (!isProduction) localStorage.setItem(TOKEN_STORAGE_KEY, token);
    session.defaults.headers.Authorization = `Token ${token}`;
    state.token = token;
  },
  [REMOVE_TOKEN](state) {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    delete session.defaults.headers.Authorization;
    state.token = null;
  },
  [SET_USER](state, username) {
    state.user = username;
  },
  [SET_TERMS_ACCEPTED](state, termsAccepted) {
    state.termsAccepted = termsAccepted;
  },
};

export default {
  namespaced: true,
  state: initialState,
  getters,
  actions,
  mutations,
};
