import {session, wrappedSession} from './session';

const camelcaseKeys = require('camelcase-keys');

export default {
    getBannerMessages() {
        return wrappedSession.get('/api/banner-messages/').then(data => camelcaseKeys(data, {deep: true}));

    },
    changePassword(old_password, new_password1, new_password2) {
        return session.post('/rest-auth/password/change/', {new_password1, new_password2, old_password})
            .catch(function (data) {
                if (data.response) {
                    if (data.response.status == 400) {
                        return Promise.reject(data.response.data);
                    } else {
                        throw(data.response)
                    }
                }
            });
    },
    login(username, password) {
        return session.post('/rest-auth/login/', {username, password})
            .then(data => camelcaseKeys(data, {deep: true}))
            .catch(function (data) {
                if (data.response) {
                    if (data.response.status == 400) {
                        return Promise.reject(data.response.data);
                    } else {
                        throw(data.response)
                    }
                }
        });
  },
  googleLogin(access_token) {
      return wrappedSession.post('/rest-auth/google/', {'access_token': access_token});
  },
  logout() {
      return wrappedSession.post('/rest-auth/logout/', {});
  },
  createAccount(username, password1, password2, email) {
      return session.post('/rest-auth/registration/', {username, password1, password2, email})
          .catch(function (data) {
              if (data.response) {
                  if (data.response.status == 400) {
                      return Promise.reject(data.response.data);
                  } else {
                      throw(data.response)
                  }
              }
          });
  },
  sendAccountPasswordResetEmail(email) {
      return session.post('/rest-auth/password/reset/', {email})
          .catch(function (data) {
              if (data.response) {
                  if (data.response.status == 400) {
                      return Promise.reject(data.response.data);
                  } else {
                      throw(data.response)
                  }
              }
          });
  },
  resetAccountPassword(uid, token, new_password1, new_password2) { // eslint-disable-line camelcase
      return session.post('/rest-auth/password/reset/confirm/', {uid, token, new_password1, new_password2})
          .catch(function (data) {
              if (data.response) {
                  if (data.response.status == 400) {
                      return Promise.reject(data.response.data);
                  } else {
                      throw(data.response)
                  }
              }
          });
  },
  getAccountDetails() {
      return wrappedSession.get('/rest-auth/user/').then(data => camelcaseKeys(data, {deep: true}));
  },
  updateAccountDetails(data) {
      return wrappedSession.patch('/rest-auth/user/', data);
  },
  verifyAccountEmail(key) {
      return wrappedSession.post('/rest-auth/registration/verify-email/', {key});
  },
};
