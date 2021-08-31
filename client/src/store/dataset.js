import dataset from "@/api/dataset";
import analysis from "@/api/analysis";
const camelcaseKeys = require('camelcase-keys');

import {
    SET_DATASET_LIST,
    SET_DATASET_INFO,
    SET_PROFILER_MSG,
    SET_PROFILER_STATUS,
    SET_ANALYSIS_PLAN
} from './types';
import dataverse from "@/api/dataverse";

const initialState = {
    datasetList: null,
    datasetInfo: null,
    profilerStatus: null,
    profilerMsg: null,
    analysisPlan: null
};
const getters = {
    getDatasetList: state => {
        return state.datasetList
    },
    getDatasetInfo: state => {
        return state.datasetInfo
    },
    getDepositorSetupInfo: state => {
        if (state.datasetInfo) {
            return state.datasetInfo.depositorSetupInfo
        } else {
            return null
        }
    },
    // List of items for the MyData table, which flattens the nested AnalysisPlan array.
    // If a Dataset contains multiple AnalysisPlan objects,
    // create an item in the list for each AnalysisPlan.
    getMyDataList: state => {
        let myData = []
        if (state.datasetList) {
            state.datasetList.forEach(dataset => {
                let myDataElem = {}
                if (dataset.analysisPlans && dataset.analysisPlans.length > 0) {
                    myDataElem.datasetInfo = dataset
                    dataset.analysisPlans.forEach(analysisPlan => {
                        myDataElem.analysisPlan = analysisPlan
                        myData.push(myDataElem)
                    })
                } else {
                    myDataElem.datasetInfo = dataset
                    myDataElem.analysisPlan = null;
                    myData.push(myDataElem)
                }
            })
        }
        return myData
    },
    getUpdatedTime: state => {
        if (state.analysisPlan) {
            return state.analysisPlan.updated
        } else if (state.datasetInfo.depositorSetupInfo) {
            let d = new Date(state.datasetInfo.depositorSetupInfo.updated)
            return d.toLocaleString()
        } else {
            return 'not found'
        }
    },
    getCreatedTime: state => {
        return state.datasetInfo.created
    },
    getTimeRemaining: state => {
        const millisInDay = 1000 * 60 * 60 * 24
        const millisInHour = 1000 * 60 * 60
        const millisInMin = 1000 * 60
        const createdDate = new Date(state.datasetInfo.created)
        // console.log('createdDate: '+createdDate)
        const expirationDate = createdDate.getTime() + (3 * millisInDay)

        const diffTime = expirationDate - (new Date().getTime())
        // console.log('exp date '+new Date(expirationDate))

        if (diffTime < 0) {
            return ('Time has expired')
        } else {
            const diffDays = Math.floor(diffTime / (millisInDay))
            const diffHours = Math.floor((diffTime - (diffDays * millisInDay)) / millisInHour)
            const diffMin = Math.floor((diffTime - (diffDays * millisInDay + diffHours * millisInHour)) / millisInMin)
            return '' + diffDays + 'd ' + diffHours + 'h ' + diffMin + 'min'
        }

    }

};
const actions = {
    createAnalysisPlan({commit, state}, datasetId) {
        return analysis.createAnalysisPlan(datasetId)
            .then((resp) => {
                console.log('response from create:' + JSON.stringify(resp))
                commit('SET_ANALYSIS_PLAN', resp)
            }).catch((error) => {
                console.log(error.response.data);
                console.log(error.response.status);
            })
    },
    setAnalysisPlan({commit, state}, analysisId) {
        return analysis.getAnalysisPlan(analysisId)
            .then((resp) => {
                commit('SET_ANALYSIS_PLAN', resp)
            }).catch((error) => {
                console.log(error.response.data);
                console.log(error.response.status);
            })
    },
    updateAnalysisPlan({commit, state}, {objectId, props}) {
        return analysis.patchAnalysisPlan(objectId, props)
            .then(() => this.dispatch('dataset/setAnalysisPlan', state.analysisPlan.objectId)
                .catch((data) => {
                    return Promise.reject(data)
                }))

    },
    setDatasetList({commit, state}) {
        return dataset.getUserDatasets()
            .then((resp) => {
                console.log('response: ' + JSON.stringify(resp))
                commit(SET_DATASET_LIST, resp.data.results)
            })
    },
    setDatasetInfo({commit}, objectId) {
        return dataset.getDatasetInfo(objectId)
            .then((resp) => {
                console.log('setDatasetInfo, resp: ' + JSON.stringify(resp))
                commit(SET_DATASET_INFO, resp.data)
            })
    },
    updateDepositorSetupInfo({commit, state}, {objectId, props}) {
        return analysis.patchDepositorSetup(objectId, props)
            .then(() => this.dispatch('dataset/setDatasetInfo', state.datasetInfo.objectId)
                .catch((data) => {
                    return Promise.reject(data)
                }))

    },
    /**
     * Save user edits to the variables in the Confirm Variables page
     * @param commit
     * @param state
     * @param variableInput
     */
    updateVariableInfo({commit, state}, variableInput) {
        //  Get a local copy of variableInfo, for editing
        let variableInfo = JSON.parse(JSON.stringify(state.datasetInfo.depositorSetupInfo.variableInfo))
        let targetVar = variableInfo[variableInput.key]
        targetVar.name = variableInput.name
        targetVar.label = variableInput.label
        if (variableInput.type === 'Numerical') {
            targetVar.min = Number(variableInput.additional_information.min)
            targetVar.max = Number(variableInput.additional_information.max)
        }
        if (variableInput.type === 'Categorical') {
            targetVar.categories = variableInput.additional_information.categories
            let numericValues = [];
            if (variableInput.additional_information.categories !== null) {
                variableInput.additional_information.categories.forEach(item => {
                    if (!isNaN(item)) {
                        numericValues.push(Number(item))
                    }
                })
            }
            if (numericValues !== null) {
                if (numericValues.length === variableInput.additional_information.categories.length) {
                    targetVar.categories = numericValues
                }
            }
        }
        const patch = {
            variableInfo: variableInfo
        }
        const payload = {objectId: state.datasetInfo.depositorSetupInfo.objectId, props: patch}
        this.dispatch('dataset/updateDepositorSetupInfo', payload)

    },
    /**
     * Save user edits to the statistics table in the Create Statistics page
     * @param commit
     * @param state
     * @param statInput - Array of JSON objects from statistics table
     */
    updateDPStatistics({commit, state}, statList) {
        const patch = {
            dpStatistics: statList
        }
        const payload = {objectId: state.analysisPlan.objectId, props: patch}
        this.dispatch('dataset/updateAnalysisPlan', payload)

    },
    /**
     * POST a request to start the profiler for current dataset,
     * then open a websocket to receive messages about profiler status.
     * If profiler completes successfully, update depositorSetupInfo with the variableInfo = returned variables from profiler
     * @param commit
     * @param state
     * @param userId used for websocket URL
     */
    runProfiler({commit, state}, {userId}) {
        dataset.runProfiler(state.datasetInfo.objectId)

        const prefix = 'ws://'
        const websocketId = 'ws_' + userId
        console.log("running profiler, before chatsocket")
        const chatSocket = new WebSocket(
            prefix + window.location.host + '/async_messages/ws/profile/' + websocketId + '/'
        );

        /* ---------------------------------------------- */
        /* Add a handler for incoming websocket messages  */
        /* ---------------------------------------------- */

        chatSocket.onmessage = (e) => {
            // parse the incoming JSON to a .js object

            const wsData = camelcaseKeys(JSON.parse(e.data), {deep: true});

            /* "wsMsg" attributes are the defined in the Python WebsocketMessage object
                 msgType (str): expected "PROFILER_MESSAGE"
                 success (boolean):  error detected?
                 userMessage (str): description of what happened
                 msgCnt (int): Not used for the profiler
                 data: Profile data, if it exists, JSON
                 timestamp: timestamp

                - reference: opendp_apps/async_messages/websocket_message.py
            */
            const wsMsg = wsData.message
            // "wsMsg.msgType": should be 'PROFILER_MESSAGE'
            if (wsMsg.msgType !== 'PROFILER_MESSAGE') {
                console.log('unknown msgType: ' + wsMsg.msgType);
            } else {
                // ---------------------------------------
                // "ws_msg.success": Did it work?
                // ---------------------------------------
                if (wsMsg.success === true) {
                    console.log('-- success message');
                } else if (wsMsg.success === false) {
                    console.log('-- error message');
                    alert(wsMsg.userMessage);
                } else {
                    console.log('-- error occurred!')
                    return;
                }
                commit(SET_PROFILER_MSG, wsMsg.userMessage)
                commit(SET_PROFILER_STATUS, wsMsg.success)
                console.log('ws_msg.user_message: ' + wsMsg.userMessage);

                if (wsMsg.data) {
                    const profileData = JSON.parse(wsMsg.data.profileStr)
                    const profileStr = JSON.stringify(profileData.variables, null, 2);
                    console.log(typeof wsMsg.data);
                    console.log('>>DATA<< ws_msg.data: ' + profileStr);

                    // update depositorSetupInfo with variableInfo contained in the message
                    const props = {variable_info: profileData.variables}
                    const payload = {objectId: state.datasetInfo.depositorSetupInfo.objectId, props: props}
                    this.dispatch('dataset/updateDepositorSetupInfo', payload)
                    return (wsMsg.userMessage)
                }

            }

        };

        chatSocket.onclose = function (e) {
            console.error('Chat socket closed unexpectedly');
        };
        chatSocket.onerror = function (e) {
            console.error('onerror: ' + e);
        };
    }

};

const mutations = {
    [SET_ANALYSIS_PLAN](state, analysisPlan) {
        state.analysisPlan = analysisPlan
    },
    [SET_DATASET_LIST](state, datasetList) {
        state.datasetList = datasetList
    },
    [SET_PROFILER_MSG](state, msg) {
        state.profilerMsg = msg
    },
    [SET_PROFILER_STATUS](state, status) {
        state.profilerStatus = status
    },
    [SET_DATASET_INFO](state, datasetInfo) {
        state.datasetInfo = datasetInfo
    },
};

export default {
  namespaced: true,
  state: initialState,
  getters,
  actions,
  mutations,
};
