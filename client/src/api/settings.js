import {wrappedSession} from './session';

export default {

    // Gets the runtime environment variables needed in Vue
    getVueSettings() {
        return wrappedSession.get('/api/vue-settings/')
    },

};
