<template>
  <div>
    <v-app-bar
        class="pt-10"
        app
        color="white"
        flat
        extended
        extension-height="80px"
    >
      <v-container class="my-5 fill-height">
        <v-col class="logo" cols="3">
          <router-link class="router-link" to="/">Logo</router-link>
        </v-col>

        <v-spacer></v-spacer>

        <v-app-bar-nav-icon
            @click.stop="drawer = !drawer"
            class="hidden-md-and-up menu-trigger"
        ></v-app-bar-nav-icon>

        <div class="hidden-sm-and-down" v-if="!!loggedUser">
          <span v-for="(item, index) in items" :key="index" class="ml-8">
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
    <v-navigation-drawer v-model="drawer" absolute right temporary width="100%">
      <v-container class="my-5 pt-10 d-flex justify-space-between align-center">
        <v-col class="logo" cols="3">
          <router-link class="router-link" to="/">Logo</router-link>
        </v-col>
        <div class="px-5">
          <v-icon @click.stop="drawer = !drawer">mdi-close</v-icon>
        </div>
      </v-container>
      <v-list dense nav>
        <v-list-item v-for="item in mobileItems" :key="item.title" link>
          <v-list-item-icon>
            <v-icon>{{ item.icon }}</v-icon>
          </v-list-item-icon>

          <v-list-item-content>
            <v-list-item-title @click="$router.push(item.link)">{{
                item.title
              }}
            </v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>
  </div>
</template>

<style lang="scss" scoped>
.menu-trigger {
  min-width: unset !important;
}
</style>

<script>
export default {
  name: "Header",
  computed: {
    loggedUser: function () {
      return localStorage.getItem("loggedUser");
    }
  },
  data: () => ({
    drawer: false,
    items: [
      {title: "My Data", link: "/my-data", icon: "mdi-database"},
      {title: "My Profile", link: "/my-profile", icon: "mdi-account"}
    ],
    mobileItems: [
      {title: "Log in", link: "/log-in", icon: "mdi-login"},
      {title: "Sign up", link: "/sign-up", icon: "mdi-account-plus"},
      {
        title: "Terms and conditions",
        link: "/terms-and-conditions",
        icon: "mdi-file-document"
      },
      {title: "Contact us", link: "/contact-us", icon: "mdi-email"}
    ]
  }),
  methods: {
    logoutHandler() {
      this.loggedUser = undefined;
      localStorage.removeItem("loggedUser");
      this.$router.go();
    }
  }
};
</script>
