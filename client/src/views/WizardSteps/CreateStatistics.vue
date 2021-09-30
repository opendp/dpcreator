<template>
  <div id="create-statistics-page">
    <h1 class="title-size-1">Create the statistics</h1>
    <p>
      {{
        $t('create statistics.statistics intro')
      }}
    </p>

    <NoiseParams
        :epsilon="epsilon"
        :delta="delta"
        :confidenceInterval="confidenceInterval"
        v-on:editNoiseParams="dialogEditNoiseParamsConfirmation = true"
    />

    <ColoredBorderAlert type="warning" locale-tag="create statistics.epsilon warning">
    </ColoredBorderAlert>
    <ColoredBorderAlert type="info" locale-tag="create statistics.statistics help">
    </ColoredBorderAlert>

    <StatisticsTable
        :statistics="statistics"
        :total-epsilon="epsilon"
        :total-delta="delta"
        v-on:newStatisticButtonPressed="dialogAddStatistic = true"
        v-on:editStatistic="editItem"
        v-on:editEpsilon="editEpsilon"
        v-on:editDelta="editDelta"
        v-on:changeLockStatus="changeLockStatus"
        v-on:deleteStatistic="deleteItem"
        class="mb-10"
    />

    <AddStatisticDialog
        :variable-info="datasetInfo.depositorSetupInfo.variableInfo"
        :statistics="statistics"
        :formTitle="formTitle"
        :dialog="dialogAddStatistic"
        :editedIndex="editedIndex"
        :editedItem="editedItem"
        v-on:saveConfirmed="save"
        v-on:close="close"
    />
    <DeleteStatisticDialog
        :dialogDelete="dialogDelete"
        :editedItem="editedItem"
        v-on:cancel="closeDelete"
        v-on:confirm="deleteItemConfirm"
    />
    <EditNoiseParamsConfirmationDialog
        v-on:confirm="handleOpenEditNoiseParamsDialog"
        :dialog.sync="dialogEditNoiseParamsConfirmation"
    />
    <EditNoiseParamsDialog
        :dialogEditNoiseParams.sync="dialogEditNoiseParams"
        v-on:noiseParamsUpdated="handleSaveEditNoiseParamsDialog"
        :epsilon="epsilon"
        :delta="delta"
        :confidenceInterval="confidenceInterval"
    />
  </div>
</template>

<style lang="scss">
#create-statistics-page {
  th {
    span {
      color: #000000;
    }

    color: inherit !important;
    border-bottom-color: black !important;
  }

  .v-data-table > .v-data-table__wrapper > table > thead > tr > th {
    font-size: 0.875rem;
  }
}
</style>

<script>
import Decimal from 'decimal.js';
import ColoredBorderAlert from "../../components/DynamicHelpResources/ColoredBorderAlert.vue";
import AddStatisticDialog from "../../components/Wizard/Steps/CreateStatistics/AddStatisticDialog.vue";
import DeleteStatisticDialog from "../../components/Wizard/Steps/CreateStatistics/DeleteStatisticDialog.vue";
import EditNoiseParamsDialog from "../../components/Wizard/Steps/CreateStatistics/EditNoiseParamsDialog.vue";
import EditNoiseParamsConfirmationDialog
  from "../../components/Wizard/Steps/CreateStatistics/EditNoiseParamsConfirmation.vue";
import NoiseParams from "../../components/Wizard/Steps/CreateStatistics/NoiseParams.vue";
import StatisticsTable from "../../components/Wizard/Steps/CreateStatistics/StatisticsTable.vue";
import {mapGetters, mapState} from "vuex";
import createStatsUtils from "@/shared/createStatsUtils";

export default {
  name: "CreateStatistics",
  components: {
    ColoredBorderAlert,
    EditNoiseParamsDialog,
    DeleteStatisticDialog,
    EditNoiseParamsConfirmationDialog,
    AddStatisticDialog,
    StatisticsTable,
    NoiseParams
  },
  props: [
    "stepperPosition"
  ],
  computed: {
    ...mapState('auth', ['error', 'user']),
    ...mapState('dataset', ['datasetInfo', "analysisPlan"]),
    ...mapGetters('dataset', ['getDepositorSetupInfo']),

    formTitle() {
      return this.isEditionMode
          ? "Edit your statistic"
          : "Create your statistic";
    },
    isEditionMode() {
      return this.editedIndex > -1;
    }
  },
  created() {
    this.initializeForm()
  },
  watch: {
    statistics: function (newStatisticsArray) {
      this.$emit("stepCompleted", 3, newStatisticsArray.length !== 0);
    },
    stepperPosition: function (val, oldVal) {
      // If the wizard has landed on the CreateStatistics Step,
      // initialize the form with data from Vuex store
      if (val === 3) {
        this.initializeForm()
      }
    }

  },
  data: () => ({
    epsilon: null,
    delta: null,
    confidenceInterval: null,
    statistics: [],
    dialogAddStatistic: false,
    dialogDelete: false,
    dialogEditNoiseParamsConfirmation: false,
    dialogEditNoiseParams: false,
    editedIndex: -1,
    editedItem: {
      statistic: "",
      variable: [],
      epsilon: "",
      error: "",
      missingValuesHandling: "",
      handleAsFixed: false,
      fixedValue: "0",
      locked: false
    },
    defaultItem: {
      statistic: "",
      variable: [],
      epsilon: "",
      error: "",
      missingValuesHandling: "",
      handleAsFixed: false,
      fixedValue: "0",
      locked: false
    }
  }),
  methods: {
    initializeForm() {
      if (this.analysisPlan !== null && this.analysisPlan.dpStatistics !== null) {
        // make a deep copy of the Vuex state so it can be edited locally
        this.statistics = JSON.parse(JSON.stringify(this.analysisPlan.dpStatistics))
      } else {
        this.statistics = []
      }
      if (this.getDepositorSetupInfo.epsilon == null) {
        this.epsilon = this.getDepositorSetupInfo.defaultEpsilon
      } else {
        this.epsilon = this.getDepositorSetupInfo.epsilon
      }
      if (this.getDepositorSetupInfo.confidenceInterval == null) {
        this.confidenceInterval = .01
      } else {
        this.confidenceInterval = this.getDepositorSetupInfo.confidenceInterval
      }

      if (!createStatsUtils.statisticsUseDelta(this.statistics)) {
        this.delta = 0
      } else if (this.getDepositorSetupInfo.delta == null) {
        this.delta = this.getDepositorSetupInfo.defaultDelta
      } else {
        this.delta = this.getDepositorSetupInfo.delta
      }

    },

    handleOpenEditNoiseParamsDialog() {
      this.dialogEditNoiseParamsConfirmation = false;
      this.dialogEditNoiseParams = true;
    },
    handleSaveEditNoiseParamsDialog(epsilon, delta, confidenceInterval) {
      this.epsilon = epsilon;
      this.delta = delta;
      this.confidenceInterval = confidenceInterval;
      createStatsUtils.redistributeValues(this.statistics, this.delta, this.epsilon, this.getDepositorSetupInfo.defaultDelta)
      // update stats with the accuracy values
      // (we don't have to check validation because that was done in the Dialog)
      createStatsUtils.releaseValidation(this.analysisPlan.objectId, this.statistics)
          .then((validateResults) => {
            for (let i = 0; i < this.statistics.length; i++) {
              this.statistics[i].accuracy = validateResults.data[i].accuracy
            }
          })

      this.saveUserInput()
    },
    // Label may not be set for all variables, so use name as the label if needed
    getVarLabel(key) {
      let label = this.datasetInfo.depositorSetupInfo.variableInfo[key].label
      if (label === '') {
        label = this.datasetInfo.depositorSetupInfo.variableInfo[key].name
      }
      return label
    },
    save(editedItemFromDialog) {
      this.editedItem = Object.assign({}, editedItemFromDialog);
      if (this.isEditionMode) {
         Object.assign(this.statistics[this.editedIndex], this.editedItem);
      } else {
        for (let variable of this.editedItem.variable) {
          let ci = this.getDepositorSetupInfo.confidenceInterval
          if (!createStatsUtils.isDeltaStat(this.editedItem.statistic)) {
            this.editedItem.delta = ""
          }
          this.statistics.push(
              Object.assign({}, this.editedItem, {variable}, {ci})
          );
        }
      }
      createStatsUtils.redistributeValues(this.statistics, this.delta, this.epsilon, this.getDepositorSetupInfo.defaultDelta)
      // update stats with the accuracy values
      // (we don't have to check validation because that was done in the Dialog)
      console.log("SAVING INPUT: " + JSON.stringify(this.statistics))
      createStatsUtils.releaseValidation(this.analysisPlan.objectId, this.statistics)
          .then((validateResults) => {
            for (let i = 0; i < this.statistics.length; i++) {
              console.log('assigning accuracy: ' + JSON.stringify(validateResults.data[i].accuracy))
              const accuracy = validateResults.data[i].accuracy
              Object.assign(this.statistics[i], {accuracy})
            }
            this.saveUserInput()
            this.close()
          })


    },
    saveUserInput() {
      // convert statistics back from Decimal to Number
      // before saving
      this.statistics.forEach(function (item) {
        item.epsilon = +item.epsilon
        item.delta = +item.delta
      })
      let props = {
        epsilon: this.epsilon,
        delta: this.delta,
        confidenceInterval: this.confidenceInterval
      }
      const payload = {objectId: this.getDepositorSetupInfo.objectId, props: props}
      this.$store.dispatch('dataset/updateDepositorSetupInfo',
          payload)
      this.$store.dispatch('dataset/updateDPStatistics', this.statistics)

    },

    editEpsilon(item) {
      this.redistributeValue(this.epsilon, 'epsilon')
      this.saveUserInput()
    },
    editDelta(item) {
      this.redistributeValue(this.delta, 'delta')
      this.saveUserInput()
    },
    editItem(item) {

      this.editedIndex = this.statistics.indexOf(item);
      this.editedItem = Object.assign({}, item);
      this.dialogAddStatistic = true;
    },
    changeLockStatus(item) {
      item.locked = !item.locked;
    },
    deleteItem(item) {
      this.editedIndex = this.statistics.indexOf(item);
      this.editedItem = Object.assign({}, item);
      this.dialogDelete = true;
    },
    deleteItemConfirm() {
      this.statistics.splice(this.editedIndex, 1);
      createStatsUtils.redistributeValues()
      this.saveUserInput()
      this.closeDelete();
    },
    close() {
      this.dialogAddStatistic = false;
      this.resetEditedItem();
    },
    closeDelete() {
      this.dialogDelete = false;
      this.resetEditedItem();
    },
    resetEditedItem() {
      this.editedItem = Object.assign({}, this.defaultItem);
      this.editedIndex = -1;
    },

  }
};
</script>
