import settings from "@/api/settings";

import {
    SET_VUE_SETTINGS,
} from './types';
import dataverse from "@/api/dataverse";


const initialState = {
    vueSettings: null,

};
const getters = {
    getVueSettings: state => {
        return state.vueSettings
    },

};
const actions = {
    fetchVueSettings({commit, state}) {
        settings.getVueSettings().then((resp) => {
            console.log("setting data " + JSON.stringify(resp.data) + "," + typeof resp.data)
            commit('SET_VUE_SETTINGS', resp.data)
        })
    }

};

const mutations = {
    [SET_VUE_SETTINGS](state, settings) {
        state.vueSettings = settings
    },

};


export default {
    namespaced: true,
    state: initialState,
    getters,
    actions,
    mutations,
};
