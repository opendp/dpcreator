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
        :confidenceLevel="confidenceLevel"
        v-on:editNoiseParams="dialogEditNoiseParamsConfirmation = true"
    />

    <ColoredBorderAlert type="warning" locale-tag="create statistics.epsilon warning">
    </ColoredBorderAlert>
    <ColoredBorderAlert type="info" locale-tag="create statistics.statistics help">
    </ColoredBorderAlert>

    <StatisticsTable
        :statistics="statistics"
        :total-epsilon="epsilon"
        v-on:newStatisticButtonPressed="dialogAddStatistic = true"
        v-on:editStatistic="editItem"
        v-on:editEpsilon="editEpsilon"
        v-on:changeLockStatus="changeLockStatus"
        v-on:deleteStatistic="deleteItem"
        class="mb-10"
    />

    <AddStatisticDialog
        :variable-info="datasetInfo.depositorSetupInfo.variableInfo"
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
        :confidenceLevel="confidenceLevel"
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
  computed: {
    ...mapState('auth', ['error', 'user']),
    ...mapState('dataset', ['datasetInfo']),
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
  watch: {
    statistics: function (newStatisticsArray) {
      this.$emit("stepCompleted", 3, newStatisticsArray.length !== 0);
    }
  },
  data: () => ({
    epsilon: 0.25,
    delta: 0.000001,
    confidenceLevel: "99%",
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
    handleOpenEditNoiseParamsDialog() {
      this.dialogEditNoiseParamsConfirmation = false;
      this.dialogEditNoiseParams = true;
    },
    handleSaveEditNoiseParamsDialog(epsilon, delta, confidenceLevel) {
      this.epsilon = epsilon;
      this.delta = delta;
      this.confidenceLevel = confidenceLevel;
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
        const label = this.getVarLabel(this.editedItem.variable)
        Object.assign(this.statistics[this.editedIndex], this.editedItem, {label});
      } else {
        for (let variable of this.editedItem.variable) {
          let label = this.getVarLabel(variable)
          this.statistics.push(
              Object.assign({}, this.editedItem, {variable}, {label})
          );
        }
        this.redistributeEpsilon()
      }
      console.log('saved: ' + JSON.stringify(this.statistics))
      this.close();
    },
    redistributeEpsilon() {
      // for all statistics with locked == false, update so that the unlocked epsilon
      // is shared equally among them.
      let lockedEpsilon = new Decimal('0.0');
      let lockedCount = new Decimal('0');
      this.statistics.forEach(function (item) {
        if (item.locked) {
          lockedEpsilon = lockedEpsilon.plus(item.epsilon)
          lockedCount = lockedCount.plus(1);
        }
      });
      const remaining = new Decimal(this.epsilon).minus(lockedEpsilon)
      const unlockedCount = this.statistics.length - lockedCount
      if (unlockedCount > 0) {
        const epsilonShare = remaining.div(unlockedCount)
        this.statistics.forEach(function (item) {
          if (!item.locked) {
            item.epsilon = epsilonShare
          }
        })

      }


    },
    editEpsilon(item) {
      this.redistributeEpsilon()

    },
    editItem(item) {

      this.editedIndex = this.statistics.indexOf(item);
      this.editedItem = Object.assign({}, item);
      this.dialogAddStatistic = true;
    },
    changeLockStatus(item) {
      item.locked = !item.locked;
      console.log('changing locked status: ' + item.locked)
    },
    deleteItem(item) {
      this.editedIndex = this.statistics.indexOf(item);
      this.editedItem = Object.assign({}, item);
      this.dialogDelete = true;
    },
    deleteItemConfirm() {
      this.statistics.splice(this.editedIndex, 1);
      this.redistributeEpsilon()
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
    }
  }
};
</script>
