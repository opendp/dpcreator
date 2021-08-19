<template>
  <v-container
      :class="{
      'mb-5': $vuetify.breakpoint.xsOnly,
      'mb-16': $vuetify.breakpoint.smAndUp
    }"
  >
    <v-row>
      <v-col
          offset-sm="1"
          offset-md="0"
          sm="10"
          class="text-center mx-auto px-5"
          md="7"
      >
        <h2 class="title-size-1 home-title mx-auto mb-7">
          {{ $t("home.stepsTitle") }}Hello
        </h2>
        <p v-html="$t('home.stepsDescription')"
           class="grey--text text--darken-2 home-description"
           :class="{
            'mb-5': $vuetify.breakpoint.xsOnly,
            'mb-10': $vuetify.breakpoint.smAndUp
          }"
        >

        </p>
      </v-col>
    </v-row>
    <v-row>
      <v-col
          offset-sm="1"
          offset-md="0"
          sm="10"
          cols="12"
          md="3"
          :class="{ 'py-2': $vuetify.breakpoint.xsOnly }"
      >
        <ColoredBox class="step">
          <template v-slot:content>
            <RoundedNumber :number="1"/>
            <h3 class="mb-5 grid-item__title"> {{ $t("home.step1 title") }}</h3>
            <p v-html="$t('home.step1 text')" class="grey--text text--darken-2">

            </p>
          </template>
        </ColoredBox>
      </v-col>
      <v-col
          offset-sm="1"
          offset-md="0"
          sm="10"
          cols="12"
          md="3"
          :class="{ 'py-2': $vuetify.breakpoint.xsOnly }"
      >
        <ColoredBox class="step">
          <template v-slot:content>
            <RoundedNumber :number="2"/>
            <h3 class="mb-5 grid-item__title">{{ $t("home.step2 title") }}</h3>
            <p v-html="$t('home.step2 text')" class="grey--text text--darken-2">

            </p>
          </template>
        </ColoredBox>
      </v-col>
      <v-col
          offset-sm="1"
          offset-md="0"
          sm="10"
          cols="12"
          md="3"
          :class="{ 'py-2': $vuetify.breakpoint.xsOnly }"
      >
        <ColoredBox class="step">
          <template v-slot:content>
            <RoundedNumber :number="3"/>
            <h3 class="mb-5 grid-item__title">{{ $t('home.step3 title') }}</h3>
            <p v-html="$t('home.step3 text')" class="grey--text text--darken-2">
            </p>
          </template>
        </ColoredBox>
      </v-col>
      <v-col
          offset-sm="1"
          offset-md="0"
          sm="10"
          cols="12"
          md="3"
          :class="{ 'py-2': $vuetify.breakpoint.xsOnly }"
      >
        <ColoredBox class="step">
          <template v-slot:content>
            <RoundedNumber :number="4"/>
            <h3 class="mb-5 grid-item__title">{{ $t('home.step4 title') }}</h3>
            <p v-html="$t('home.step4 text')" class="grey--text text--darken-2">

            </p>
          </template>
        </ColoredBox>
      </v-col>
    </v-row>
  </v-container>
</template>

<style lang="scss" scoped>
.home-title {
  max-width: 500px;
  @media (max-width: 600px) {
    max-width: 250px;
  }
}

.home-description {
  @media (max-width: 600px) {
    max-width: 85%;
    margin: 0 auto;
  }
}

.step {
  min-height: unset;
  @media screen and (min-width: 960px) {
    min-height: 370px;
  }
}

.grid-item__title {
  font-size: 25px;
  font-weight: lighter;
}
</style>

<script>
import ColoredBox from "../DesignSystem/Boxes/ColoredBox.vue";
import RoundedNumber from "../RoundedNumber.vue";
export default {
  components: {ColoredBox, RoundedNumber},
  name: "StepsGrid"
};
</script>
