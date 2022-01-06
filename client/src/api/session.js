import axios from 'axios';

const CSRF_COOKIE_NAME = 'csrftoken';
const CSRF_HEADER_NAME = 'X-CSRFToken';

// Keep the original session for api calls that need to do their own error handling
const session = axios.create({
    xsrfCookieName: CSRF_COOKIE_NAME,
    xsrfHeaderName: CSRF_HEADER_NAME,
});
const wrappedSession = axios.create({
    xsrfCookieName: CSRF_COOKIE_NAME,
    xsrfHeaderName: CSRF_HEADER_NAME,
});

// Add a second version of session that includes response interceptor
wrappedSession.interceptors.response.use(function (response) {
    // Any status code that lie within the range of 2xx cause this function to trigger
    // Do something with response data
    return response;
}, function (error) {
    // Any status codes that falls outside the range of 2xx cause this function to trigger
    // Do something with response error
    console.log('interceptor response error: ' + error)
    console.log('interceptor response status: ' + error.response.status)

    // throw the response that will be caught by the general error handler in App.vue
    throw(error.response)

    return Promise.reject(error);

});


export {session, wrappedSession};