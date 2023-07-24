<template>
  <div class="set-epsilon-page">
    <h1 class="title-size-1">Sampling Frame</h1>
    <p>
      {{
        $t('set epsilon.epsilon intro')
      }}
    </p>

   <div

   >
      <span class="font-weight-bold title-size-2 d-flex"
      ><v-icon color="primary" left>mdi-play</v-icon> Can the number of
        observations in your data file be made public knowledge?
      </span>
     <v-radio-group
         v-model="observationsNumberCanBePublic"
         class="pl-2"
         v-on:change="saveUserInput"
     >
       <RadioItem label="Yes." data-test="Public Observations - yes" value="yes"/>
       <RadioItem label="No." value="no"/>
       <RadioItem label="I'm unsure." value="unsure"/>
     </v-radio-group>

     <AdditionalInformationAlert locale-tag="set epsilon.help data public">
     </AdditionalInformationAlert>
   </div>
    <span class="font-weight-bold title-size-2 d-flex"
    ><v-icon color="primary" left>mdi-play</v-icon> Is your data a secret and
      simple random sample from a larger population?
    </span>
    <v-radio-group v-model="secretSample" class="pl-2" v-on:change="saveUserInput">
      <RadioItem data-test="Larger Population - yes" label="Yes." value="yes"/>
      <div
          :class="
          `${secretSample === 'yes' ? 'population-size-container' : 'd-none'}`
        "
      >
        <strong>Population size: </strong>
        <v-text-field
            v-model="populationSize"
            data-test="populationSizeInput"
            data
            class="d-inline-block"
            id="populationSize"
            placeholder="E.g. 5,000,000"
            type="number"
            :hide-spin-buttons=true
            background-color="soft_primary"
            :rules="[populationSizeRule]"
            v-on:keyup="saveUserInput"
        />
        <strong>people</strong>
      </div>
      <RadioItem data-test="Larger Population - no" label="No." value="no"/>
      <RadioItem label="I'm unsure." value="unsure"/>
    </v-radio-group>

    <AdditionalInformationAlert class="mb-10" locale-tag="set epsilon.help data secret">
    </AdditionalInformationAlert>

  </div>
</template>

<style lang="scss">
// Remove up an down error from text field when type == number
input::-webkit-outer-spin-button,
input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

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
import {mapGetters, mapState} from "vuex";

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
    populationSize: 0
  }),
  created() {
    // Initialize questions with previously input values,
    // if they exist
    if (this.getDepositorSetupInfo.epsilonQuestions !== null) {
      this.secretSample =
          this.getDepositorSetupInfo.epsilonQuestions.secretSample
      this.observationsNumberCanBePublic =
          this.getDepositorSetupInfo.epsilonQuestions.observationsNumberCanBePublic
      this.populationSize =
          this.getDepositorSetupInfo.epsilonQuestions.populationSize

    }
  },
  computed: {
    ...mapState('auth', ['error', 'user']),
    ...mapState('dataset', ['datasetInfo']),
    ...mapGetters('dataset', ['getDepositorSetupInfo']),
    radioObservationsNumberShouldBeDisabled: function () {
      return this.secretSample === "";
    }
  },
  methods: {
    populationSizeRule(n) {
      return (this.populationSizeIsValid(n))
          || "Population size must greater than 0."
    },
    populationSizeIsValid(pop) {

      let valid = this.secretSample !== 'yes' || pop > 0
      return valid
    },

    saveUserInput() {
      const userInput = {
        epsilonQuestions: {
          secretSample: this.secretSample,
          populationSize: Number(this.populationSize),
          observationsNumberCanBePublic: this.observationsNumberCanBePublic,
        }
      }

      const payload = {objectId: this.getDepositorSetupInfo.objectId, props: userInput}
      this.$store.dispatch('dataset/updateDepositorSetupInfo',
          payload)
    }
  },
  watch: {
    secretSample: function (newValue, oldValue) {
      if (newValue !== "" && this.populationSizeIsValid(this.populationSize)) {
        this.$emit("stepCompleted", 2, true);
      } else {
        this.$emit("stepCompleted", 2, false);
      }
    },
    populationSize: function (newValue, oldValue) {
      if (this.observationsNumberCanBePublic !== "" && this.secretSample !== "" && this.populationSizeIsValid(newValue)) {
        this.$emit("stepCompleted", 2, true);
      } else {
        this.$emit("stepCompleted", 2, false);
      }
    },
    observationsNumberCanBePublic: function (newValue, oldValue) {
      if (newValue !== "" && this.secretSample !== "" && this.populationSizeIsValid(this.populationSize)) {
        this.$emit("stepCompleted", 2, true);
      } else {
        this.$emit("stepCompleted", 2, false);
      }
    }
  }
};
</script>
