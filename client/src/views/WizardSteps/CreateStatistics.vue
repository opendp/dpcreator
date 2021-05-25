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
        v-on:newStatisticButtonPressed="dialogAddStatistic = true"
        v-on:editStatistic="editItem"
        v-on:changeLockStatus="changeLockStatus"
        v-on:deleteStatistic="deleteItem"
        class="mb-10"
    />

    <AddStatisticDialog
        :formTitle="formTitle"
        :dialog="dialogAddStatistic"
        :editedIndex="editedIndex"
        :editedItem="editedItem"
        v-on:saveConfirmed="save"
        v-on:close="close"
    />
    <DeleteStatisticDialog
        :dialogDelete="dialogDelete"
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
import ColoredBorderAlert from "../../components/DynamicHelpResources/ColoredBorderAlert.vue";
import AddStatisticDialog from "../../components/Wizard/Steps/CreateStatistics/AddStatisticDialog.vue";
import DeleteStatisticDialog from "../../components/Wizard/Steps/CreateStatistics/DeleteStatisticDialog.vue";
import EditNoiseParamsDialog from "../../components/Wizard/Steps/CreateStatistics/EditNoiseParamsDialog.vue";
import EditNoiseParamsConfirmationDialog
  from "../../components/Wizard/Steps/CreateStatistics/EditNoiseParamsConfirmation.vue";
import NoiseParams from "../../components/Wizard/Steps/CreateStatistics/NoiseParams.vue";
import StatisticsTable from "../../components/Wizard/Steps/CreateStatistics/StatisticsTable.vue";
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
      locked: "false"
    },
    defaultItem: {
      statistic: "",
      variable: [],
      epsilon: "",
      error: "",
      missingValuesHandling: "",
      handleAsFixed: false,
      fixedValue: "0",
      locked: "false"
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
    save(editedItemFromDialog) {
      this.editedItem = Object.assign({}, editedItemFromDialog);
      if (this.isEditionMode) {
        Object.assign(this.statistics[this.editedIndex], this.editedItem);
      } else {
        for (let variable of this.editedItem.variable) {
          this.statistics.push(
              Object.assign({}, this.editedItem, {variable})
          );
        }
      }
      this.close();
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
