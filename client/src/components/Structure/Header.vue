<template>
  <div>
    <v-app-bar
        class="pt-5"
        app
        color="header"
        flat
        extended
        extension-height="50px"
    >
      <v-container class="my-5 fill-height">
        <v-col class="logo" cols="3">
          <router-link class="router-link" :to="NETWORK_CONSTANTS.HOME.PATH"
          >
            <v-img
                :src="require('../../assets/DPCreator_from_OpenDP.svg')"
                contain
                aspect-ratio="4"
            ></v-img>
          </router-link
          >


        </v-col>

        <v-spacer></v-spacer>

        <v-app-bar-nav-icon
            @click.stop="isDrawerActive = !isDrawerActive"
            class="hidden-md-and-up"
        ></v-app-bar-nav-icon>

        <div class="hidden-sm-and-down" v-if="!!isLoggedUser">
          <span
              v-for="(item, index) in items"
              :key="index + '-' + index"
              class="ml-8"
          >
            <router-link
                class="router-link d-inline-flex align-center"
                :to="item.link"
            >
              <v-icon left>{{ item.icon }}</v-icon>
              {{ item.title }}
            </router-link>
          </span>
          <span class="ml-8 red--text text--accent-4">
            <router-link
                class="router-link d-inline-flex align-center"
                to="/?logout=true"
                v-on:click.native="logoutHandler()"
            >
              <v-icon color="red accent-4" left>mdi-logout</v-icon>
              Logout
            </router-link>
          </span>
        </div>
      </v-container>
    </v-app-bar>
    <v-navigation-drawer
        v-model="isDrawerActive"
        v-if="isDrawerActive"
        app
        width="100%"
    >
      <v-container class="my-5 pt-4 d-flex justify-space-between align-center">
        <v-col class="logo" cols="3">
          <router-link class="router-link" :to="NETWORK_CONSTANTS.HOME.PATH"
          >Logo
          </router-link
          >
        </v-col>
        <div class="px-2">
          <v-icon @click.stop="isDrawerActive = !isDrawerActive"
          >mdi-close
          </v-icon
          >
        </div>
      </v-container>
      <v-list nav class="mobile-menu-list">
        <v-list-item
            v-for="(item, index) in mobileMenu"
            :key="item.title + '-' + index"
            link
        >
          <v-list-item-icon class="mx-5">
            <v-icon>{{ item.icon }}</v-icon>
          </v-list-item-icon>

          <v-list-item-content>
            <v-list-item-title
                @click="$router.push(item.link)"
                class="grey--text"
            >{{ item.title }}
            </v-list-item-title
            >
          </v-list-item-content>
        </v-list-item>
        <v-list-item v-if="isLoggedUser">
          <v-list-item-icon class="mx-5">
            <v-icon color="red accent-4">mdi-logout</v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title
                @click="$router.push('/logout')"
                class="red--text text--accent-4"
            >Logout
            </v-list-item-title
            >
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>
  </div>
</template>

<style lang="scss" scoped>
.mobile-menu-list {
  .v-list-item .v-list-item__title {
    font-size: 1.6rem;
  }
}
</style>

<script>
import NETWORK_CONSTANTS from "../../router/NETWORK_CONSTANTS";
import {mapGetters, mapState} from "vuex";
export default {
  name: "Header",
  computed: {
    ...mapGetters('auth', ['isAuthenticated', 'isTermsAccepted']),
    ...mapState('auth', ['user']),
    username() {
      return (this.user) ? this.user.username : null
    },
    isLoggedUser: function () {
      return this.isAuthenticated;
    },
    mobileMenu: function () {
      return this.isLoggedUser
          ? this.mobileMenuLoggedUser
          : this.mobileMenuUnisLoggedUser;
    }
  },
  data: () => ({
    isDrawerActive: false,
    items: [
      {
        title: "My Data",
        link: NETWORK_CONSTANTS.MY_DATA.PATH,
        icon: "mdi-database"
      },
      {
        title: "My Profile",
        link: NETWORK_CONSTANTS.MY_PROFILE.PATH,
        icon: "mdi-account"
      }
    ],
    mobileMenuUnisLoggedUser: [
      {
        title: "Log in",
        link: NETWORK_CONSTANTS.LOGIN.PATH,
        icon: "mdi-login"
      },
      {
        title: "Sign up",
        link: NETWORK_CONSTANTS.SIGN_UP.PATH,
        icon: "mdi-account-plus"
      },
      {
        title: "Terms and conditions",
        link: NETWORK_CONSTANTS.TERMS_AND_CONDITIONS.PATH,
        icon: "mdi-file-document"
      },
      {title: "Contact us", link: NETWORK_CONSTANTS.CONTACT_US.PATH, icon: "mdi-email"}
    ],
    mobileMenuLoggedUser: [
      {title: "Home", link: NETWORK_CONSTANTS.HOME.PATH, icon: "mdi-home"},
      {
        title: "My Data",
        link: NETWORK_CONSTANTS.MY_DATA.PATH,
        icon: "mdi-database"
      },
      {
        title: "My Profile",
        link: NETWORK_CONSTANTS.MY_PROFILE.PATH,
        icon: "mdi-account"
      },
      {title: "Contact us", link: NETWORK_CONSTANTS.CONTACT_US.PATH, icon: "mdi-email"}
    ],
    NETWORK_CONSTANTS
  }),
  methods: {
    logoutHandler() {
      this.isLoggedUser = undefined;
      localStorage.removeItem("isLoggedUser");
      this.$router.go();
    }
  }
};
</script>
