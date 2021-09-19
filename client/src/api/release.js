import session from './session';

const camelcaseKeys = require('camelcase-keys');
const snakecaseKeys = require('snakecase-keys');


export default {
    generateRelease(analysisPlanId) {
        return session.post('/api/release/',
            {object_id: analysisPlanId})
            .then(resp => {
                camelcaseKeys(resp.data, {deep: true})
                console.log("generate release API, received response: " + JSON.stringify(resp))
            })


    },
    validate(analysisPlanId, dpStatistics) {

        dpStatistics = snakecaseKeys(dpStatistics, {deep: true})
        console.log(JSON.stringify(dpStatistics));


        return session.post('/api/validation/',
                 {analysis_plan_id: analysisPlanId, dp_statistics: dpStatistics})
                 .then(resp => camelcaseKeys(resp.data, {deep: true}))


        // Return an object with valid:true for each statistic, to mimic the API
        /*    let resp = {}
            resp['valid'] = []
            dpStatistics.forEach((item) => {
                resp['valid'].push({"valid": true})
            })
            const myPromise = new Promise((resolve, reject) => {
                resolve(resp);
            });
            return myPromise
            */

    },

};
