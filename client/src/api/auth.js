import session from './session';
const camelcaseKeys = require('camelcase-keys');

export default {
    changePassword(old_password, new_password1, new_password2) {
        session.post('/rest-auth/password/change/', {new_password1, new_password2, old_password})
            .catch(function (data) {
                if (data.response) {
                    if (data.response.status == 400) {
                        return Promise.reject(data.response.data);
                    }
                } else if (data.request) {
                    // The request was made but no response was received
                    console.log('no response' + data.request);
                } else {
                    // Something happened in setting up the request that triggered an Error
                    console.log('Error', data.message);
                }

            })
    },
    login(username, password) {
        return session.post('/rest-auth/login/', {username, password})
            .then(data => camelcaseKeys(data, {deep: true}))
            .catch(function (data) {
                if (data.response) {
                    if (data.response.status == 400) {
                        return Promise.reject(data.response.data);
                    }
                } else if (data.request) {
                    // The request was made but no response was received
            console.log('no response' + data.request);
          } else {
            // Something happened in setting up the request that triggered an Error
            console.log('Error', data.message);
          }

        });
  },
  googleLogin(access_token) {
    return session.post('/rest-auth/google/', {'access_token': access_token});
  },
  logout() {
    return session.post('/rest-auth/logout/', {});
  },
  createAccount(username, password1, password2, email) {
      return session.post('/rest-auth/registration/', {username, password1, password2, email})
          .catch(function (data) {
              if (data.response) {
                  if (data.response.status == 400) {
                      return Promise.reject(data.response.data);
                  }
              } else if (data.request) {
                  // The request was made but no response was received
                  console.log(data.request);
              } else {
                  // Something happened in setting up the request that triggered an Error
                  console.log('Error', data.message);
              }

          });
  },
  changeAccountPassword(password1, password2) {
      return session.post('/rest-auth/password/change/', {password1, password2});
  },
  sendAccountPasswordResetEmail(email) {
      return session.post('/rest-auth/password/reset/', {email});
  },
  resetAccountPassword(uid, token, new_password1, new_password2) { // eslint-disable-line camelcase
      return session.post('/rest-auth/password/reset/confirm/', {uid, token, new_password1, new_password2})
          .catch(function (data) {
              if (data.response) {
                  if (data.response.status == 400) {
                      return Promise.reject(data.response.data);
                  }
              } else if (data.request) {
                  // The request was made but no response was received
                  console.log(data.request);
              } else {
                  // Something happened in setting up the request that triggered an Error
                  console.log('Error', data.message);
              }

          });
  },
  getAccountDetails() {
      return session.get('/rest-auth/user/').then(data => camelcaseKeys(data, {deep: true}));
  },
  updateAccountDetails(data) {
    return session.patch('/rest-auth/user/', data);
  },
  verifyAccountEmail(key) {
      return session.post('/registration/verify-email/', {key});
  },
};
