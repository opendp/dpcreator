import session from './session';
import axios from "axios";
const camelcaseKeys = require('camelcase-keys');

export default {

    /**
     * Get the most recent terms of use
     */
    getCurrentTerms() {
        // This will return a list of termsOfAccess, ordered by creation time.
        // We return the first element of the list as the current one
        return session.get('/api/terms-of-access/')
            .then(resp => {
                return camelcaseKeys(resp.data, {deep: true}).results[0]

            })

    },
    /*
     * Returns a history of agreed Terms of Access for this user
     * @returns {Promise<<any>>}
     */
    getTermsOfUseLog() {
        return axios.get('/api/terms-of-access-agreement/')
            .catch(resp => {
                if (resp.response.status === 404) {
                    // 404 error means that this user hasn't agreed to any terms yet, so
                    // just return an empty list
                    return []
                }
            }).then(resp => {
                return camelcaseKeys(resp.data.results, {deep: true})

            })
    },
    /**
     * Inserts a row in the termsOfUseAccessLog table, to record user acceptance
     */
    acceptTermsOfUse(user, termsOfAccess) {
        console.log('api user:' + user)
        console.log('api terms:' + termsOfAccess)
        return session.post('/api/terms-of-access-agreement/', {user: user, terms_of_access: termsOfAccess})
    }
}