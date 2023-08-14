<template>
<v-dialog  v-model="dialogVisible" max-width="500px">
<v-card data-test="createPlanDialog" >
  <v-card-title>
    <span class="headline">Add Analysis Plan</span>
  </v-card-title>
  <v-card-text>
    <v-select
        v-if="selectedDataset ==null"
        data-test="selectPlanDataset"
        v-model="newPlan.datasetId"
        :items="availableDatasets()"
        label="Dataset Name"
        item-text="name"
        item-value="objectId"
        v-on:change="setMaxBudget()"
    ></v-select>
    <v-text-field data-test="inputPlanName" v-model="newPlan.planName" label="Plan Name"></v-text-field>
    <v-text-field data-test="inputPlanDescription" v-model="newPlan.description" label="Description"></v-text-field>
    <v-select
        data-test="selectPlanAnalyst"
        v-model="newPlan.analystId"
        :items="users"
        label="Analyst Name"
        item-text="username"
        item-value="objectId"
    ></v-select>
    <div class="budget-row">
      <v-text-field
          data-test="inputPlanBudget"
          :rules="[validateBudgetRule]"
          v-model="newPlan.budget"
          label="Budget"></v-text-field>
      <div class="max-budget" v-if="maxBudget > 0">
        <span class="help-text">(Max Budget: {{maxBudget}})</span>
      </div>
    </div>
    <v-text-field v-model="newPlan.expirationDate" label="ExpirationDate"></v-text-field>
    <v-date-picker v-model="newPlan.expirationDate" no-title></v-date-picker>

  </v-card-text>

  <v-card-actions>
    <v-btn :disabled="isSubmitDisabled" data-test="createPlanSubmitButton" color="primary" @click="createPlan">Create</v-btn>
    <v-btn color="secondary" @click="closeDialog">Cancel</v-btn>
  </v-card-actions>
</v-card>
</v-dialog>
</template>

<script>
const getDefaultExpirationDate =() => {
  const currentDate = new Date();
  const threeDaysAfter = new Date(currentDate.getTime() + (3 * 24 * 60 * 60 * 1000));
  return threeDaysAfter.toISOString().substr(0, 10);

}
import epsilonBudget from "@/shared/epsilonBudget";
export default {
  props: {
    dialogVisible: Boolean,
    users: Array,
    datasetList: Array,
    selectedDataset: Object
  },
  data() {
    return {
      newPlan: {
        datasetId: null,
        planName: null,
        description: null,
        analystId: null,
        expirationDate: getDefaultExpirationDate(),
        budget: null,
      },
    };
  },

  computed: {
    maxBudget( ) {
      let budget = 0;
      console.log('getting max budget')
      if (this.selectedDataset == null ) {
        if (this.datasetList == null) {
          budget = 0
        } else  {
          this.datasetList.forEach(dataset => {
            if (dataset.objectId === this.newPlan.datasetId) {
              budget = epsilonBudget.getDatasetMaxBudget(dataset)
            }
          })
        }
      } else {
        budget = epsilonBudget.getDatasetMaxBudget(this.selectedDataset)
      }
      return  budget
    },
    isSubmitDisabled() {
      return (
          !(this.getSelectedDatasetId()) ||
          !this.newPlan.planName ||
          !this.newPlan.analystId ||
          !this.newPlan.budget ||
          !this.newPlan.expirationDate
      );
    },
  },
  methods: {
    resetPlan() {
      this.newPlan.datasetId = null
      this.newPlan.planName = null
      this.newPlan.analystId = null
      this.newPlan.budget = null
      this.newPlan.description =null
      this.newPlan.expirationDate = getDefaultExpirationDate()

    },
    validateBudgetRule(value) {
      return (this.getSelectedDatasetId() == null  ||( value  && value <= this.maxBudget)) ||
          "Budget must be less than Max Budget." // Invalid budget input
    },
    setMaxBudget( ) {
      this.datasetList.forEach(dataset => {
        if (dataset.objectId === this.getSelectedDatasetId()) {
          this.maxBudget = epsilonBudget.getDatasetMaxBudget(dataset)
        }
      })
    },
    getSelectedDatasetId() {
         return this.selectedDataset == null  ? this.newPlan.datasetId : this.selectedDataset.objectId
    },
    createPlan() {
      this.newPlan.description = 'my description'
      this.newPlan.budget = Number(this.newPlan.budget)
      if (this.selectedDataset) {
        this.newPlan.datasetId = this.selectedDataset.objectId
      }
      this.$store.dispatch('dataset/createAnalysisPlan',
          this.newPlan)

      this.closeDialog();
    },

    availableDatasets() {
      let availableDatasets = []
      if (this.datasetList)
        this.datasetList.forEach(dataset => {
          const maxBudget = epsilonBudget.getDatasetMaxBudget(dataset)
          if (maxBudget > 0){
            availableDatasets.push(dataset)
          }
        })
      return availableDatasets
    },
    closeDialog() {
      this.resetPlan()
      this.$emit("close")

    },
  }
};
</script>

<style scoped>
.max-budget {
  margin-left: 16px;
}
</style>



