import session from './session';

const camelcaseKeys = require('camelcase-keys');
const snakecaseKeys = require('snakecase-keys');


export default {

    validate(analysisPlanId, dpStatistics) {
        // TODO: Update AddStatisticDialog so that it has separate Label/values to handle this
        dpStatistics.forEach((item) => {
            if (item['missingValuesHandling'] === 'Drop them') {
                item['missingValuesHandling'] = 'drop'
            }
            if (item['missingValuesHandling'] === 'Insert random value') {
                item['missingValuesHandling'] = 'insert_random'
            }
            if (item['missingValuesHandling'] === 'Insert fixed value') {
                item['missingValuesHandling'] = 'insert_fixed'
            }
            item['statistic'] = item['statistic'].toLowerCase()
        })
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
