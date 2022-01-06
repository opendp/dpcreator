<template>
  <v-app id="app" :style="generalCss">
    <link rel="preconnect" href="https://fonts.gstatic.com"/>
    <link :href="fontUrl" rel="stylesheet"/>
    <Header/>
    <v-main class="">
      <template v-if="error || apiErrorMessage">
        <v-container>
          <v-row>
            <v-col cols="1">
              <!-- left side padding to center the alert box -->
            </v-col>
            <v-col cols="11">

              <v-spacer></v-spacer>
              <ColoredBorderAlert v-if="errMsg" type="error">
                <template v-slot:content>
                  <b>Vue Runtime Error:</b> {{ errMsg.message }}
                  <v-spacer></v-spacer>
                  <b>Stack Trace: </b>{{ errMsg.stack }}
                </template>

              </ColoredBorderAlert>
              <ColoredBorderAlert v-if="apiErrorMessage" type="error">
                <template v-slot:content>
                  <b>API Error:</b> {{ apiErrorMessage.config.url }} <br>
                  Status: {{ apiErrorMessage.status }} {{ apiErrorMessage.statusText }} <br>
                  Detail: {{ apiErrorMessage.data.detail }} <br>
                </template>
              </ColoredBorderAlert>
            </v-col>
          </v-row>
        </v-container>
      </template>
      <router-view v-if="!(error || apiErrorMessage)"/>
    </v-main>
    <Footer/>
  </v-app>
</template>

<style lang="scss">
@import "./style.scss";
</style>

<script>
import settings from "./settings";
import Footer from "./components/Structure/Footer.vue";
import Header from "./components/Structure/Header.vue";
import ColoredBorderAlert from "@/components/DynamicHelpResources/ColoredBorderAlert";
import {mapState} from "vuex";

export default {
  title: 'DP Creator',
  components: {Footer, Header, ColoredBorderAlert},
  data: () => ({
    error: false,
    errMsg: null,
    apiErrorMessage: null,
    fontUrl: settings.google_fonts_url
  }),
  created() {
    window.addEventListener('unhandledrejection', (event) => {
      console.log("unhandled rejection")
      console.log('event.promise: ' + event.promise)
      console.log('event.reason: ' + event.reason)
      this.apiErrorMessage = event.reason
      console.log('event url: ' + this.apiErrorMessage.config.url)
      //event.promise contains the promise object
      //event.reason contains the reason for the rejection


    });
  },
  computed: {
    ...mapState('auth', ['errorMessage']),
    theme() {
      return this.$vuetify.theme.dark ? "dark" : "light";
    },
    generalCss() {
      return {
        background: this.$vuetify.theme.themes[this.theme].background,
        "--font-name": settings.google_fonts_name
      };
    }
  },
  errorCaptured(err, vm, info) {
    // err: error trace
    // vm: component in which error occured
    // info: Vue specific error information such as lifecycle hooks, events etc.
    this.error = true
    this.errMsg = err
    // return false to stop the propagation of errors further to parent or global error handler
  }
};
</script>
