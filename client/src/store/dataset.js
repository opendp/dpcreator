import dataset from "@/api/dataset";

import {
  SET_DATASET_LIST,
  SET_DATASET_INFO
} from './types';

const initialState = {
  datasetList: null,
  datasetInfo: null
};
const getters = {
  getDatasetList: state => {
    return state.datasetList
  },

};
const actions = {
  setDatasetList({commit, state}) {
    return dataset.getUserDatasets()
        .then((resp) => {
          console.log(resp.data.results)
          commit('SET_DATASET_LIST', resp.data.results)
        })
  },
  setDatasetInfo({commit}, objectId) {
    return dataset.getDatasetInfo(objectId)
        .then((resp) => {
          console.log(resp.data.results)
          commit('SET_DATASET_INFO', resp.data.results)
        })
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
