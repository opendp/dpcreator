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
    commit('SET_DV_PARAMS', {apiToken, siteUrl})
  },
  removeDvParams({commit}) {
    commit('REMOVE_DV_PARAMS')
  },
  /**
   * Get the latest DV User info for this OpenDPUser
   * from Dataverse, and put in Vuex store
   * @param commit
   * @param state
   * @param OpenDPUserId
   * @returns {Promise<void>}
   */
  updateDataverseUser({commit, state}, OpenDPUserId) {
    // TODO: replace this with new updateDataverseUser API, which takes OpenDPUserId
    dataverse.updateDataverseUser(OpenDPUserId, state.dvParams.siteUrl, state.dvParams.apiToken)
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
    state.dvParams.apiToken = null
    state.dvParms.siteUrl = null
  },

};

export default {
  namespaced: true,
  state: initialState,
  getters,
  actions,
  mutations,
};
