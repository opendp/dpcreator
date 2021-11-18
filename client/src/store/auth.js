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
  // Check to see if the user has accepted any terms at all.
  // (TermsAccepted will be false the first time the user logs in,
  // because the acceptance happened as the first step in Create Account.)
  isTermsAccepted: state => {
    let accepted = false
    if (state.termsOfAccessLog !== null && state.termsOfAccessLog.length > 0) {
      for (let i in state.termsOfAccessLog) {
        if (state.termsOfAccessLog[i].user === state.user.objectId) {
          accepted = true
        }
      }
    }
    return accepted
  },
  // Check if the user has accepted the most recent termsOfUse
  isCurrentTermsAccepted: state => {
    let accepted = false
    if (state.termsOfAccessLog !== null && state.termsOfAccessLog.length > 0) {
      for (let i in state.termsOfAccessLog) {
        if (state.termsOfAccessLog[i].user === state.user.objectId
            && state.termsOfAccessLog[i].termsOfAccess === state.currentTerms.objectId) {
          accepted = true
        }
      }
    }
    return accepted
  },
  getUser: state => {
    return state.user
  },
};


const actions = {
  changeUsername({commit, state}, newUsername) {
    let newUser = null;
    console.log('current user: ' + JSON.stringify(state.user))
    newUser = Object.assign({}, state.user)
    newUser.username = newUsername
    auth.updateAccountDetails(newUser)
        .then((data) => {
          console.log('resp: ' + JSON.stringify(data))
          commit(SET_USER, newUser)
        })

  },
  login({commit}, {username, password}) {
    commit(LOGIN_BEGIN);
    return auth.login(username, password)
        .then(({data}) => {
          commit(SET_TOKEN, data.key)
        })
        .then(() => commit(LOGIN_SUCCESS))
        .catch((data) => {
          commit(LOGIN_FAILURE);
          return Promise.reject(data)
        });
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
  fetchCurrentTerms({commit, state}) {
    return terms.getCurrentTerms().then((response) => {
      commit('SET_CURRENT_TERMS', response)
    })
  },
  fetchTermsLog({commit, state}) {
    return terms.getTermsOfUseLog().then(response => {
      commit(SET_TERMS_LOG, response)
    })
  },
  acceptTerms({commit, state}, {userId, termsOfAccessId}) {
    console.log("accepting terms ")
    terms.acceptTermsOfUse(userId, termsOfAccessId).then(console.log('updated terms'))
        .then(() => {
          terms.getTermsOfUseLog().then(response => {
            commit(SET_TERMS_LOG, response)
          })
        })
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
    state.currentTerms = null,
        state.termsOfAccessLog = null
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
  [SET_USER](state, user) {
    state.user = user;
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
