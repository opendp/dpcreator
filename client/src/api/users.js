import {wrappedSession} from './session';

const camelcaseKeys = require('camelcase-keys');



export default {
    /**
     * Gets a list of datasets that belong to the currently logged in user
     *
     */
    getUsers() {
        return wrappedSession.get('/api/users/')
            .then(resp => {console.log(JSON.stringify(resp)); return resp})
            .then(resp => {
                resp = camelcaseKeys(resp, {deep: true});
                console.log('returning: ' + JSON.stringify(resp))
                return resp;})

    },


}