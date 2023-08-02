<template>
  <div class="confirmVariablesPage">
    <h1 class="title-size-1">Confirm Variables</h1>
    <p v-html="$t('confirm variables.confirm variables intro')"></p>
    <ColoredBorderAlert type="warning">
      <template v-slot:content>
        Currently, the DP Creator takes the first 20 variables of the data file.
      </template>
    </ColoredBorderAlert>
    <ColoredBorderAlert type="info" icon="mdi-shield-half-full">
      <template v-slot:content>
        Any changes will be applied for the purpose of creating the differential
        privacy release only, and will <strong>not affect</strong> the original
        data file.
      </template>
    </ColoredBorderAlert>
    <v-text-field
        v-model="search"
        append-icon="mdi-magnify"
        label="Search Variables"
        single-line
        hide-details
    ></v-text-field>

    <Checkbox v-if="allowSelectAll"
        data-test="filterCheckBox"
        :class="{ 'width80 mx-auto': $vuetify.breakpoint.xsOnly }"
        :value.sync="filterSelected"
        text='Show Only Selected Variables'
    />

    <v-data-table
        :headers="headers"
        :search="search"
        data-test="variableTable"
        v-model="selected"
        :items="items"
        class="my-10"
        :items-per-page="20"
        :loading="loadingVariables"
        :hide-default-footer="true"
        :single-select="false"
        item-key="name"
        show-select
        v-on:toggle-select-all="handleSelectAll"
        v-on:item-selected="handleItemSelected"
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
      <!--
      <template v-slot:item.data-table-select="{ on, props }">
        <v-simple-checkbox color="green" v-bind="props" v-on="on"></v-simple-checkbox>
      </template>-->
      <template v-slot:[`item.valid`]="{ item }">
        <div v-if="!isValidRow(item)">
          <v-icon color="red">mdi-alert</v-icon>
        </div>

      </template>

      <template v-slot:[`item.index`]="{ index }">
        <span data-test="variableRow" class="index-td grey--text">{{ index + 1 }}</span>
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
            :items="['Float', 'Integer', 'Categorical', 'Boolean']"
            :data-test="item.label+':selectToolTip'"
            standard
            v-tooltip="'Changing type will clear additional info.'"
            class="d-inline-block select"
            v-on:click="currentRow=item.index"
            v-on:hover="currentRow=item.index"
            dense
            v-on:change="changeVariableType(item)"
        ></v-select>
        <v-select
            v-else
            v-model="item.type"
            :items="['Float', 'Integer', 'Categorical', 'Boolean']"
            :data-test="item.label+':select'"
            standard
            class="d-inline-block select"
            v-on:click="currentRow=item.index"
            v-on:hover="currentRow=item.index"
            dense
            v-on:change="changeVariableType(item)"
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
              :data-test="variable.label+':categories'"
              v-on:click="currentRow=variable.index"
              :search-input.sync="categoryInput"
              @change="changeCategories(variable)"
              @update:search-input="delimitInput(variable)"
              :delimiters="[',']"
          >
            <template v-slot:selection="{ attrs, item, select, selected }">
              <v-chip
                  :v-bind="attrs"
                  :input-value="selected"
                  close
                  color="blue darken-2"
                  text-color="white"
                  :click="select"
                  :item="item"

                  @click:close="removeCategoryFromVariable(item, variable)"
              >
                <div data-test="categoryChip"><strong>{{ item }}
                  <!--{{ 'attrs:'+ JSON.stringify(attrs) }}{{ 'select:' +select }}{{ 'selected'+selected }}-->
                </strong></div>
              </v-chip>
            </template>
          </v-combobox>
        </div>
        <div v-if="isNumerical(variable.type)" class="range-input-wrapper">
          <v-text-field
              background-color="soft_primary mb-0"
              label="Add min"
              v-model="variable.additional_information['min']"
              class="text-center py-0"
              :rules="[checkMin]"
              :data-test="variable.label+':min'"

              v-on:click="currentRow=variable.index"
              v-on:keyup="saveUserInput(variable)"
          ></v-text-field>
          <v-text-field
              background-color="soft_primary mb-0"
              label="Add max"
              :rules="[checkMax]"
              :data-test="variable.label+':max'"
              v-model="variable.additional_information['max']"
              class="text-center py-0"
              v-on:click="currentRow=variable.index"
              v-on:keyup="saveUserInput(variable)"
          ></v-text-field>
        </div>
        <div v-if="variable.type==='Boolean'" class="range-input-wrapper">
          <v-text-field
              background-color="soft_primary mb-0"
              label="Add true value"
              v-model="variable.additional_information['trueValue']"
              class="text-center py-0"
              :data-test="variable.label+':trueValue'"
              :ref="variable.label+':trueValue'"
              v-on:click="currentRow=variable.index"
              v-on:keyup="saveUserInput(variable)"
          ></v-text-field>
          <v-text-field
              background-color="soft_primary mb-0"
              label="Add false value"
              :data-test="variable.label+':falseValue'"
              v-model="variable.additional_information['falseValue']"
              :ref="variable.label+':falseValue'"
              class="text-center py-0"
              v-on:click="currentRow=variable.index"
              v-on:keyup="saveUserInput(variable)"
          ></v-text-field>
        </div>
      </template>
    </v-data-table>
    <div v-if="selected.length == 0">
      <ColoredBorderAlert type="warning">
        <template v-slot:content>
          Please select at least one variable to continue.
        </template>
      </ColoredBorderAlert>
    </div>
    <div v-if="!formCompleted(variables)">
      <ColoredBorderAlert type="warning">
        <template v-slot:content>
          Please fix missing or invalid input to continue.
        </template>
      </ColoredBorderAlert>
    </div>
  </div>
</template>

<style lang="scss">
.tooltip {
  display: block !important;
  z-index: 10000;
}

.tooltip .tooltip-inner {
  background: gray;
  color: white;
  border-radius: 16px;
  padding: 5px 10px 4px;
}

.tooltip .tooltip-arrow {
  width: 0;
  height: 0;
  border-style: solid;
  position: absolute;
  margin: 5px;
  border-color: black;
  z-index: 1;
}

.tooltip[x-placement^="top"] {
  margin-bottom: 5px;
}

.tooltip[x-placement^="top"] .tooltip-arrow {
  border-width: 5px 5px 0 5px;
  border-left-color: transparent !important;
  border-right-color: transparent !important;
  border-bottom-color: transparent !important;
  bottom: -5px;
  left: calc(50% - 5px);
  margin-top: 0;
  margin-bottom: 0;
}

.tooltip[x-placement^="bottom"] {
  margin-top: 5px;
}

.tooltip[x-placement^="bottom"] .tooltip-arrow {
  border-width: 0 5px 5px 5px;
  border-left-color: transparent !important;
  border-right-color: transparent !important;
  border-top-color: transparent !important;
  top: -5px;
  left: calc(50% - 5px);
  margin-top: 0;
  margin-bottom: 0;
}

.tooltip[x-placement^="right"] {
  margin-left: 5px;
}

.tooltip[x-placement^="right"] .tooltip-arrow {
  border-width: 5px 5px 5px 0;
  border-left-color: transparent !important;
  border-top-color: transparent !important;
  border-bottom-color: transparent !important;
  left: -5px;
  top: calc(50% - 5px);
  margin-left: 0;
  margin-right: 0;
}

.tooltip[x-placement^="left"] {
  margin-right: 5px;
}

.tooltip[x-placement^="left"] .tooltip-arrow {
  border-width: 5px 0 5px 5px;
  border-top-color: transparent !important;
  border-right-color: transparent !important;
  border-bottom-color: transparent !important;
  right: -5px;
  top: calc(50% - 5px);
  margin-left: 0;
  margin-right: 0;
}

.tooltip.popover .popover-inner {
  background: #f9f9f9;
  color: black;
  padding: 24px;
  border-radius: 5px;
  box-shadow: 0 5px 30px rgba(black, .1);
}

.tooltip.popover .popover-arrow {
  border-color: #f9f9f9;
}

.tooltip[aria-hidden='true'] {
  visibility: hidden;
  opacity: 0;
  transition: opacity .15s, visibility .15s;
}

.tooltip[aria-hidden='false'] {
  visibility: visible;
  opacity: 1;
  transition: opacity .15s;
}

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
import Checkbox from "../../components/DesignSystem/Checkbox.vue";
import DynamicQuestionIconTooltip from "@/components/DynamicHelpResources/DynamicQuestionIconTooltip";
import {mapGetters, mapState} from 'vuex';

export default {
  name: "ConfirmVariables",
  components: {
    LoadingBar,
    QuestionIconTooltip,
    DynamicQuestionIconTooltip,
    ColoredBorderAlert,
    ChipSelectItem,
    Checkbox
  },
  props: ["stepperPosition","variableList", "allowSelectAll"],
  computed: {
    ...mapState('auth', ['error', 'user']),
    ...mapState('dataset', ['datasetInfo', 'analysisPlan']),
    ...mapGetters('dataset', ['getDepositorSetupInfo']),

  },
  created: function () {
    if (this.variableList !== null) {
      this.createVariableList()
    }
  },

  data: () => ({
    currentRow: null,
    loadingVariables: true,
    search: "",
    categoryInput: "",
    headers: [
      {value: "valid"},
      {value: "index"},
      {text: "Variable Name", value: "name"},
      {text: "Variable Label", value: "label"},
      {text: "Type", value: "type"},
      {
        text: "Additional Variable Information",
        value: "additional_information"
      }
    ],
    items: [],
    variables: [],
    selected: [],
    filterSelected: false
  }),

  methods: {
    getItems() {
      if (this.filterSelected) {
        return this.variables.filter(obj => {
          return obj.selected === true;
        });
      } else {
        return this.variables
      }
    },
    changeCategories(variable) {
      //  console.log('category change: ' + JSON.stringify(variable) +','+this.categoryInput)
      this.saveUserInput(variable)
    },
    delimitInput(variable) {
      if (this.categoryInput && this.categoryInput.split(",").length > 1) {
        let v = JSON.parse(JSON.stringify(variable.additional_information.categories))
        v.push(this.categoryInput)
        const reducer = (a, e) => [...a, ...e.split(',')]
        let categories = [...new Set(v.reduce(reducer, []))]
        categories = categories.filter(word => word.length > 0);

        variable.additional_information.categories = JSON.parse(JSON.stringify(categories))
        this.saveUserInput(variable)
        this.categoryInput = ""
      }
    },
    formCompleted(varList) {
      let completed = true
      varList.forEach(row => {
        if (!this.isValidRow(row)) {
          completed = false
        }
      })
      return completed
    },
    handleItemSelected(event) {
      this.variables[event.item.sortOrder].selected = event.value
      this.items = this.getItems()
      this.saveUserInput(this.variables[event.item.sortOrder])
    },
    handleSelectAll(event) {
      const selectAllValue = event.value
      this.variables.forEach(obj => obj.selected = selectAllValue)
      this.items = this.getItems()
      this.saveAllVariables(selectAllValue)
    },
    checkMin(value) {
      if (isNaN(value)) {
        return false
      }
      if (this.currentRow !== null) {
        if (this.variables[this.currentRow].additional_information !== undefined) {
          const currentMax = this.variables[this.currentRow].additional_information.max
          if (currentMax !== null && currentMax < Number(value)) {
            return false
          }
        }
      }
      return true
    },
    checkMax(value) {
      let valid = true
      if (isNaN(value)) {
        valid = false
      }
      if (this.currentRow !== null) {
        if (this.variables[this.currentRow].additional_information !== undefined) {
          const currentMin = this.variables[this.currentRow].additional_information.min
          if (currentMin !== null && currentMin > Number(value)) {
            valid = false
          }
        }
      }
      return valid
    },
    checkTrueValue(value) {
      // If falseValue has been entered, then trueValue is required, and cannot be the same as false value
      let valid = true
      if (this.currentRow !== null) {
        if (this.variables[this.currentRow].additional_information !== undefined) {
          const falseValue = this.variables[this.currentRow].additional_information.falseValue
          if (falseValue !== undefined && falseValue !== null
              && (value === null || value.trim() === '' || value === falseValue)) {
            valid = false
          }
        }

      }

      return valid
    },

    checkFalseValue(value) {
      //  False value is not required, but if it is entered it cannot be the same as true value
      let valid = true
      if (this.currentRow !== null) {
        if (this.variables[this.currentRow].additional_information !== undefined) {
          const trueValue = this.variables[this.currentRow].additional_information.trueValue
          console.log('checkFalseValue,value parameter = ' + value + ", falseValue =" + this.variables[this.currentRow].additional_information.falseValue)
          if (trueValue !== undefined && trueValue !== null && value === trueValue) {
            valid = false
          }
          if (valid) {
            const refName = this.variables[this.currentRow].label + ':trueValue'
            this.$refs[refName].validate()
          }
        }
      }
      return valid
    },
    isNumerical(type) {
      return type === 'Float' || type === 'Integer'
    },
    showToolTip(item) {
      const show = (this.isNumerical(item.type) && (item.additional_information.max !== null
          || item.additional_information.min !== null))
          || (item.type === 'Categorical' && (item.additional_information.categories !== null
              && item.additional_information.categories.length > 0))
      return show
    },
    isBlank(str) {
      return (!str || /^\s*$/.test(str));
    },
    isSelectable(variable) {
      let selectable = true
      if (this.analysisPlan && this.analysisPlan.dpStatistics) {
        this.analysisPlan.dpStatistics.forEach(statistic => {
          if (statistic.variable === variable.key) {
            selectable = false
          }
        })
      }

      return selectable
    },
    isValidRow(variable) {
      // We only need to check selected rows,
      // so if row isn't selected it's always valid
      if (!variable.selected) {
        return true
      } else {
        let minmaxValid = true
        let catValid = true
        let booleanValid = true
        if (this.isNumerical(variable.type)) {
          if (this.isBlank(variable.additional_information.min)
              || this.isBlank(variable.additional_information.max)
          ) {
            minmaxValid = false
          } else {
            minmaxValid = (Number(variable.additional_information.min) < Number(variable.additional_information.max))
          }
        }
        if (variable.type === 'Boolean') {
          if (variable.additional_information == null
              || variable.additional_information !== null && (
                  (this.isBlank(variable.additional_information.trueValue) || this.isBlank(variable.additional_information.falseValue))
                  || (variable.additional_information.trueValue === variable.additional_information.falseValue))
          ) {
            booleanValid = false
          }
        }

        if (variable.type === 'Categorical' &&
            (variable.additional_information === 'undefined'
                || variable.additional_information.categories === 'undefined'
                || variable.additional_information.categories === null
                || variable.additional_information.categories.length === 0)) {
          catValid = false
        }
        const valid = (variable.name !== null && minmaxValid && catValid && booleanValid)
        return valid
      }
    },
    removeCategoryFromVariable(category, variable) {
      variable.additional_information["categories"].splice(
          variable.additional_information["categories"].indexOf(category),
          1
      );
      this.saveUserInput(variable)
    },
    // This is run so that as statistics are added, variables are set to unselectable
    updateSelectable() {
      this.variables.forEach(variable => {
        variable.isSelectable = this.isSelectable(variable)
      })
    },
    // Create a list version of variableInfo. A deep copy, so we can edit locally
    createVariableList() {
      let vars = this.variableList
      for (const key in vars) {
        let row = {}
        row.key = key
        row.name = vars[key].name
        row.type = vars[key].type
        row.sortOrder = vars[key].sortOrder
        if (vars[key].selected === undefined) {
          row.selected = false
        } else {
          row.selected = vars[key].selected
        }
        if (vars[key].label === '') {
          row.label = vars[key].name
        } else {
          row.label = vars[key].label
        }
        row.additional_information = {}
        if (this.isNumerical(row.type)) {
          // Min and max are stored as ints, but the form expects them to be strings
          if (vars[key].max !== undefined && vars[key].max !== null) {
            row.additional_information.max = vars[key].max.toString()
          }
          if (vars[key].min !== undefined && vars[key].min !== null) {
            row.additional_information.min = vars[key].min.toString()
          }
        }
        if (row.type === 'Categorical') {
          // make a deep copy of the categories, so we can edit locally
          row.additional_information.categories = JSON.parse(JSON.stringify(vars[key].categories))
        }
        if (row.type === 'Boolean') {
          row.additional_information.trueValue = vars[key].trueValue
          row.additional_information.falseValue = vars[key].falseValue
        }
        row['editDisabled'] = true
        row['isSelectable'] = this.isSelectable(vars[key])
        if (row.selected) {
          this.selected.push(row)
        }
        this.variables.push(row)
      }
      // Order variables by sortOrder returned from the server
      this.variables = this.variables.sort((a, b) => (a.sortOrder > b.sortOrder) ? 1 : -1)

      for (let i = 0; i < this.variables.length; i++) {
        this.variables[i].index = i
      }
      this.items = this.getItems()
      this.loadingVariables = false
      this.updateStepCompleted(this.variables, this.selected.length > 0)
    },

    changeVariableType(elem) {
      elem.additional_information.categories = []
      elem.additional_information.max = null
      elem.additional_information.min = null
      this.saveUserInput(elem)
    },
    saveUserInput(elem) {
      // make a deep copy so that the form doesn't share object references with the Vuex data
      const elemCopy = JSON.parse(JSON.stringify(elem))
      if (this.formCompleted(this.variables) && this.isValidRow(elem) && this.atLeastOneSelected(elem)) {
        this.$emit("stepCompleted", 1, true);
      } else {
        this.$emit("stepCompleted", 1, false);
      }
      console.log('emitting updateVariable')
      this.$emit("updateVariable", elem)
    },
    updateStepCompleted(varList, anySelected) {
      if (this.formCompleted(varList) && anySelected) {
        this.$emit("stepCompleted", 1, true);
      } else {
        this.$emit("stepCompleted", 1, false);
      }
    },
    saveAllVariables(selectAllValue) {
      const varsCopy = JSON.parse(JSON.stringify(this.variables))
      this.$emit("updateAllVariables", varsCopy)
      this.updateStepCompleted(this.variables, selectAllValue)
    },
    atLeastOneSelected(elem) {
      let othersSelected = false
      this.selected.forEach(row => {
        if (row.index !== elem.index) {
          othersSelected = true
        }
      })
      return elem.selected || othersSelected
    }
  },
  /**
   * Watch for the variableInfo object to be populated by the Run Profiler action.
   * When it is populated, create a local variableList for the data table
   */
  watch: {
    filterSelected: function (newFilterValue) {
      this.items = this.getItems()
      this.filterSelected = newFilterValue
    },
    variables: function() {
      if (this.items === []) {
        this.items = this.getItems()
      }
    },
    variableList: function () {
      if (this.variableList !== null) {
        // the watch will be triggered multiple times,
        // so check if we have already created the variableList
        if (this.variables.length === 0) {
          this.createVariableList()
        } else {
          this.loadingVariables = false
        }
      }
    },
    '$store.state.dataset.analysisPlan': function () {
      if (this.analysisPlan.variableInfo !== null) {
        this.updateSelectable()

      }
    }
  },


};
</script>