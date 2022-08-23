<template>
  <v-dialog
      :width="$vuetify.breakpoint.smAndDown ? '90%' : '50%'"
      v-model="dialog"
      @click:outside="close"
  >
    <v-card elevation="2" class="px-10 py-12 add-statistic-dialog">
      <v-icon data-test="Add Statistic Close" style="position: absolute; right: 40px" @click="close"
      >mdi-close
      </v-icon
      >
      <v-card-title>
        <h2 data-test='AddStatisticDialog' class="title-size-2 mb-5">{{ formTitle }}</h2>
      </v-card-title>
      <v-card-text class="text--primary">
        <div>
          <span>
            Which <strong>single-variable statistic</strong> would you like to
            use?
          </span>
          <v-radio-group
              row
              class="radio-group-statistics-modal"
              v-model="editedItemDialog.statistic"
          >
            <v-radio
                class="rounded-pill mr-2"
                v-for="(statistic, index) in singleVariableStatistics"
                :key="statistic + '-' + index"
                :label="statistic.label"
                :value="statistic.value"
                on-icon="mdi-check"
                @click="() => updateSelectedStatistic(statistic)"
                :data-test="statistic.label"
            ></v-radio>
          </v-radio-group>
        </div>

        <div>
          <span> Which<strong> variable </strong>would you like to use? </span>
          <span> (Need to add another variable?
            <a data-test="confirmVariablesLink" v-on:click="addVariable">Go back to Confirm Variables Step </a>
            ) </span>

          <v-radio-group
              row
              :multiple="false"
              class="radio-group-statistics-modal"
              v-model="editedItemDialog.variable"
          >
            <v-radio
                class="rounded-pill mr-2"
                v-for="(variable, index) in variables"
                :key="variable + index"
                :label="variable['label']"
                :value="variable['key']"
                :data-test="variable['label']"
                on-icon="mdi-check"
            ></v-radio>
          </v-radio-group>

        </div>

        <div v-if="editedItemDialog.handleAsFixed">

          <span>Enter a <strong> fixed value</strong></span> for missing values:
          <div>{{ minMax }}</div>
          <div class="width50">
            <v-text-field
                v-model="editedItemDialog.fixedValue"
                background-color="soft_primary"
                class="top-borders-radius width50"
                data-test="Fixed value"
                :rules="[validateFixedValue]"
            ></v-text-field>
          </div>
        </div>
        <div class="width100" v-if="showHistogramOptions()">
          <span>Choose option for <strong>histogram bins:</strong></span>
          <v-radio-group
              v-model="editedItemDialog.histogramBinType"
          >
            <v-container class="grey lighten-5">
              <v-row>
                <v-col>
                  <v-radio v-if="this.variableInfo[this.editedItemDialog.variable]
                  &&  this.variableInfo[this.editedItemDialog.variable].type ==  'Integer'"
                           :key="ONE_BIN_PER_VALUE"
                           :label="histogramOptions[ONE_BIN_PER_VALUE].label"
                           :value="ONE_BIN_PER_VALUE"
                           :data-test="ONE_BIN_PER_VALUE"
                  ></v-radio>
                </v-col>
              </v-row>
              <v-row>
                <v-col>
                  <v-radio
                      :key="EQUAL_BIN_RANGES"
                      :label="histogramOptions[EQUAL_BIN_RANGES].label+' ('+ minEdge()+','+maxEdge()+')'"
                      :value="EQUAL_BIN_RANGES"
                      :data-test="EQUAL_BIN_RANGES"
                  ></v-radio>
                </v-col>
              </v-row>
              <v-expand-transition>
                <v-row v-show="editedItemDialog.histogramBinType == EQUAL_BIN_RANGES">
                  <v-col>

                    <v-text-field
                        label="Enter number of bins within bounds"
                        v-model="editedItemDialog.numberOfBins"
                        background-color="soft_primary"
                        class="top-borders-radius  width80"
                        data-test="numberOfBins"
                        :rules="[validateNumBins]"
                    ></v-text-field>


                  </v-col>

                </v-row>
              </v-expand-transition>
              <v-row>
                <v-col>
                  <v-radio
                      :key="BIN_EDGES"
                      :label="histogramOptions[BIN_EDGES].label"
                      :value="BIN_EDGES"
                      :data-test="BIN_EDGES"
                  ></v-radio>
                </v-col>
              </v-row>
              <v-expand-transition>
                <v-row align-content="center" v-show="editedItemDialog.histogramBinType == BIN_EDGES">
                  <v-col cols="3">
                    {{ 'Min: ' + minEdge() }}
                  </v-col>
                  <v-col cols="6">
                    <v-combobox
                        v-model="editedItemDialog.binEdges"
                        chips
                        label="Add edges"
                        multiple
                        class="my-0 py-0"
                        background-color="soft_primary my-0"
                        data-test="binEdges"
                        :search-input.sync="edgesInput"
                        @update:search-input="delimitInput()"
                        :delimiters="[',']"
                        :rules="[validateBinEdges]"
                    >
                      <template v-slot:selection="{ attrs, item, select, selected }">
                        <v-chip
                            :v-bind="attrs"
                            :input-value="selected"
                            close
                            :color="edgeColor(item)"
                            text-color="white"
                            :click="select"
                            :item="item"
                            @click:close="removeEdgeFromList(item)"
                        >
                          <div data-test="categoryChip"><strong>{{ item }}
                          </strong></div>
                        </v-chip>
                      </template>
                    </v-combobox>
                  </v-col>
                  <v-col cols="3">
                    {{ 'Max: ' + maxEdge() }}
                  </v-col>

                </v-row>
              </v-expand-transition>
            </v-container>


          </v-radio-group>
        </div>
        <ColoredBorderAlert type="warning" v-if="validationError">
          <template v-slot:content>
            <div data-test="validation alertbox">
              <ul v-if="errorCount > 1">
                <li v-if="item.message" v-for="item in validationErrorMsg">
                  {{ item.stat.statistic }} / {{ item.stat.variable }}: {{ item.message }}
                </li>
              </ul>
              <div v-if="errorCount==1" v-for="item in validationErrorMsg">
                {{ item.message }}
              </div>
            </div>
          </template>
        </ColoredBorderAlert>

      </v-card-text>

      <v-card-actions>
        <Button
            color="primary"
            classes="mr-2 px-5"
            :click="save"
            :disabled="isButtonDisabled()"
            data-test="Create Statistic Button"
            :label="getButtonLabel"
        />

        <Button
            color="primary"
            outlined
            classes="px-5"
            :click="close"
            label="Close"
            data-test="Close Dialog"
        />
      </v-card-actions>

    </v-card>
  </v-dialog>
</template>

<style lang="scss">
.add-statistic-dialog {
  .radio-group-statistics-modal {
    .v-input--selection-controls__input {
      height: 0;
      width: 0;
      margin-right: 0;

      i.mdi-check {
        display: inherit;
        color: white !important;
      }
      input,
      div,
      i {
        display: none;
      }
    }
    .v-radio {
      border: 1px solid var(--v-primary-base);
      padding: 5px 20px;

      &:hover,
      &.v-item--active {
        background: var(--v-primary-base);

        .v-label {
          color: white;
        }
      }

      &.v-item--active {
        .v-input--selection-controls__input {
          margin-right: 12px;
        }
      }

      .v-label {
        color: var(--v-primary-base);
        font-weight: 700;
        justify-content: center;
      }
    }
  }

  .v-text-field__slot {
    padding-left: 10px;
  }
}
</style>

<script>
import Button from "../../../DesignSystem/Button.vue";
import ColoredBorderAlert from "@/components/DynamicHelpResources/ColoredBorderAlert";
import {mapGetters, mapState} from "vuex";
import createStatsUtils from "@/shared/createStatsUtils";

const ONE_BIN_PER_VALUE = "onePerValue"
const EQUAL_BIN_RANGES = "equalRanges"
const BIN_EDGES = "binEdges"

export default {
  name: "AddStatisticDialog",
  components: {Button, ColoredBorderAlert},
  props: ["formTitle", "dialog", "editedIndex", "editedItem", "variableInfo", "statistics"],

  computed: {
    ...mapState('dataset', ['analysisPlan', "datasetInfo"]),
    ...mapGetters('dataset', ['getDepositorSetupInfo']),
    errorCount: function () {
      let count = 0;
      if (this.validationErrorMsg) {
        this.validationErrorMsg.forEach((item) => {
          if (item.message) {
            count++
          }
        })
      }
      return count
    },
    getButtonLabel: function () {
      return this.formTitle === 'Edit Statistic' ? 'Save' : 'Create Statistic'
    },

    isMultiple: function () {
      return this.editedIndex === -1;
    },

    minMax: function () {
      let minMax = ""
      if (this.editedItemDialog.variable &&
          this.variableInfo[this.editedItemDialog.variable] &&
          this.variableInfo[this.editedItemDialog.variable].hasOwnProperty('min')
      ) {
        minMax = "(Must be between " +
            this.variableInfo[this.editedItemDialog.variable].min + " and " +
            this.variableInfo[this.editedItemDialog.variable].max + ")"
      }
      return minMax
    },
    variables: function () {
      let displayVars = []
      for (const key in this.variableInfo) {
        let displayVar = JSON.parse(JSON.stringify(this.variableInfo[key]))
        displayVar.key = key
        if (displayVar.label === '') {
          displayVar.label = displayVar.name
        }
        if (this.variableInfo[key].selected &&
            (!this.selectedStatistic || this.allowedVariableTypes[this.selectedStatistic.label].includes(this.variableInfo[key].type))) {
          displayVars.push(displayVar)

        }

      }
      return displayVars
    }
  },
  watch: {
    editedItem: function (newEditedItem) {
      /*
       Check the value of statistic coming from the CreateStatistics page.
       If it exists, that means we are in edit mode, in which case we need
       to initialize the value of selectedStatistic to the current value to be edited.
       */
      if (newEditedItem.statistic) {
        this.singleVariableStatistics.forEach(item => {
          if (item.value === newEditedItem.statistic) {
            this.selectedStatistic = item
          }
        })
        if (this.selectedStatistic === null) {
          throw 'Error: statistic ' + newEditedItem.statistic + ' not found in singleVariableStatistices'
        }
      }
      this.editedItemDialog = Object.assign({}, newEditedItem);
      // automatic assignments added here because we removed the Missing Values option from the popup.
      // All stats are created with type = insert_fixed, only the fixed value is editable.
      this.editedItemDialog.handleAsFixed = true
      this.editedItemDialog.missingValuesHandling = "insert_fixed"
    },

  },
  data: () => ({
    singleVariableStatistics: [
      {value: "mean", label: "Mean"},
      {value: "histogram", label: "Histogram"},
      //  {value: "quantile", label: "Quantile"},
      {value: "count", label: "Count"},
      {value: "variance", label: "Variance"}
    ],
    allowedVariableTypes: {
      "Mean": ["Integer", "Float"],
      "Count": ["Integer", "Float", "Categorical", "Boolean"],
      "Variance": ["Integer", "Float"],
      "Histogram": ["Integer", "Float", "Categorical", "Boolean"],
      "Quantile": ["Integer", "Float"] // not yet available
    },
    selectedStatistic: null,
    edgesInput: "",
    validationError: false,
    validationErrorMsg: null,
    editedItemDialog: {
      statistic: "",
      label: "",
      variable: "",
      epsilon: "",
      delta: '0.0',
      error: "",
      missingValuesHandling: "insert_fixed",
      histogramBinType: "",
      numberOfBins: null,
      binEdges: [],
      handleAsFixed: true,
      fixedValue: "",
      locked: false,
      accuracy: {value: null, message: null}
    },
    missingValuesHandling: [
      // "Drop them", remove this for now, until the library can use it
      {value: "insert_random", label: "Insert random value"},
      {value: "insert_fixed", label: "Insert fixed value"}
    ],

    ONE_BIN_PER_VALUE,
    EQUAL_BIN_RANGES,
    BIN_EDGES,
    histogramOptions: {
      [ONE_BIN_PER_VALUE]: {label: "One bin per value"},
      [EQUAL_BIN_RANGES]: {label: "Equal range bins within variable bounds"},
      [BIN_EDGES]: {label: "Bin edges"}
    }
  }),
  methods: {
    isButtonDisabled: function () {
      let disabled = false
      let validHistogramOption = false
      if (!this.showHistogramOptions()
          || this.editedItemDialog.histogramBinType === ONE_BIN_PER_VALUE
          || (this.editedItemDialog.histogramBinType === BIN_EDGES
              && this.editedItemDialog.binEdges instanceof Array
              && this.editedItemDialog.binEdges.length > 0
              && this.isEdgesInputValid(this.editedItemDialog.binEdges))
          || (this.editedItemDialog.histogramBinType === EQUAL_BIN_RANGES
              && this.editedItemDialog.numberOfBins
              && this.isNumBinsValid(this.editedItemDialog.numberOfBins)
          )) {
        validHistogramOption = true
      }
      if (this.editedItemDialog.statistic === ""
          || this.editedItemDialog.variable === ""
          || this.editedItemDialog.variable === undefined
          || (this.editedItemDialog.statistic !== "count" && !this.editedItemDialog.fixedValue)
          || (this.editedItemDialog.statistic === "histogram" && !validHistogramOption)
      ) {
        disabled = true
      }
      console.log('returning  disabled: ' + disabled)
      return disabled
    },
    removeEdgeFromList(edge) {
      this.editedItemDialog.binEdges.splice(
          this.editedItemDialog.binEdges.indexOf(edge),
          1
      );
    },
    delimitInput(edges) {
      if (this.edgesInput && this.edgesInput.split(",").length > 1) {
        let v = []
        if (this.editedItemDialog.binEdges) {
          v = JSON.parse(JSON.stringify(this.editedItemDialog.binEdges))
        }
        v.push(this.edgesInput)
        const reducer = (a, e) => [...a, ...e.split(',')]
        let edges = [...new Set(v.reduce(reducer, []))]
        edges = edges.filter(word => word.length > 0);

        this.editedItemDialog.binEdges = JSON.parse(JSON.stringify(edges))
        this.edgesInput = ""
      }
    },
    showHistogramOptions() {
      let retVal = this.editedItemDialog.statistic == 'histogram'
          && this.variableInfo[this.editedItemDialog.variable]
          && !["Categorical", "Boolean"].includes(this.variableInfo[this.editedItemDialog.variable].type)
      return retVal
    },
    maxBins() {
      let maxBins = 0
      if (this.editedItemDialog.variable &&
          this.variableInfo[this.editedItemDialog.variable] &&
          this.variableInfo[this.editedItemDialog.variable].hasOwnProperty('min')) {
        maxBins = Number(this.variableInfo[this.editedItemDialog.variable].max) - Number(this.variableInfo[this.editedItemDialog.variable].min)
      }
      return maxBins
    },
    minEdge() {
      let minEdge = 0
      if (this.editedItemDialog.variable &&
          this.variableInfo[this.editedItemDialog.variable] &&
          this.variableInfo[this.editedItemDialog.variable].hasOwnProperty('min')) {
        minEdge = Number(this.variableInfo[this.editedItemDialog.variable].min)
      }
      return minEdge
    },
    variableRange() {
      let range = 0;
      if (this.editedItemDialog.variable &&
          this.variableInfo[this.editedItemDialog.variable] &&
          this.variableInfo[this.editedItemDialog.variable].hasOwnProperty('max')) {
        range = Number(this.variableInfo[this.editedItemDialog.variable].max)
            - Number(this.variableInfo[this.editedItemDialog.variable].min) + 1
      }
      return range
    },
    maxEdge() {
      let maxEdge = 0
      if (this.editedItemDialog.variable &&
          this.variableInfo[this.editedItemDialog.variable] &&
          this.variableInfo[this.editedItemDialog.variable].hasOwnProperty('max')) {
        maxEdge = Number(this.variableInfo[this.editedItemDialog.variable].max)
      }
      return maxEdge
    },
    edgeColor(edge) {
      if (this.isValidEdge(edge)) {
        return "blue darken-2"
      }
      return "red"
    },
    isValidEdge(edge) {
      const parsed = Number.parseFloat(edge)
      if (isNaN(parsed)
          || parsed > this.variableInfo[this.editedItemDialog.variable].max
          || parsed < this.variableInfo[this.editedItemDialog.variable].min) {
        return false
      }
      return true
    },
    isEdgesInputValid(v) {
      let valid = true
      v.forEach(edge => {
            valid = this.isValidEdge(edge)
          }
      )
      return valid
    },
    isNumBinsValid(v) {
      const num = Number(v)
      return Number.isInteger(num) && num >= 1 && num <= this.variableRange()
    },
    validateNumBins(v) {
      return this.isNumBinsValid(v) || "Value must be an integer between 1 and " + this.variableRange()
    },
    validateBinEdges(v) {

      return this.isEdgesInputValid(v) || "Edge must be a number between "
          + this.variableInfo[this.editedItemDialog.variable].min + " and "
          + this.variableInfo[this.editedItemDialog.variable].max
    },
    validateFixedValue(v) {
      let valid = true
      if (this.editedItemDialog.variable &&
          this.variableInfo[this.editedItemDialog.variable] &&
          this.variableInfo[this.editedItemDialog.variable].hasOwnProperty('min')) {
        const val = Number(v)
        if (val < this.variableInfo[this.editedItemDialog.variable].min ||
            val > this.variableInfo[this.editedItemDialog.variable].max)
          valid = false
      }
      return valid || "Value must be between " +
          this.variableInfo[this.editedItemDialog.variable].min +
          " and " + this.variableInfo[this.editedItemDialog.variable].max
    },
    save() {
      try {
        this.editedItemDialog.label = this.selectedStatistic.label
        this.validate().then((valid) => {
          if (valid) {
            this.validationError = false
            this.$emit("saveConfirmed", this.editedItemDialog)
          } else {
            this.validationError = true
          }
        })
      } catch (err) {
        this.validationError = true
        this.validationErrorMsg = [{"valid": false, "message": err}]
      }
    },
    validate() {
      if (this.checkForDuplicates()) {
        // if there are duplicates in the list, then
        // no need to check release validation, just return false
        // Use the same format for the error message as the release validation
        this.validationErrorMsg = [{"valid": false, "message": "Statistic already exists on the statistics table."}]
        return new Promise(function (resolve, reject) {
          resolve(false);
        });
      } else {
        return this.validateStatistics()
      }
    },
    checkForDuplicates() {
      let duplicates = false
      if (this.statistics) {
        if (this.editedItemDialog.variable) {
          duplicates = this.isMatchingStatistic(this.editedItemDialog.variable)
        }
      }
      return duplicates
    },
    isMatchingStatistic(variable) {
      let isMatching = false
      if (this.statistics) {
        this.statistics.forEach((stat) => {
          if (stat.statistic === this.editedItemDialog.statistic
              && stat.variable === variable
              && stat.missingValuesHandling === this.editedItemDialog.missingValuesHandling
              && stat.fixedValue === this.editedItemDialog.fixedValue) {
            isMatching = true
          }
        })
      }
      return isMatching
    },

    validateStatistics() {
      // create a local list that
      // includes the statistic the user wants to add or edit
      let tempStats = JSON.parse(JSON.stringify(this.statistics))
      if (this.editedIndex > -1) {
        tempStats[this.editedIndex] = this.editedItemDialog
      } else {
        const label = this.editedItemDialog.variable
        const variable = this.editedItemDialog.variable
        const cl = this.getDepositorSetupInfo.confidenceLevel
        tempStats.push(Object.assign({}, this.editedItemDialog, {variable}, {label}, {cl}))

      }
      createStatsUtils.redistributeValue(this.getDepositorSetupInfo.epsilon, 'epsilon', tempStats)
      createStatsUtils.redistributeValue(this.getDepositorSetupInfo.delta, 'delta', tempStats)
      return createStatsUtils.releaseValidation(this.analysisPlan.objectId, tempStats)
          .then((validateResults) => {
            this.validationErrorMsg = validateResults.data
            return validateResults.valid
          })


    },
    addVariable() {
      this.close()
      this.$emit("addVariable")
    },
    close() {
      this.validationError = false
      this.validationErrorMsg = ""
      this.selectedStatistic = null
      this.$emit("close");
    },
    updateSelectedVariable(variable, index) {
      if (this.editedItemDialog.variable.includes(variable)) {
        this.editedItemDialog.variable.splice(index, 1);
      }
    },
    updateSelectedStatistic(statistic) {
      this.selectedStatistic = statistic
      if (this.selectedStatistic.value == "count") {
        this.editedItemDialog.missingValuesHandling = ""
        this.editedItemDialog.handleAsFixed = false
        this.editedItemDialog.fixedValue = 'na'
      } else {
        this.editedItemDialog.missingValuesHandling = "insert_fixed"
        this.editedItemDialog.handleAsFixed = true
        this.editedItemDialog.fixedValue = ''

      }
    },
    updateFixedInputVisibility(handlingOption) {
      this.editedItemDialog.handleAsFixed =
          handlingOption.label === "Insert fixed value";
    }
  }
};
</script>
