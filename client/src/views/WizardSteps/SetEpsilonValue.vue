<template>
  <div class="set-epsilon-page">
    <h1 class="title-size-1">Set epsilon value</h1>
    <p>
      {{
        $t('set epsilon.epsilon intro')
      }}
    </p>
    <BorderTopAlertDismissible>
      <template v-slot:content>
        <strong>What is Epsilon (ε)?</strong>
        <p class="my-1">
          Epsilon is a metric of privacy loss at a differentially change in data
          (adding, removing 1 entry). The smaller the value is, the better
          privacy protection.
        </p>
      </template>
    </BorderTopAlertDismissible>
    <span class="font-weight-bold title-size-2 d-flex"
    ><v-icon color="primary" left>mdi-play</v-icon> Is your data a secret and
      simple random sample from a larger population?
    </span>
    <v-radio-group v-model="secretSample" class="pl-2">
      <RadioItem label="Yes." value="yes"/>
      <div
          :class="
          `${secretSample === 'yes' ? 'population-size-container' : 'd-none'}`
        "
      >
        <strong>Population size: </strong>
        <v-text-field
            v-model="populationSize"
            class="d-inline-block"
            id="populationSize"
            placeholder="E.g. 5,000,000"
            type="number"
            background-color="soft_primary"
        />
        <strong>people</strong>
      </div>
      <RadioItem label="No." value="no"/>
      <RadioItem label="I'm unsure." value="unsure"/>
    </v-radio-group>

    <AdditionalInformationAlert class="mb-10" locale-tag="set epsilon.help data secret">
    </AdditionalInformationAlert>

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
        <RadioItem label="Yes." value="yes"/>
        <RadioItem label="No." value="no"/>
        <RadioItem label="I'm unsure." value="unsure"/>
      </v-radio-group>

      <AdditionalInformationAlert locale-tag="set epsilon.help data public">
      </AdditionalInformationAlert>
    </div>
  </div>
</template>

<style lang="scss">
.info-banner {
  .v-banner__content {
    align-items: unset;
  }
}

#populationSize {
  text-align: center;
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
    }
  }
}
</style>

<script>
import RadioItem from "../../components/DesignSystem/RadioItem.vue";
import AdditionalInformationAlert from "../../components/DynamicHelpResources/AdditionalInformationAlert.vue";
import BorderTopAlertDismissible from "../../components/DynamicHelpResources/BorderTopAlertDismissible.vue";

export default {
  name: "SetEpsilonValue",
  components: {
    BorderTopAlertDismissible,
    AdditionalInformationAlert,
    RadioItem
  },
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
