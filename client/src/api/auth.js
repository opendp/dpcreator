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
    return session.post('/dj_rest_auth/registration/', { username, password1, password2, email });
  },
  changeAccountPassword(password1, password2) {
    return session.post('/auth/password/change/', { password1, password2 });
  },
  sendAccountPasswordResetEmail(email) {
    return session.post('/auth/password/reset/', { email });
  },
  resetAccountPassword(uid, token, new_password1, new_password2) { // eslint-disable-line camelcase
    return session.post('/auth/password/reset/confirm/', { uid, token, new_password1, new_password2 });
  },
  getAccountDetails() {
    return session.get('/rest-auth/user/');
  },
  updateAccountDetails(data) {
    return session.patch('/auth/user/', data);
  },
  verifyAccountEmail(key) {
    return session.post('/registration/verify-email/', { key });
  },
};
