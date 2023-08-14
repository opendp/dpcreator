<template>
<v-dialog  v-model="dialogVisible" max-width="500px">
<v-card data-test="createPlanDialog" >
  <v-card-title>
    <span class="headline">Add Analysis Plan</span>
  </v-card-title>
  <v-card-text>
    <v-select
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
    datasetList: Array
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
      maxBudget: 0
    };
  },
  computed: {
    isSubmitDisabled() {
      return (
          !this.newPlan.datasetId ||
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
      this.maxBudget = 0
    },
    validateBudgetRule(value) {
      return (this.newPlan.datasetId == null  ||( value  && value <= this.maxBudget)) ||
          "Budget must be less than Max Budget." // Invalid budget input
    },
    setMaxBudget( ) {
      this.datasetList.forEach(dataset => {
        if (dataset.objectId === this.newPlan.datasetId) {
          this.maxBudget = epsilonBudget.getDatasetMaxBudget(dataset)
        }
      })
    },

    createPlan() {
      this.newPlan.description = 'my description'
      this.newPlan.budget = Number(this.newPlan.budget)

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



