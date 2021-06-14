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
            ></v-radio>
          </v-radio-group>
        </div>

        <div>
          <span> Which<strong> variables </strong>would you like to use? </span>
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
                :label="variable"
                :value="variable"
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

export default {
  name: "AddStatisticDialog",
  components: {Button},
  props: ["formTitle", "dialog", "editedIndex", "editedItem"],
  computed: {
    isButtonDisabled: function () {
      return (
          !this.editedItemDialog.statistic ||
          !this.editedItemDialog.variable ||
          !this.editedItemDialog.missingValuesHandling
      );
    },
    isMultiple: function () {
      return this.editedIndex === -1;
    }
  },
  watch: {
    editedItem: function (newEditedItem) {
      this.editedItemDialog = Object.assign({}, newEditedItem);
    }
  },
  //TODO: Define the default epsilon and error values for new statistics
  data: () => ({
    //TODO: These should be connected with the variables loaded on the previous step
    singleVariableStatistics: ["Mean", "Histogram", "Quantile"],
    variables: ["Age", "DOB",
      "Income", "Visit", "Program", "Provider"],
    editedItemDialog: {
      statistic: "",
      variable: [],
      epsilon: "",
      error: "",
      missingValuesHandling: "",
      handleAsFixed: false,
      fixedValue: "0",
      locked: "false"
    },
    missingValuesHandling: [
      "Drop them",
      "Insert random value",
      "Insert fixed value"
    ]
  }),
  methods: {
    save() {
      this.$emit("saveConfirmed", this.editedItemDialog);
    },
    close() {
      this.$emit("close");
    },
    updateFixedInputVisibility(handlingOption) {
      this.editedItemDialog.handleAsFixed =
          handlingOption === "Insert fixed value";
    }
  }
};
</script>
