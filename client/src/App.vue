<template>
  <v-app id="inspire">
    <Header/>
    <v-main class="">
      <router-view/>
    </v-main>
    <Footer/>
  </v-app>
</template>

<style lang="scss">
.v-application {
  .router-link {
    color: inherit;
    text-decoration: none;
  }
}

.logo {
  font-size: 1.625rem;
  font-weight: bold;
  padding: 0;
}

.v-toolbar__content,
.v-toolbar__extension {
  padding: 0 !important;
}

.title-size-1 {
  font-size: 2.5rem;
  line-height: 3.125rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
}

.title-size-2 {
  font-size: 1.625rem;
  line-height: 1.6875rem;
  font-weight: 400;

  &.title-size-2--small {
    font-size: 1.25rem;
  }

  strong {
    font-weight: 600;
  }
}

.v-btn {
  border-radius: 6px !important;
  text-transform: none !important;
  min-width: 150px !important;
  letter-spacing: 0 !important;
}

.pointer {
  cursor: pointer;
}

.disabled {
  opacity: 0.6;
}

@import url("https://fonts.googleapis.com/css2?family=Nunito+Sans:ital,wght@0,400;0,600;0,700;1,400;1,600;1,700&display=swap");
$body-font-family: "Nunito Sans";
.v-application {
  font-family: $body-font-family, sans-serif !important;
  font-size: 1rem;
}

.top-borders-radius {
  border-top-left-radius: 5px !important;
  border-top-right-radius: 5px !important;
}

.width50 {
  width: 50%;
}

.v-application .noise-params.lighten-4 {
  border-bottom: 1px solid gray !important;
}

.v-card__actions {
  padding-left: 24px !important;
}

:root {
  --light-blue-color: #e8f0fe;
}

.light-blue-bg {
  background: var(--light-blue-color);
}
</style>

<script>
import Footer from "./components/Structure/Footer.vue";
import Header from "./components/Structure/Header.vue";

export default {
  components: {Footer, Header}
};
</script>
