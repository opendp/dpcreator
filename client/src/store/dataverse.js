import dataverse from '../api/dataverse'
import session from '../api/session';

import {
  SET_DV_PARAMS,
  REMOVE_DV_PARAMS,
  SET_DATAVERSE_USER,
} from './types';

const initialState = {
  dvParams: {
    apiToken: null,
    siteUrl: null
  },
  dataverseUser: null
};
const getters = {
  getDvParams: state => {
    return state.dvParams
  },
};
const actions = {
  setDvParams({commit, state}, {apiToken, siteUrl}) {
    console.log("apiToken: " + apiToken + " siteUrl: " + siteUrl)

    commit('SET_DV_PARAMS', {apiToken, siteUrl})
  },
  removeDvParams({commit}) {
    commit('REMOVE_DV_PARAMS')
  },
  createDataverseUser({commit, state}, OpenDPUserId) {
    // TODO: replace this with new createDataverseUser API
    return dataverse.getUserInfo(state.dvParams.apiToken, state.dvParams.siteUrl)
        .then((resp) => {
          commit('SET_DATAVERSE_USER', resp.data.data)
        })
  },
};

const mutations = {
  [SET_DATAVERSE_USER](state, dataverseUser) {
    state.dataverseUser = dataverseUser
  },
  [SET_DV_PARAMS](state, payload) {
    state.dvParams.siteUrl = payload.siteUrl
    state.dvParams.apiToken = payload.apiToken
  },
  [REMOVE_DV_PARAMS]() {
    state.dvParams = null
  },

};

export default {
  namespaced: true,
  state: initialState,
  getters,
  actions,
  mutations,
};
