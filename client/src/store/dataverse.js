import dataverse from '../api/dataverse'
import session from '../api/session';

import {
  SET_DV_HANDOFF,
  REMOVE_DV_HANDOFF,
  SET_DATAVERSE_USER,
  SET_DATAVERSE_FILE_INFO,
  SET_DATAVERSE_FILE_LOCKED
} from './types';

const initialState = {
  handoffId: null,
  dataverseUser: null,
  fileInfo: null,
  fileLocked: false
};
const getters = {
  getHandoffId: state => {
    return state.handoffId
  },
  getfileInfo: state => {
    return state.fileInfo
  },
  getFileLocked: state => {
    return state.fileLocked
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
    return dataverse.updateDataverseUser(OpenDPUserId, state.handoffId)
        .then((resp) => {
          console.log(resp.data)
          commit('SET_DATAVERSE_USER', resp.data.data['dv_user'])
          return resp.data.data['dv_user']
        })
  },

  /**
   * Get the latest DV FileInfo info for this OpenDPUser
   * from Dataverse, and put in Vuex store
   * @param commit
   * @param state
   * @param dataverseUserId (object_id field of DataverseUser object)
   * @returns {Promise<void>}
   */
  updateFileInfo({commit, state}, dataverseUserId) {
    return dataverse.updateFileInfo(dataverseUserId, state.handoffId)
        .then((resp) => {
          commit('SET_DATAVERSE_FILE_INFO', resp.data.data)
          //   return resp.data.data
        }).catch((error) => {
          if (error.response.status == 423) {
            commit('SET_DATAVERSE_FILE_LOCKED', true)
          }
          console.log(error.response.data);
          console.log(error.response.status);
        })
  },
};

const mutations = {
  [SET_DATAVERSE_USER](state, dataverseUser) {
    state.dataverseUser = dataverseUser
  },
  [SET_DATAVERSE_FILE_INFO](state, fileInfo) {
    state.fileInfo = fileInfo
  },
  [SET_DATAVERSE_FILE_LOCKED](state, fileLocked) {
    state.fileLocked = fileLocked
  },
  [SET_DV_HANDOFF](state, payload) {
    state.handoffId = payload
  },
  [REMOVE_DV_HANDOFF](state) {
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
