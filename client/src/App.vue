<template>
  <v-app id="app" :style="generalCss">
    <link rel="preconnect" href="https://fonts.gstatic.com"/>
    <link :href="fontUrl" rel="stylesheet"/>
    <Header/>
    <v-main class="">
      <template v-if="error || errorObject">
        <v-container>
          <v-row>
            <v-col>
              <v-spacer></v-spacer>
            </v-col>
            <v-col>
              <ColoredBorderAlert v-if="appErrMsg" type="error">
                <template v-slot:content>
                  <b>Error Message:</b> {{ appErrMsg }}
                </template>
              </ColoredBorderAlert>
              <ColoredBorderAlert v-else type="warning">
                <template v-slot:content>
                  Sorry! An error occurred.
                </template>
              </ColoredBorderAlert>
              <Button
                  data-test="ErrorContinueButton"
                  :click="continueAction"
                  label="Go To Homepage"
                  class="primary"
              />
            </v-col>
            <v-col>
              <v-spacer></v-spacer>
            </v-col>
          </v-row>
          <v-row>
            <v-col>
              <ColoredBorderAlert v-if="errMsg" type="error">
                <template v-slot:content>
                  <b>Vue Runtime Error:</b> {{ errMsg.message }}
                  <v-spacer></v-spacer>
                  <b>Stack Trace: </b>{{ errMsg.stack }}
                </template>
              </ColoredBorderAlert>
              <ColoredBorderAlert v-if="error && errorObject" type="error">
                <template v-slot:content>
                  <template v-if="errorObject.status==403">
                    You do not have authorization to view this page.
                  </template>
                  <template v-else>
                    <b>Runtime Error:</b>
                    <json-viewer :value="errorObject"></json-viewer>
                  </template>
                </template>
              </ColoredBorderAlert>
            </v-col>
          </v-row>
          <v-row>
            <v-col>
              <v-spacer></v-spacer>
            </v-col>
            <v-col>
              <Button
                  data-test="ErrorContinueButton"
                  :click="continueAction"
                  class="primary"
                  label="Go To Homepage"
              />
            </v-col>
            <v-col>
              <v-spacer></v-spacer>
            </v-col>
          </v-row>
        </v-container>
      </template>
      <router-view v-if="!(error || errorObject)"/>
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
import NETWORK_CONSTANTS from "@/router/NETWORK_CONSTANTS";
import Button from "@/components/DesignSystem/Button";
export default {
  title: 'DP Creator',
  components: {Footer, Header, ColoredBorderAlert, Button},
  data: () => ({
    error: false,
    errMsg: null,
    errorObject: null,
    errorRequest: null,
    appErrMsg: null,
    fontUrl: settings.google_fonts_url
  }),
  created() {
    window.addEventListener('unhandledrejection', (event) => {
      this.error = true
      console.log("unhandled rejection")
      console.log('event.promise: ' + event.promise)
      console.log('event.reason: ' + JSON.stringify(event.reason))
      // if the reason has a request object, display it separately
      if (event.reason.request){
        this.errorRequest = event.reason.request
        delete event.reason.request
      }

      this.errorObject = event.reason
      if (('data' in this.errorObject) && ('message' in this.errorObject.data)){
        this.appErrMsg = this.errorObject.data.message;
      }



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
  },
  methods: {
    continueAction() {
      window.location.replace('/')
      this.error = false
      this.errorObject = null
      this.errMsg = null
      this.errorRequest = null
    }
  }
};
</script>
