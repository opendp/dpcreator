import session from './session';

export default {
  login(username, password) {
    return session.post('/rest-auth/login/', { username, password });
  },
  googleLogin(access_token) {
    console.log('access passing token: '+ access_token)
    return session.post('/rest-auth/google/',{'access_token':access_token});
  },
  logout() {
    return session.post('/rest-auth/logout/', {});
  },
  createAccount(username, password1, password2, email) {
    return session.post('/rest-auth/registration/', { username, password1, password2, email })
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
    return session.post('/rest-auth/password/change/', { password1, password2 });
  },
  sendAccountPasswordResetEmail(email) {
    return session.post('/rest-auth/password/reset/', { email });
  },
  resetAccountPassword(uid, token, new_password1, new_password2) { // eslint-disable-line camelcase
    return session.post('/rest-auth/password/reset/confirm/', { uid, token, new_password1, new_password2 });
  },
  getAccountDetails() {
    return session.get('/rest-auth/user/');
  },
  updateAccountDetails(data) {
    return session.patch('/rest-auth/user/', data);
  },
  verifyAccountEmail(key) {
    return session.post('/registration/verify-email/', { key });
  },
};
