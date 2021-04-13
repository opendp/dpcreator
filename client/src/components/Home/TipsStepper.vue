<template>
  <v-stepper vertical id="tips-stepper">
    <v-stepper-step complete complete-icon="mdi-account-plus" step="1">
      Sign up
    </v-stepper-step>

    <v-stepper-content step="1">
      <p>
        Before starting, you have to make sure your data is appropriate to be
        processed with this tool by checking the following tips and terms of
        use.
      </p></v-stepper-content
    >

    <v-stepper-step complete complete-icon="mdi-play-circle" step="2">
      Start the process
    </v-stepper-step>

    <v-stepper-content step="1">
      <p>
        When you log in you can start working with your Dataverse file. We’ll
        use the first 20 variables of your dataset.
      </p>
    </v-stepper-content>

    <v-stepper-step complete complete-icon="mdi-timer" step="3">
      Work on release
    </v-stepper-step>

    <v-stepper-content step="1">
      <p>
        You can work with your data in 4 steps: Confirm variables, Set epsilon
        value, Create statistics, Generate DP Release. You'll see more
        information about the steps during the process. You have 72 hours to
        finish your release or the data will be deleted from the tool.
      </p>
    </v-stepper-content>

    <v-stepper-step complete complete-icon="mdi-email" step="4">
      Check the release
    </v-stepper-step>
    <v-stepper-content step="1">
      <p>
        Once you finish the steps, the file has to be processed and it can take
        minutes or hours. You’ll receive an email when it's done.
      </p>
    </v-stepper-content>
  </v-stepper>
</template>

<style lang="scss">
#tips-stepper {
  box-shadow: unset;

  .v-stepper__step__step.primary {
    background-color: unset !important;
    margin-right: 40px;

    .v-icon {
      color: #9e9e9e;
      font-size: 3rem;
    }
  }

  .v-stepper__label {
    font-size: 1.625rem;
    font-weight: 300;
    letter-spacing: 0;
  }

  &.v-stepper--vertical .v-stepper__content {
    padding-left: 50px;
    margin-top: 5px;
    margin-bottom: 5px;
  }
}
</style>

<script>
export default {
  name: "TipsStepper"
};
</script>
