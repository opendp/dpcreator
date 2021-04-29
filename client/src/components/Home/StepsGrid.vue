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
          {{ $t("home.stepsTitle") }}
        </h2>
        <p
            class="grey--text text--darken-2 home-description"
            :class="{
            'mb-5': $vuetify.breakpoint.xsOnly,
            'mb-10': $vuetify.breakpoint.smAndUp
          }"
        >
          {{ $t("home.stepsDescription") }}
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
            <h3 class="mb-5 grid-item__title">Sign up</h3>
            <p class="grey--text text--darken-2">
              Before starting, you have to
              <strong
              >make sure your data is appropriate to be processed</strong
              >
              with this tool by checking the following tips and terms of use.
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
            <h3 class="mb-5 grid-item__title">Start the process</h3>
            <p class="grey--text text--darken-2">
              When you log in you can start working with your Dataverse
              file.<strong>
              We’ll use the first 20 variables of your dataset.</strong
            >
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
            <h3 class="mb-5 grid-item__title">Work on release</h3>
            <p class="grey--text text--darken-2">
              You can work with your data in 5 steps: Validate Dataset, Confirm
              variables, Set epsilon value, Create statistics, Generate DP
              Release. You'll see more information about the steps during the
              process, which
              <strong
              >you have to finish before 72 hours or the data will be deleted
                from the tool.</strong
              >
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
            <h3 class="mb-5 grid-item__title">Check the release</h3>
            <p class="grey--text text--darken-2">
              Once you finish the steps,
              <strong>the file has to be processed</strong> and it can take
              minutes or hours.
              <strong>You’ll receive an email when it's done.</strong>
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
