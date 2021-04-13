<template>
  <v-dialog width="66%" v-model="dialog" @click:outside="close">
    <v-card elevation="2" class="px-10 py-12 add-statistic-dialog">
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
                v-for="statistic in singleVariableStatistics"
                :key="statistic"
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
                v-for="variable in variables"
                :key="variable"
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
                v-for="handlingOption in missingValuesHandling"
                :key="handlingOption"
                :label="handlingOption"
                :value="handlingOption"
                on-icon="mdi-check"
                @click="
                editedItemDialog.handleAsFixed =
                  handlingOption === 'Insert fixed value'
              "
            ></v-radio>
          </v-radio-group>
        </div>

        <div v-if="editedItemDialog.handleAsFixed">
          <span>Enter your <strong> fixed value:</strong></span>
          <div class="width50">
            <v-text-field
                v-model="editedItemDialog.fixedValue"
                placeholder="E.g. Lorem ipsum"
                background-color="blue lighten-4"
                class="top-borders-radius width50"
            ></v-text-field>
          </div>
        </div>
      </v-card-text>

      <v-card-actions>
        <v-btn
            color="primary"
            class="mr-2 px-5"
            @click="save"
            :disabled="isButtonDisabled"
        >
          Save
        </v-btn>
        <v-btn color="primary" outlined class="px-5" @click="close">
          Cancel
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<style lang="scss">
.add-statistic-dialog {
  @import "~vuetify/src/styles/main.sass";

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
      border: 1px solid map-get($map: $blue, $key: darken-2);
      padding: 5px 20px;

      &:hover,
      &.v-item--active {
        background: map-get($map: $blue, $key: darken-2);

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
        color: map-get($map: $blue, $key: darken-2);
        font-weight: 700;
        justify-content: center;
      }
    }
  }
}
</style>

<script>
export default {
  name: "AddStatisticDialog",
  props: ["formTitle", "dialog", "editedIndex", "editedItem"],
  computed: {
    isButtonDisabled: function () {
      return (
          !this.editedItemDialog.statistic ||
          !this.editedItemDialog.variable ||
          !this.editedItemDialog.missingValuesHandling
      );
    }
  },
  watch: {
    editedItem: function (newEditedItem) {
      this.editedItemDialog = Object.assign({}, newEditedItem);
    }
  },
  data: () => ({
    singleVariableStatistics: ["Mean", "Histogram", "Quantile"],
    variables: ["Age", "Sex", "Educ", "Race", "Income", "Married"],
    editedItemDialog: {
      statistic: "",
      variable: [],
      epsilon: "",
      error: "",
      missingValuesHandling: "",
      handleAsFixed: false,
      fixedValue: "0"
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
    }
  }
};
</script>
