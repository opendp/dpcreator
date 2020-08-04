import Vue from "vue";

export const store = Vue.observable({
    isNavOpen: true
});

export const mutations = {
    toggleNav() {
	store.isNavOpen = !store.isNavOpen
    }
};
