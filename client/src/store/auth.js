import auth from '../api/auth';
import {session} from '../api/session';
import {
  LOGIN_BEGIN,
  LOGIN_FAILURE,
  LOGIN_SUCCESS,
  LOGOUT,
  REMOVE_TOKEN, SET_CURRENT_TERMS, SET_TERMS_ACCEPTED, SET_TERMS_LOG,
  SET_TOKEN,
  SET_USER,
  SET_BANNER_MESSAGES,
  EDIT_USER_BEGIN,
  EDIT_USER_CLEAR,
  EDIT_USER_FAILURE,
  EDIT_USER_SUCCESS, PASSWORD_EMAIL_BEGIN, PASSWORD_EMAIL_CLEAR, PASSWORD_EMAIL_FAILURE, PASSWORD_EMAIL_SUCCESS
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
  termsOfAccessLog: null,
  bannerMessages: null,
  editUserCompleted: false,
  editUserError: false,
  editUserLoading: false,
};

const getters = {
  isAuthenticated: state => !!state.user,
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
    commit(EDIT_USER_BEGIN)
    let newUser = null;
    newUser = Object.assign({}, state.user)
    newUser.username = newUsername
    return auth.updateAccountDetails(newUser)
        .then((data) => {
          commit(SET_USER, newUser)
          commit(EDIT_USER_SUCCESS)
        }).catch((data) => {
          commit(EDIT_USER_FAILURE)
          return Promise.reject(data)
        })

  },
  clearEditUserStatus({commit}) {
    commit(EDIT_USER_CLEAR);
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
  logout({commit}) {
    return auth.logout()
        .then(() => commit(LOGOUT))
        .finally(() => commit(REMOVE_TOKEN));
  },
  fetchBannerMessages({commit}) {
    auth.getBannerMessages()
        .then(response => {
          commit(SET_BANNER_MESSAGES, response.data.results)
          Promise.resolve()
        })
  },
  fetchUser({commit, state}) {
    return auth.getAccountDetails()
        .then(response => {
          commit('SET_USER', response.data)
          return Promise.resolve()
        })
        .catch(error => {
          commit('SET_USER', null)
          return Promise.resolve()
        })
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
    terms.acceptTermsOfUse(userId, termsOfAccessId)
        .then(() => {
          terms.getTermsOfUseLog().then(response => {
            commit(SET_TERMS_LOG, response)
          })
        })
  },
  initializeState({commit}) {
    commit(LOGOUT)
  },
  initializeToken({commit}) {
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
        state.token = null,
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
  },
  [SET_BANNER_MESSAGES](state, bannerMessages) {
    state.bannerMessages = bannerMessages
  },
  [EDIT_USER_BEGIN](state) {
    state.editUserLoading = true;
  },
  [EDIT_USER_CLEAR](state) {
    state.editUserCompleted = false;
    state.editUserError = false;
    state.editUserLoading = false;
  },
  [EDIT_USER_FAILURE](state) {
    state.editUserError = true;
    state.editUserLoading = false;
  },
  [EDIT_USER_SUCCESS](state) {
    state.editUserCompleted = true;
    state.editUserError = false;
    state.editUserLoading = false;
  },
};

export default {
  namespaced: true,
  state: initialState,
  getters,
  actions,
  mutations,
};
