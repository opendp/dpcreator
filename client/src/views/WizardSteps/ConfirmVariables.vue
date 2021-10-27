<template>
  <div class="confirmVariablesPage">
    <h1 class="title-size-1">Confirm Variables</h1>
    <p v-html="$t('confirm variables.confirm variables intro')"></p>
    <ColoredBorderAlert type="warning">
      <template v-slot:content>
        The DPcreator takes the first 20 variables of the dataset. The default
        type has been inferred from the dataset. Incorrect type labeling can
        result in privacy violation.
      </template>
    </ColoredBorderAlert>
    <ColoredBorderAlert type="info" icon="mdi-shield-half-full">
      <template v-slot:content>
        Any changes will be applied for the purpose of creating the differential
        privacy release only, and will <strong>not affect </strong>the original
        data file. dataset. Incorrect type labeling can result in privacy
        violation.
      </template>
    </ColoredBorderAlert>

    <v-data-table
        :headers="headers"
        :items="variables"
        class="my-10"
        :items-per-page="20"
        :loading="loadingVariables"
        :hide-default-footer="true"
    >
      <template v-slot:loading>
        <LoadingBar v-for="i in 20" :key="i"/>
      </template>
      <template v-slot:[`header.type`]="{ header }">
        {{ header.text }}
        <DynamicQuestionIconTooltip
            locale-tag="confirm variables.help type"
        />
      </template>
      <template v-slot:[`header.additional_information`]="{ header }">
        {{ header.text }}
        <DynamicQuestionIconTooltip
            locale-tag="confirm variables.help variable"
        />
      </template>
      <template v-slot:[`item.index`]="{ index }">
        <span class="index-td grey--text">{{ index + 1 }}</span>
      </template>
      <template v-slot:[`item.label`]="{ item }">
        <div v-if="item.editDisabled">
          <span>{{ item.label }}</span>
          <v-icon right @click="item.editDisabled = !item.editDisabled">
            mdi-pencil
          </v-icon>
        </div>
        <v-text-field
            v-else
            v-model="item.label"
            type="text"
            :readonly="item.editDisabled"
            :append-outer-icon="'mdi-check'"
            @click:append-outer="item.editDisabled = !item.editDisabled"
            v-on:change="saveUserInput(item)"
        ></v-text-field>
      </template>
      <template v-slot:[`item.type`]="{ item }">
            <v-select
                v-if="showToolTip(item)"
                v-model="item.type"
                :items="['Numerical', 'Categorical', 'Boolean']"
                standard
                v-tooltip="'Changing type will clear additional info.'"
                hide-selected
                class="d-inline-block select"
                v-on:click="currentRow=item.index"
                v-on:hover="currentRow=item.index"
                dense
                v-on:change="saveUserInput(item)"
            ></v-select>
        <v-select
            v-else
            v-model="item.type"
            :items="['Numerical', 'Categorical', 'Boolean']"
            standard
            hide-selected
            class="d-inline-block select"
            v-on:click="currentRow=item.index"
            v-on:hover="currentRow=item.index"
            dense
            v-on:change="saveUserInput(item)"
        ></v-select>
      </template>

      <template v-slot:[`item.additional_information`]="{ item: variable }">
        <div v-if="variable.type === 'Categorical'">
          <v-combobox
              v-model="variable.additional_information['categories']"
              chips
              label="Add categories"
              multiple
              class="my-0 py-0"
              background-color="soft_primary my-0"
              v-on:click="currentRow=variable.index"
              v-on:change="saveUserInput(variable)"
          >
            <template v-slot:selection="{ attrs, item, select, selected }">
              <ChipSelectItem
                  :v_bind="attrs"
                  :input_value="selected"
                  :click="select"
                  :click_close="() => removeCategoryFromVariable(item, variable)"
                  :item="item"
              />
            </template>
          </v-combobox>
        </div>
        <div v-if="variable.type === 'Numerical'" class="range-input-wrapper">
          <v-text-field
              background-color="soft_primary mb-0"
              type="number"
              label="Add min"
              v-model="variable.additional_information['min']"
              class="text-center py-0"
              :rules="[checkMin]"
              :data-test="variable.label+':min'"

              v-on:click="currentRow=variable.index"
              v-on:change="saveUserInput(variable)"
          ></v-text-field>
          <v-text-field
              background-color="soft_primary mb-0"
              type="number"
              label="Add max"
              :rules="[checkMax]"
              :data-test="variable.label+':max'"
              v-model="variable.additional_information['max']"
              class="text-center py-0"
              v-on:click="currentRow=variable.index"
              v-on:change="saveUserInput(variable)"
          ></v-text-field>
        </div>
      </template>
    </v-data-table>
  </div>
</template>

<style lang="scss">
.confirmVariablesPage {
  thead .v-data-table__progress {
    display: none;
  }

  th {
    color: inherit !important;
    border-bottom-color: black !important;
  }

  .v-data-table > .v-data-table__wrapper > table > thead > tr > th {
    font-size: 0.875rem;
  }

  .v-data-table > .v-data-table__wrapper > table > tbody > tr > td {
    height: 60px;
  }

  input {
    font-size: 0.875rem;
  }

  .v-text-field__details {
    display: none;
  }

  .index-td {
    color: rgba(0, 0, 0, 0.6);
    font-weight: 600;
    font-size: 0.75rem;
  }

  .v-label--active {
    display: none;
  }

  .range-input-wrapper {
    display: grid;
    grid-template-columns: 47.5% 47.5%;
    grid-gap: 5%;
    input {
      text-align: center;
    }
    .v-label:not(.v-label--active) {
      width: 100%;
      padding-left: 20px;
    }
  }
  .v-select__slot {
    padding-left: 20px;
  }
  div[role="combobox"] {
    .v-input__append-inner {
      display: none;
    }
    .v-label:not(.v-label--active) {
      left: unset !important;
      top: unset !important;
    }
  }
  .v-input__control {
    border-top-left-radius: 5px !important;
    border-top-right-radius: 5px !important;
  }
}
</style>

<script>
import QuestionIconTooltip from "../../components/DynamicHelpResources/QuestionIconTooltip.vue";
import ColoredBorderAlert from "../../components/DynamicHelpResources/ColoredBorderAlert.vue";
import LoadingBar from "../../components/LoadingBar.vue";
import ChipSelectItem from "../../components/DesignSystem/ChipSelectItem.vue";
import DynamicQuestionIconTooltip from "@/components/DynamicHelpResources/DynamicQuestionIconTooltip";
import {mapState, mapGetters} from 'vuex';

export default {
  name: "ConfirmVariables",
  components: {
    LoadingBar,
    QuestionIconTooltip,
    DynamicQuestionIconTooltip,
    ColoredBorderAlert,
    ChipSelectItem
  },
  props: ["stepperPosition"],
  computed: {
    ...mapState('auth', ['error', 'user']),
    ...mapState('dataset', ['datasetInfo']),
    ...mapGetters('dataset', ['getDepositorSetupInfo']),
    showMessage: function () {
      if (this.currentRow !== null) {
        return this.variables[this.currentRow].additional_information.max !== null
            && this.variables[this.currentRow].type == 'Numerical'
      } else {
        return false;
      }
    }
  },
  created: function () {
    if (this.datasetInfo.depositorSetupInfo.variableInfo !== null) {
      this.createVariableList()
    }
  },

  data: () => ({
    currentRow: null,
    loadingVariables: true,
    headers: [
      {value: "index"},
      {text: "Variable name", value: "name"},
      {text: "Variable label", value: "label"},
      {text: "Type", value: "type"},
      {
        text: "Additional variable information",
        value: "additional_information"
      }
    ],
    variables: []
  }),
  methods: {
    checkMin(value) {
      if (this.currentRow !== null) {
        const currentMax = this.variables[this.currentRow].additional_information.max
        if (currentMax !== null && currentMax < Number(value)) {
          return false
        }
      }
      return true
    },
    checkMax(value) {
      if (this.currentRow !== null) {
        const currentMin = this.variables[this.currentRow].additional_information.min
        if (currentMin !== null && currentMin > Number(value)) {
          return false
        }
      }
      return true
    },
    showToolTip(item) {
      console.log('isNumeric ' + item.type)
      return item.type == 'Numerical' && (item.additional_information.max !== null || item.additional_information.min !== null)
    },
    isValidRow(variable) {
      let minmaxValid = true
      if (variable.type == 'Numerical') {
        if (variable.additional_information.max !== null && variable.additional_information.min !== null) {
          minmaxValid = (Number(variable.additional_information.min) < Number(variable.additional_information.max))
        }
      }
      const valid = (variable.name !== null && minmaxValid)
      return valid
    },
    removeCategoryFromVariable(category, variable) {
      variable.additional_information["categories"].splice(
          variable.additional_information["categories"].indexOf(category),
          1
      );
      this.saveUserInput(variable)
    },
    // Create a list version of variableInfo. A deep copy, so we can edit locally
    createVariableList() {
      let vars = this.datasetInfo.depositorSetupInfo.variableInfo
      let index = 0;
      for (const key in vars) {
        let row = {}
        row.index = index
        row.key = key
        row.name = vars[key].name
        row.type = vars[key].type
        if (vars[key].label === '') {
          row.label = vars[key].name
        } else {
          row.label = vars[key].label
        }
        row.additional_information = {}
        if (row.type === 'Numerical') {
          row.additional_information.max = vars[key].max
          row.additional_information.min = vars[key].min
        }
        if (row.type === 'Categorical') {
          // make a deep copy of the categories, so we can edit locally
          row.additional_information.categories = JSON.parse(JSON.stringify(vars[key].categories))
        }
        row['editDisabled'] = true
        this.variables.push(row)
        index += 1
      }
      this.loadingVariables = false
    },
    saveUserInput(elem) {
      if (this.isValidRow(elem)) {
        this.$store.dispatch('dataset/updateVariableInfo', elem)
      }

    },

  },
  /**
   * Watch for the variableInfo object to be populated by the Run Profiler action.
   * When it is populated, create a local variableList for the data table
   */
  watch: {
    '$store.state.dataset.datasetInfo': function () {
      if (this.datasetInfo.depositorSetupInfo.variableInfo !== null) {
        // the watch will be triggered multiple times,
        // so check if we have already created the variableList
        if (this.variables.length === 0) {
          this.createVariableList()
        } else {
          this.loadingVariables = false
        }
      }
    },
    // If additional information has been added for all variables, then
    // send stepCompleted event to the wizard (will enable the continue button
    variables: function (newValue) {
      // for now, for ease of use, we will not require additional info for all variables.
      // TODO: add validation later, or make it conditional to running in dev mode
      this.$emit("stepCompleted", 1, true);
      //  }
    }

  }
};
</script>
