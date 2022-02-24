import auth from '../api/auth';

import {
  PASSWORD_RESET_BEGIN,
  PASSWORD_RESET_CLEAR,
  PASSWORD_RESET_FAILURE,
  PASSWORD_RESET_SUCCESS,
  PASSWORD_CHANGE_BEGIN,
  PASSWORD_CHANGE_CLEAR,
  PASSWORD_CHANGE_FAILURE,
  PASSWORD_CHANGE_SUCCESS,
  PASSWORD_EMAIL_BEGIN,
  PASSWORD_EMAIL_CLEAR,
  PASSWORD_EMAIL_FAILURE,
  PASSWORD_EMAIL_SUCCESS,
} from './types';

export default {
  namespaced: true,
  state: {
    emailCompleted: false,
    emailError: false,
    emailLoading: false,
    resetCompleted: false,
    resetError: false,
    resetLoading: false,
    changeCompleted: false,
    changeError: false,
    changeLoading: false,
  },
  actions: {
    resetPassword({commit}, {uid, token, password1, password2}) {
      commit(PASSWORD_RESET_BEGIN);
      return auth.resetAccountPassword(uid, token, password1, password2)
          .then(() => commit(PASSWORD_RESET_SUCCESS))
          .catch((data) => {
            commit(PASSWORD_RESET_FAILURE);
            return Promise.reject(data)
          });
    },
    changePassword({commit}, {oldPassword, password1, password2}) {
      commit(PASSWORD_CHANGE_BEGIN);
      return auth.changePassword(oldPassword, password1, password2)
          .then(() => commit(PASSWORD_CHANGE_SUCCESS))
          .catch((data) => {
            commit(PASSWORD_CHANGE_FAILURE);
            return Promise.reject(data)
          });
    },
    sendPasswordResetEmail({commit}, {email}) {
      commit(PASSWORD_EMAIL_BEGIN);
      return auth.sendAccountPasswordResetEmail(email)
          .then(() => commit(PASSWORD_EMAIL_SUCCESS))
          .catch(() => commit(PASSWORD_EMAIL_FAILURE));
    },
    clearResetStatus({commit}) {
      commit(PASSWORD_RESET_CLEAR);
    },
    clearEmailStatus({commit}) {
      commit(PASSWORD_EMAIL_CLEAR);
    },
    clearPasswordStatus({commit}) {
      commit(PASSWORD_CHANGE_CLEAR);
    },
  },
  mutations: {
    [PASSWORD_RESET_BEGIN](state) {
      state.resetLoading = true;
    },
    [PASSWORD_RESET_CLEAR](state) {
      state.resetCompleted = false;
      state.resetError = false;
      state.resetLoading = false;
    },
    [PASSWORD_CHANGE_CLEAR](state) {
      state.changeCompleted = false;
      state.changeError = false;
      state.changeLoading = false;
    },
    [PASSWORD_CHANGE_FAILURE](state) {
      state.changeError = true;
      state.changeLoading = false;
    },
    [PASSWORD_CHANGE_SUCCESS](state) {
      state.changeCompleted = true;
      state.changeError = false;
      state.changeLoading = false;
    },
    [PASSWORD_RESET_FAILURE](state) {
      state.resetError = true;
      state.resetLoading = false;
    },
    [PASSWORD_RESET_SUCCESS](state) {
      state.resetCompleted = true;
      state.resetError = false;
      state.resetLoading = false;
    },
    [PASSWORD_EMAIL_BEGIN](state) {
      state.emailLoading = true;
    },
    [PASSWORD_EMAIL_CLEAR](state) {
      state.emailCompleted = false;
      state.emailError = false;
      state.emailLoading = false;
    },
    [PASSWORD_EMAIL_FAILURE](state) {
      state.emailError = true;
      state.emailLoading = false;
    },
    [PASSWORD_EMAIL_SUCCESS](state) {
      state.emailCompleted = true;
      state.emailError = false;
      state.emailLoading = false;
    },
  },
};
