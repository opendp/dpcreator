<template>
  <section class="soft_primary">
    <v-container
        class="py-16"
        :class="{ 'px-11': $vuetify.breakpoint.smAndDown }"
    >
      <v-row>
        <v-col offset-md="1" class="d-flex align-center" id="img-wrapper">
          <v-img
              max-height="60%"
              max-width="30%"
              min-width="250px"
              src="../../assets/OpenDPLogo.png"
              class="hidden-sm-and-down"
          ></v-img>
          <v-img
              max-width="60%"
              src="../../assets/OpenDPLogo.png"
              class="hidden-md-and-up mb-5"
          ></v-img>
        </v-col>
        <v-col cols="12" md="6" id="text-wrapper">
          <h2 v-html="$t('home.footer title')" class="title-size-1">
          </h2>
          <p>
            {{
              $t('home.footer text')
            }}
          </p>
          <Button
              color="primary"
              label="Learn more"
              classes="my-5"
              url="https://opendp.org/"
          />
        </v-col>
      </v-row>
    </v-container>
  </section>
</template>

<style lang="scss" scoped>
#img-wrapper {
  @media screen and (min-width: 960px) {
    order: 2;
  }
}
#text-wrapper {
  @media screen and (min-width: 960px) {
    order: 1;
  }
}
</style>

<script>
import Button from "../DesignSystem/Button.vue";
export default {
  components: {Button},
  name: "AboutOpenDPBanner"
};
</script>
