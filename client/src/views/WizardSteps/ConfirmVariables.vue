<template>
  <div class="confirmVariablesPage">
    <h1 class="title-size-1">Confirm variables</h1>
    <p>
      {{ $t('confirm variables.confirm variables intro') }}
    </p>
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
      <template v-slot:[`item.name`]="{ item }">
        <div v-if="item.editDisabled">
          <span>{{ item.name }}</span>
          <v-icon right @click="item.editDisabled = !item.editDisabled">
            mdi-pencil
          </v-icon>
        </div>
        <v-text-field
            v-else
            v-model="item.name"
            type="text"
            :readonly="item.editDisabled"
            :append-outer-icon="'mdi-check'"
            @click:append-outer="item.editDisabled = !item.editDisabled"
        ></v-text-field>
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
          ></v-text-field>
          <v-text-field
              background-color="soft_primary mb-0"
              type="number"
              label="Add max"
              v-model="variable.additional_information['max']"
              class="text-center py-0"
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
export default {
  name: "ConfirmVariables",
  components: {
    LoadingBar,
    QuestionIconTooltip,
    DynamicQuestionIconTooltip,
    ColoredBorderAlert,
    ChipSelectItem
  },
  mounted: function () {
    setTimeout(() => {
      this.loadingVariables = false;
      this.variables = [
        {
          name: "V207",
          label: "Birth Year",
          type: "Numerical",
          additional_information: {},
          editDisabled: true
        },
        {
          name: "V208",
          label: "Gender",
          type: "Categorical",
          additional_information: {},
          editDisabled: true
        },
        {
          name: "V246",
          label: "Household Income",
          type: "Categorical",
          additional_information: {},
          editDisabled: true
        },
        {
          name: "V211",
          label: "Race",
          type: "Categorical",
          additional_information: {},
          editDisabled: true
        },
        {
          name: "V214",
          label: "Marital Status",
          type: "Categorical",
          additional_information: {},
          editDisabled: true
        },

        {
          name: "V259",
          label: "State",
          type: "Categorical",
          additional_information: {},
          editDisabled: true
        },
        {
          name: "V256",
          label: "Voted 2016",
          type: "Boolean",
          additional_information: {},
          editDisabled: true
        },
      ];
      this.$emit("stepCompleted", 1, true);
    }, 3000);
  },
  data: () => ({
    loadingVariables: true,
    filename: "California Demographic Dataset",
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
    removeCategoryFromVariable: (category, variable) => {
      variable.additional_information["categories"].splice(
          variable.additional_information["categories"].indexOf(category),
          1
      );
    }
  }
};
</script>
