import auth from '../api/auth';
import session from '../api/session';
import {
  LOGIN_BEGIN,
  LOGIN_FAILURE,
  LOGIN_SUCCESS,
  LOGOUT,
  REMOVE_TOKEN, SET_CURRENT_TERMS, SET_TERMS_ACCEPTED, SET_TERMS_LOG,
  SET_TOKEN,
  SET_USER,
} from './types';
import terms from "@/api/terms";

const TOKEN_STORAGE_KEY = 'TOKEN_STORAGE_KEY';
const isProduction = process.env.NODE_ENV === 'production';

const initialState = {
  authenticating: false,
  error: false,
  token: null,
  user: null,
  currentTerms: null,
  termsOfAccessLog: null

};

const getters = {
  isAuthenticated: state => !!state.token,
  isTermsAccepted: state => {
    const retVal = (state.user !== null
        && state.termsOfAccessLog !== null
        && state.termsOfAccessLog.filter(
            function (obj) {
              return obj.objectId === state.currentTerms.objectId;
            }) !== null)
    console.log('returning ' + retVal)
    return retVal
  },
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
  setCurrentTerms({commit, state}) {
    return terms.getCurrentTerms().then((response) => {
      commit('SET_CURRENT_TERMS', response)
    })
  },
  setTermsLog({commit, state}, openDPUserId) {
    return terms.getTermsOfUseLog(openDPUserId).then(response =>
        commit(SET_TERMS_LOG, response))
  },
  acceptTerms({commit, state}, {user, termsOfAccess}) {
    terms.acceptTermsOfUse(user, termsOfAccess).then(console.log('updated terms'))
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
  [SET_CURRENT_TERMS](state, currentTerms) {
    state.currentTerms = currentTerms
  },
  [SET_TERMS_LOG](state, termsLog) {
    state.termsOfAccessLog = termsLog
  }
};

export default {
  namespaced: true,
  state: initialState,
  getters,
  actions,
  mutations,
};
