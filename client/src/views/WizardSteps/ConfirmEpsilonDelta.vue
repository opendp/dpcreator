<template>
  <div class="set-epsilon-page">
    <h1 class="title-size-1">Confirm Epsilon</h1>
    <p>
      {{
        $t('set epsilon.epsilon intro')
      }}
    </p>
    <template>
      <v-container class="form-container">
        <v-row class="form-row">
          <v-col cols="12" sm="6">
            <label class="form-label">Epsilon:</label>
            <v-text-field
                v-model="editEpsilon"
                data-test="confirmEpsilon"
                outlined
                :rules="[validateEpsilon]"
                v-on:keyup="handleChange"
            ></v-text-field>
          </v-col>
          <v-col cols="12" sm="6">
            <label class="form-label">Delta:</label>
            <v-select
                v-model="editDelta"
                :items="deltaOptions"
                label="Select Delta"
                outlined
                v-on:change="handleChange"
                :rules="[validateDelta]"
            ></v-select>
          </v-col>
        </v-row>
      </v-container>
    </template>

  </div>
</template>


<style scoped>
 .form-container {
   max-width: 600px;
   margin: 0 auto;
 }

.form-row {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  font-weight: bold;
  margin-bottom: 5px;
}

.v-text-field {
  width: 100%;
}
</style>
<script>
import RadioItem from "../../components/DesignSystem/RadioItem.vue";
import AdditionalInformationAlert from "../../components/DynamicHelpResources/AdditionalInformationAlert.vue";
import BorderTopAlertDismissible from "../../components/DynamicHelpResources/BorderTopAlertDismissible.vue";
import {mapGetters, mapState} from "vuex";
import {MAX_TOTAL_EPSILON} from "@/shared/createStatsUtils";

const MAX_EPSILON = MAX_TOTAL_EPSILON
const MIN_EPSILON = 0


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
      editDelta: null,
      deltaOptions: [
        { value: 0.0, text: '0.0' },
        { value: 0.00001, text: '0.00001 (10^-5)' },
        { value: 0.000001, text: '0.00001 (10^-6)' },
        { value: 0.0000001, text: '0.00001 (10^-7)' },
      ]
    };
  },

  created() {
    this.editEpsilon = this.defaultEpsilon
    this.editDelta = this.defaultDelta

  },
  computed: {
    ...mapState('auth', ['error', 'user']),
    ...mapState('dataset', ['datasetInfo']),
    ...mapGetters('dataset', ['getDepositorSetupInfo']),


  },
  methods: {
    inputIsValid(inputEpsilon, inputDelta) {
      console.log('inputDelta ' + inputDelta)
      const inputValid = inputEpsilon !== null && inputDelta !== null && this.epsilonIsValid(inputEpsilon) && this.deltaIsValid(inputDelta)
      console.log('inputValid ' + inputValid)
      return inputValid
    },
    epsilonIsValid(v) {

      let valid = false
      if (v) {
        const val = Number(v)
        if (val >= MIN_EPSILON &&
            val <= MAX_EPSILON) {
          valid = true
        }
      }
      return valid
    },
    validateEpsilon(v) {
      let valid = this.epsilonIsValid(v)
      return valid || "Value must be between " +
          MIN_EPSILON +
          " and " + MAX_EPSILON
    },
    deltaIsValid(v) {
      const valid= this.editDelta !== null
      console.log('delta valid =' + valid )
      return valid
    },
    validateDelta(v) {
      let valid = this.deltaIsValid(v)
      return valid || "Delta must not be null"
    },


    handleChange() {
      console.log('handleChange, this.editDelta = ' + this.editDelta)
      if (this.editDelta) {
        console.log('delta true')
      } else {
        console.log('delta false')
      }
      if (this.editEpsilon !== null && this.editDelta !==null  && this.inputIsValid(this.editEpsilon, this.editDelta)) {
        const userInput = {
          epsilon: this.editEpsilon,
          delta: this.editDelta
        }
        const payload = {objectId: this.getDepositorSetupInfo.objectId, props: userInput}
        this.$store.dispatch('dataset/updateDepositorSetupInfo',
            payload)
        this.$emit("completeDisabled",  false);
      } else {
        this.$emit("completeDisabled",  true);
      }
    }
  },
  watch: {
    defaultEpsilon:function(newValue,oldValue){
      this.editEpsilon = newValue
    },
    defaultDelta:function(newValue,oldValue){
      this.editDelta = newValue
    },
  }
};
</script>
