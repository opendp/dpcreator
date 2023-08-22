<template>
  <div class="set-epsilon-page">
    <h1 class="title-size-1">Confirm Epsilon</h1>
    <p>
      {{
        $t('set epsilon.epsilon intro')
      }}
    </p>
    <v-text-field
        v-model="editEpsilon"
        background-color="soft_primary"
        class="top-borders-radius width50"
        data-test="editEpsilon"
        :rules="[validateEpsilon]"
        v-on:keyup="saveUserInput"
    ></v-text-field>
    <v-text-field
        v-model="editDelta"
        background-color="soft_primary"
        class="top-borders-radius width50"
        data-test="Fixed value"
        :rules="[validateDelta]"
        v-on:keyup="saveUserInput"
    ></v-text-field>

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
import {MAX_TOTAL_EPSILON} from "@/shared/createStatsUtils";

export default {
  name: "ConfirmEpsilonDelta",
  components: {

  },
  props:
    ["defaultEpsilon",
    "defaultDelta"],
  data() {
    return {
      editEpsilon: 0,
      editDelta: 0
    };
  },

  created() {


  },
  computed: {
    ...mapState('auth', ['error', 'user']),
    ...mapState('dataset', ['datasetInfo']),
    ...mapGetters('dataset', ['getDepositorSetupInfo']),


  },
  methods: {
    inputIsValid(inputEpsilon, inputDelta) {
      return inputEpsilon !== null && inputDelta !== null
    },
    validateEpsilon(v) {
      const minEpsilon = 0
      const maxEpsilon = MAX_TOTAL_EPSILON
      let valid = true
      if (this.editEpsilon) {
        const val = Number(v)
        if (val < minEpsilon ||
            val > maxEpsilon)
          valid = false
      }
      return valid || "Value must be between " +
          minEpsilon +
          " and " + maxEpsilon
    },
    validateDelta(v) {
      const minDelta = 0
      const maxDelta = 1
      let valid = true
      if (this.editDelta) {
        const val = Number(v)
        if (val < minDelta ||
            val > maxDelta)
          valid = false
      }
      return valid || "Value must be between " +
          minDelta +
          " and " + maxDeltaç
    },
    saveUserInput() {
      if (this.inputIsValid(this.editEpsilon, this.editDelta)) {
        const userInput = {
          epsilon: this.editEpsilon,
          delta: this.editDelta
        }
      const payload = {objectId: this.getDepositorSetupInfo.objectId, props: userInput}
      this.$store.dispatch('dataset/updateDepositorSetupInfo',
          payload)
    }}
  },
  watch: {
    defaultEpsilon:function(newValue,oldValue){
      this.editEpsilon = newValue
    },
    defaultDelta:function(newValue,oldValue){
      this.editDelta = newValue
    },
    editEpsilon: function (newValue, oldValue) {
      if (this.inputIsValid(newValue, this.editDelta)) {
        this.$emit("stepCompleted", 2, true);
      } else {
        this.$emit("stepCompleted", 2, false);
      }
    },
    editDelta: function (newValue, oldValue) {
      if (this.inputIsValid(this.editEpsilon, newValue)) {
        this.$emit("stepCompleted", 2, true);
      } else {
        this.$emit("stepCompleted", 2, false);
      }
    },
  }
};
</script>
