import {wrappedSession} from './session';

const camelcaseKeys = require('camelcase-keys');



export default {
    /**
     * Gets a list of datasets that belong to the currently logged in user
     *
     */
    getUsers() {
        return wrappedSession.get('/api/users/')
            .then(resp => { return resp})
            .then(resp => {
                resp = camelcaseKeys(resp, {deep: true});
                return resp;})

    },


}