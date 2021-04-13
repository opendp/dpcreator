<template>
  <v-container class="mb-16">
    <v-row>
      <v-col class="text-center mx-auto px-5" md="7">
        <h2 class="title-size-1 home-title mx-auto mb-7">
          Introduce noise into your statistics to protect privacy
        </h2>
        <p class="grey--text text--darken-2 mb-10">
          This tool allows researchers to easily
          <strong>introduce noise into variables</strong> allowing them to mask
          specific details and <strong>keep data private</strong>. Find out how
          to get started with this tool below:
        </p>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12" md="3">
        <ColoredBox class="step">
          <template v-slot:content>
            <div
                class="white rounded-circle d-inline-block px-4 py-1 font-weight-bold mb-5 grid-item__title"
            >
              1
            </div>
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
      <v-col cols="12" md="3">
        <ColoredBox class="step">
          <template v-slot:content>
            <div
                class="white rounded-circle d-inline-block px-4 py-1 font-weight-bold mb-5 grid-item__title"
            >
              2
            </div>
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
      <v-col cols="12" md="3">
        <ColoredBox class="step">
          <template v-slot:content>
            <div
                class="white rounded-circle d-inline-block px-4 py-1 font-weight-bold mb-5 grid-item__title"
            >
              3
            </div>
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
      <v-col cols="12" md="3">
        <ColoredBox class="step">
          <template v-slot:content>
            <div
                class="white rounded-circle d-inline-block px-4 py-1 font-weight-bold mb-5 grid-item__title"
            >
              4
            </div>
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

export default {
  components: {ColoredBox},
  name: "StepsGrid"
};
</script>
