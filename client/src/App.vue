<template>
  <v-app id="app" :style="generalCss">
    <link rel="preconnect" href="https://fonts.gstatic.com"/>
    <link :href="fontUrl" rel="stylesheet"/>
    <Header/>
    <v-main class="">
      <router-view/>
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
export default {
  components: {Footer, Header},
  data: () => ({
    fontUrl: settings.google_fonts_url
  }),
  computed: {
    theme() {
      return this.$vuetify.theme.dark ? "dark" : "light";
    },
    generalCss() {
      return {
        background: this.$vuetify.theme.themes[this.theme].background,
        "--font-name": settings.google_fonts_name
      };
    }
  }
};
</script>
