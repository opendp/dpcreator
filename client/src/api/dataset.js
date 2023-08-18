import {wrappedSession} from './session';

const camelcaseKeys = require('camelcase-keys');

function convertWizardStep(resp) {
    // convert the wizard_step stored in the server side back to user_step
    if (resp.data.depositor_setup_info) {
        resp.data.depositor_setup_info.user_step = resp.data.depositor_setup_info.wizard_step;
        resp.data.status = resp.data.depositor_setup_info.wizard_step;
    }


    resp.data.analysis_plans.forEach(plan => {
        plan.user_step = plan.wizard_step
    })

    // Return the modified resp object
    return resp;
}


export default {
    /**
     * Gets a list of datasets that belong to the currently logged in user
     *
     */
    getUserDatasets() {
        return wrappedSession.get('/api/dataset-info/')
            .then(resp => {

                if (resp.data.results) {
                    const modifiedResults = resp.data.results.map((obj) => {
                        // copy wizard_step into user_step
                        if (obj.depositor_setup_info) {
                            obj.depositor_setup_info.user_step = obj.depositor_setup_info.wizard_step;
                            console.log('setting status to ' + obj.depositor_setup_info.wizard_step)
                            obj.status = obj.depositor_setup_info.wizard_step;
                        }
                        return obj;
                    });
                    resp.data.results = modifiedResults
                }
                return resp;
            })
            .then(resp => camelcaseKeys(resp, {deep: true}))

    },
    // Gets the DatasetInfo object for the given objectId
    getDatasetInfo(objectId) {
        return wrappedSession.get('/api/dataset-info/' + objectId + '/')
            .then(resp => convertWizardStep(resp))
            .then(resp => camelcaseKeys(resp, {deep: true}))
    },
    runProfiler(datasetId, userId) {
        return wrappedSession.post('/api/profile/run-direct-profile-no-async/',
            {object_id: datasetId})
            .then(resp => camelcaseKeys(resp, {deep: true}))

    },
    deleteDatasetInfo(datasetId) {
        return wrappedSession.delete('/api/dataset-info/' + datasetId + '/')
    }
}