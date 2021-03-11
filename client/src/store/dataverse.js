import dataverse from '../api/dataverse'
import session from '../api/session';

import {
  SET_DV_HANDOFF,
  REMOVE_DV_HANDOFF,
  SET_DATAVERSE_USER,
} from './types';

const initialState = {
  handoffId: null,
  dataverseUser: null
};
const getters = {
  getHandoffId: state => {
    return state.handoffId
  },
};
const actions = {
  setHandoffId({commit, state}, handoffId) {
    commit('SET_DV_HANDOFF', handoffId)
  },
  removeDvParams({commit}) {
    commit('REMOVE_DV_HANDOFF')
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
    dataverse.updateDataverseUser(OpenDPUserId, state.handoffId)
        .then((resp) => {
          commit('SET_DATAVERSE_USER', resp.data.data)
        })
  },
};

const mutations = {
  [SET_DATAVERSE_USER](state, dataverseUser) {
    state.dataverseUser = dataverseUser
  },
  [SET_DV_HANDOFF](state, payload) {
    state.handoffId = payload
  },
  [REMOVE_DV_HANDOFF]() {
    state.handoffId = null
  },

};

export default {
  namespaced: true,
  state: initialState,
  getters,
  actions,
  mutations,
};
