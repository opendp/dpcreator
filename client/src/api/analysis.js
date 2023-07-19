import {wrappedSession} from './session';
import caseConversion from "@/shared/caseConversion";


const camelcaseKeys = require('camelcase-keys');

export default {


    /**
     *  Updates a DepositSetupInfo object with the properties
     * @param objectId DepositorSetupInfo identifier
     * @param props  the new values to be saved (json object)
     * @returns {Promise<AxiosResponse<any>>} the updated object
     */
    patchDepositorSetup(objectId, props) {
        if (props.userStep) {
            props.wizardStep = props.userStep
        }
        const snakeProps = caseConversion.customSnakecaseKeys(props)
        return wrappedSession.patch('/api/deposit/' + objectId + '/',
            snakeProps).then(resp => {
                 resp.data.wizard_step = resp.data.user_step
                camelcaseKeys(resp.data, {deep: true})
            })

    },
    getHistogramBuckets(min, max, numberOfBins) {
        return wrappedSession.post('/api/stat-helper/make-edges-integer/',
            {min: min, max: max, number_of_bins: numberOfBins})
            .then(resp => camelcaseKeys(resp.data, {deep: true}))
    },
    // For analysisPlan, we need to add new params to API
    /*
    {
  "object_id": "bbc5bd52-7c1e-4cf2-9938-28fd4745b5b1",
  "analyst_id": "0681867b-1ce8-46c9-adfb-df83b8efff24",
  "name": "Teacher survey plan",
  "description": "Release DP Statistics for the teacher survey, version 1",
  "epsilon": 0.25,
  "expiration_date": "2023-07-23"
}
     */
    createAnalysisPlan(datasetId, analystId, budget,description, name, expirationDate) {
        console.log('budget: ' + budget)
        const params = {object_id: datasetId,
            analyst_id: analystId,
            name: name,
            epsilon: budget,
            expiration_date: expirationDate,
            description: description

        }
        console.log('posting to analysis plan, params = '+JSON.stringify(params))
        return wrappedSession.post('/api/analysis-plan/',
            params)
            .then(resp => camelcaseKeys(resp.data, {deep: true}))
    },
    getUserAnalysisPlans() {
        return wrappedSession.get('/api/analyze/')
           /* .then(resp => {

                if (resp.data.results) {
                    const modifiedResults = resp.data.results.map((obj) => {
                        // copy wizard_step into user_step
                        obj.depositor_setup_info.user_step = obj.depositor_setup_info.wizard_step;
                        console.log('setting status to ' + obj.depositor_setup_info.wizard_step)
                        obj.status = obj.depositor_setup_info.wizard_step;
                        return obj;
                    });
                    resp.data.results = modifiedResults
                }
                return resp;
            }) */
            .then(resp => camelcaseKeys(resp, {deep: true}))

    },
    getAnalysisPlan(analysisId) {
        return wrappedSession.get('/api/analyze/' + analysisId + '/')
            .then(resp => camelcaseKeys(resp.data, {deep: true}))
    },
    patchAnalysisPlan(objectId, props) {
        const snakeProps = caseConversion.customSnakecaseKeys(props)
        return wrappedSession.patch('/api/analyze/' + objectId + '/',
            snakeProps)
    },
    deleteAnalysisPlan(analysisId) {
        return wrappedSession.delete('/api/analyze/' + analysisId + '/')
    }

};
