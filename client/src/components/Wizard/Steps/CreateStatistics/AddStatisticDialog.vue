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
        <h2 class="title-size-2 mb-5">{{ formTitle }}</h2>
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
          <v-radio-group
              row
              :multiple="editedIndex === -1"
              class="radio-group-statistics-modal"
              v-model="editedItemDialog.variable"
          >
            <v-radio
                class="rounded-pill mr-2"
                v-for="(variable, index) in variables"
                :key="variable + index"
                :label="variable['label']"
                :value="variable['label']"
                :data-test="variable['label']"
                on-icon="mdi-check"
            ></v-radio>
          </v-radio-group>
        </div>

        <div>
          <span>
            How would you like<strong> missing values to be handled</strong>?
          </span>

          <v-radio-group
              row
              class="radio-group-statistics-modal"
              v-model="editedItemDialog.missingValuesHandling"
          >
            <v-radio
                class="rounded-pill mr-2"
                v-for="(handlingOption, index) in missingValuesHandling"
                :key="handlingOption + '-' + index"
                :label="handlingOption.label"
                :value="handlingOption.value"
                :data-test="handlingOption.label"
                on-icon="mdi-check"
                @click="() => updateFixedInputVisibility(handlingOption)"
            ></v-radio>
          </v-radio-group>
        </div>

        <div v-if="editedItemDialog.handleAsFixed">
          <span>Enter your <strong> fixed value:</strong></span>
          <div class="width50">
            <v-text-field
                v-model="editedItemDialog.fixedValue"
                placeholder="E.g. Lorem ipsum"
                background-color="soft_primary"
                class="top-borders-radius width50"
                data-test="Fixed value"
            ></v-text-field>
          </div>
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
            :disabled="isButtonDisabled"
            data-test="Create statistic"
            label="Create statistic"
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
import release from "@/api/release";
import {mapState, mapGetters} from "vuex";
import createStatsUtils from "@/shared/createStatsUtils";

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
    isButtonDisabled: function () {
      const returnVal = (
          !this.editedItemDialog.statistic ||
          !this.editedItemDialog.variable ||
          !this.analysisPlan ||
          !this.editedItemDialog.missingValuesHandling
      );
      return returnVal
    },
    isMultiple: function () {
      return this.editedIndex === -1;
    },
    variables: function () {
      let displayVars = []
      for (const key in this.variableInfo) {
        let displayVar = JSON.parse(JSON.stringify(this.variableInfo[key]))
        displayVar.key = key
        if (displayVar.label === '') {
          displayVar.label = displayVar.name
        }

        if ((this.selectedStatistic == null) ||
            (this.selectedStatistic.label !== 'Mean') ||
            (this.selectedStatistic.label === 'Mean' && this.variableInfo[key].type === 'Numerical')) {
          displayVars.push(displayVar)
        }

      }
      return displayVars
    }
  },
  watch: {
    editedItem: function (newEditedItem) {
      this.editedItemDialog = Object.assign({}, newEditedItem);
    },

  },
  data: () => ({
    singleVariableStatistics: [
      {value: "mean", label: "Mean"},
      {value: "histogram", label: "Histogram"},
      {value: "quantile", label: "Quantile"},
      {value: "count", label: "Count"}
    ],
    selectedStatistic: null,
    validationError: false,
    validationErrorMsg: null,
    editedItemDialog: {
      statistic: "",
      label: "",
      variable: [],
      epsilon: "",
      delta: '0.0',
      error: "",
      missingValuesHandling: "",
      handleAsFixed: false,
      fixedValue: 0,
      locked: false,
      accuracy: {value: null, message: null}
    },
    missingValuesHandling: [
      // "Drop them", remove this for now, until the library can use it
      {value: "insert_random", label: "Insert random value"},
      {value: "insert_fixed", label: "Insert fixed value"}
    ]
  }),
  methods: {
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
        // "variable" property may be a string (edit mode)
        // or an array of strings (create mode)
        if (typeof this.editedItemDialog.variable === 'string' ||
            this.editedItemDialog.variable instanceof String) {
          duplicates = this.isMatchingStatistic(this.editedItemDialog.variable)
        } else {
          this.editedItemDialog.variable.forEach((variable) => {
            // Check for duplicate in the current statistics list
            if (this.isMatchingStatistic(variable)) {
              duplicates = true
            }
          })

        }
      }
      return duplicates
    },
    isMatchingStatistic(variable) {
      let isMatching = false
      this.statistics.forEach((stat) => {
        if (stat.statistic === this.editedItemDialog.statistic
            && stat.variable === variable
            && stat.missingValuesHandling === this.editedItemDialog.missingValuesHandling
            && stat.fixedValue === this.editedItemDialog.fixedValue) {
          isMatching = true
        }
      })
      return isMatching
    },

    validateStatistics() {
      // create a local list that
      // includes the statistic the user wants to add or edit
      let tempStats = JSON.parse(JSON.stringify(this.statistics))
      if (this.editedIndex > -1) {
        tempStats[this.editedIndex] = this.editedItemDialog
      } else {
        this.editedItemDialog.variable.forEach((variable) => {
          const label = variable
          const cl = this.getDepositorSetupInfo.confidenceLevel
          tempStats.push(Object.assign({}, this.editedItemDialog, {variable}, {label}, {cl})
          );
        })
      }
      createStatsUtils.redistributeValue(this.getDepositorSetupInfo.epsilon, 'epsilon', tempStats)
      createStatsUtils.redistributeValue(this.getDepositorSetupInfo.delta, 'delta', tempStats)
      return createStatsUtils.releaseValidation(this.analysisPlan.objectId, tempStats)
          .then((validateResults) => {
            this.validationErrorMsg = validateResults.data
            return validateResults.valid
          })


    },

    close() {
      this.validationError = false
      this.validationErrorMsg = ""
      this.$emit("close");
    },
    updateSelectedVariable(variable, index) {
      if (this.editedItemDialog.variable.includes(variable)) {
        this.editedItemDialog.variable.splice(index, 1);
      }
    },
    updateSelectedStatistic(statistic) {
      this.selectedStatistic = statistic
    },
    updateFixedInputVisibility(handlingOption) {
      this.editedItemDialog.handleAsFixed =
          handlingOption.label === "Insert fixed value";
    }
  }
};
</script>
