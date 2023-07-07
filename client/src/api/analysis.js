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
    createAnalysisPlan(datasetId, analystId, budget, name, expirationDate) {
        return wrappedSession.post('/api/analyze/',
            {object_id: datasetId, analyst_id: an})
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
