<template>
  <div class="set-epsilon-page">
    <h1 class="title-size-1">Set epsilon value</h1>
    <p>
      To determine the epsilon value, we need to confirm your dataset's
      characteristics with some questions about the sample.
    </p>
    <BorderTopAlertDismissible
        title="What is Epsilon (ε)?"
        text="Epsilon is a metric of privacy loss at a differentially change in data (adding, removing 1 entry). The smaller the value is, the better privacy protection."
    />
    <span class="font-weight-bold title-size-2 d-flex"
    ><v-icon color="primary" left>mdi-play</v-icon> Is your data a secret and
      simple random sample from a larger population?
    </span>
    <v-radio-group v-model="secretSample" class="pl-2">
      <v-radio label="Yes." value="yes"></v-radio>
      <div
          :class="
          `${secretSample === 'yes' ? 'population-size-container' : 'd-none'}`
        "
      >
        <strong>Population size: </strong>
        <v-text-field
            v-model="populationSize"
            class="d-inline-block text-right"
            placeholder="E.g. 5,000,000"
            type="number"
            background-color="blue lighten-4"
        />
        <strong>people</strong>
      </div>
      <v-radio label="No." value="no"></v-radio>
      <v-radio label="I'm unsure." value="unsure"></v-radio>
    </v-radio-group>

    <v-alert
        icon="mdi-information-outline"
        class="d-inline-block mb-16 mt-5"
        elevation="4"
    >
      For example, information about persons, their behavior, beliefs and
      attributes is generally private information that individuals in the
      dataset would not want publicly shared in their name and should be marked
      “yes”. Information that is solely about instituons, corporations, natural
      phenomena, etc., that are public record and can be publicly distributed,
      does not depend on private information.
    </v-alert>

    <div
        :class="`${radioObservationsNumberShouldBeDisabled ? 'disabled' : ''}`"
    >
      <span class="font-weight-bold title-size-2 d-flex"
      ><v-icon color="primary" left>mdi-play</v-icon> Can the number of
        observations in your dataset be made public knowledge?
      </span>
      <v-radio-group
          v-model="observationsNumberCanBePublic"
          class="pl-2"
          :disabled="radioObservationsNumberShouldBeDisabled"
      >
        <v-radio label="Yes." value="yes"></v-radio>
        <v-radio label="No." value="no"></v-radio>
        <v-radio label="I'm unsure." value="unsure"></v-radio>
      </v-radio-group>

      <v-alert
          icon="mdi-information-outline"
          class="d-inline-block mb-16 mt-5"
          elevation="4"
      >
        For example, information about persons, their behavior, beliefs and
        attributes is generally private information that individuals in the
        dataset would not want publicly shared in their name and should be
        marked “yes”. Information that is solely about instituons, corporations,
        natural phenomena, etc., that are public record and can be publicly
        distributed, does not depend on private information.
      </v-alert>
    </div>
  </div>
</template>

<style lang="scss">
.info-banner {
  .v-banner__content {
    align-items: unset;
  }
}

.set-epsilon-page {
  .population-size-container {
    margin-left: 30px;
  }

  .v-input__control {
    padding: 0 10px;
    border-top-left-radius: 5px !important;
    border-top-right-radius: 5px !important;

    input {
      padding-left: 15px;
      padding-right: 15px;
      text-align: right;
    }
  }
}
</style>

<script>
import BorderTopAlertDismissible from "../../components/DynamicHelpResources/BorderTopAlertDismissible.vue";

export default {
  name: "SetEpsilonValue",
  components: {BorderTopAlertDismissible},
  data: () => ({
    secretSample: "",
    observationsNumberCanBePublic: "",
    populationSize: ""
  }),
  computed: {
    radioObservationsNumberShouldBeDisabled: function () {
      return this.secretSample === "";
    }
  },
  watch: {
    observationsNumberCanBePublic: function (newValue) {
      if (newValue !== "") {
        this.$emit("stepCompleted", 2, true);
      }
    }
  }
};
</script>
