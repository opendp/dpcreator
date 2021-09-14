<template>
  <v-dialog
      :width="$vuetify.breakpoint.smAndDown ? '90%' : '50%'"
      v-model="dialog"
      @click:outside="close"
  >
    <v-card elevation="2" class="px-10 py-12 add-statistic-dialog">
      <v-icon style="position: absolute; right: 40px" @click="close"
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
                :label="statistic"
                :value="statistic"
                on-icon="mdi-check"
                @click="() => updateSelectedStatistic(statistic)"
                :data-test="statistic"
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
                :label="handlingOption"
                :value="handlingOption"
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
            ></v-text-field>
          </div>
        </div>

        <ColoredBorderAlert type="warning" v-if="validationError">
          <template v-slot:content>

            <ul v-if="errorCount > 1">
              <li v-if="item.message" v-for="item in validationErrorMsg">
                {{ item.stat.statistic }} / {{ item.stat.variable }}: {{ item.message }}
              </li>
            </ul>
            <div v-if="errorCount==1" v-for="item in validationErrorMsg">
              {{ item.message }}
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
            label="Create statistic"
        />

        <Button
            color="primary"
            outlined
            classes="px-5"
            :click="close"
            label="Close"
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
import statsInformation from "@/data/statsInformation";

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
      return (
          !this.editedItemDialog.statistic ||
          !this.editedItemDialog.variable ||
          !this.editedItemDialog.missingValuesHandling
      );
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
        if ((this.selectedStatistic !== 'Mean') ||
            (this.selectedStatistic === 'Mean' && this.variableInfo[key].type === 'Numerical')) {
          displayVars.push(displayVar)
        }

      }
      return displayVars
    }
  },
  watch: {
    editedItem: function (newEditedItem) {
      this.editedItemDialog = Object.assign({}, newEditedItem);
    }
  },
  data: () => ({
    singleVariableStatistics: ["Mean", "Histogram", "Quantile"],
    selectedStatistic: null,
    validationError: false,
    validationErrorMsg: null,
    editedItemDialog: {
      statistic: "",
      variable: [],
      epsilon: "",
      delta: "",
      error: "",
      missingValuesHandling: "",
      handleAsFixed: false,
      fixedValue: "0",
      locked: false
    },
    missingValuesHandling: [
      "Drop them",
      "Insert random value",
      "Insert fixed value"
    ]
  }),
  methods: {
    save() {
      this.validate().then((valid) => {
        if (valid) {
          this.validationError = false
          this.$emit("saveConfirmed", this.editedItemDialog)
        } else {
          this.validationError = true
        }
      })
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
          tempStats.push(
              Object.assign({}, this.editedItemDialog, {variable}, {label})
          );
        })
      }
      statsInformation.redistributeValue(this.getDepositorSetupInfo.epsilon, 'epsilon', tempStats)
      statsInformation.redistributeValue(this.getDepositorSetupInfo.delta, 'delta', tempStats)
      return release.validate(this.analysisPlan.objectId, tempStats)
          .then((resp) => {
            console.log('validate response: ' + JSON.stringify(resp))
            console.log('validate response: ' + JSON.stringify(resp.data))
            let valid = true
            resp.data.forEach((item, index) => {
              if (item.valid !== true) {
                item.stat = tempStats[index]
                valid = false;
              }
            })
            this.validationErrorMsg = resp.data
            return valid
          })
          .catch((error) => {
            this.validationErrorMsg = [{"valid": false, "message": error}]
            return false
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
          handlingOption === "Insert fixed value";
    }
  }
};
</script>
