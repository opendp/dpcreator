import dataset from "@/api/dataset";
import depositorSetup from "@/api/depositorSetup";

import {
    SET_DATASET_LIST,
    SET_DATASET_INFO,
} from './types';

const initialState = {
  datasetList: null,
  datasetInfo: null
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
    }
};
const actions = {
  setDatasetList({commit, state}) {
      return dataset.getUserDatasets()
          .then((resp) => {
              commit(SET_DATASET_LIST, resp.data.results)
          })
  },
    setDatasetInfo({commit}, objectId) {
        return dataset.getDatasetInfo(objectId)
            .then((resp) => {
                commit(SET_DATASET_INFO, resp.data)
            })
    },
    updateDepositorSetupInfo({commit, state}, {objectId, props}) {
        return depositorSetup.patchDepositorSetup(objectId, props)
            .then(() => this.dispatch('dataset/setDatasetInfo', state.datasetInfo.objectId)
                .catch((data) => {
                    return Promise.reject(data)
                }))

    }

};

const mutations = {
  [SET_DATASET_LIST](state, datasetList) {
    state.datasetList = datasetList
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
