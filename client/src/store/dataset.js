import dataset from "@/api/dataset";

import {
  SET_DATASET_LIST,
} from './types';

const initialState = {
  datasetList: null
};
const getters = {
  getDatasetList: state => {
    return state.datasetList
  },

};
const actions = {
  setDatasetList({commit, state}, datasetList) {
    return dataset.getUserDatasets()
        .then((resp) => {
          console.log(resp.data.results)
          commit('SET_DATASET_LIST', resp.data.results)
        })
  }
};

const mutations = {
  [SET_DATASET_LIST](state, datasetList) {
    state.datasetList = datasetList
  },

};

export default {
  namespaced: true,
  state: initialState,
  getters,
  actions,
  mutations,
};
