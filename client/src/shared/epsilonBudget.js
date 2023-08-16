export default {
    getDatasetMaxBudget(dataset) {
        let selectedDatasetBudget = dataset.depositorSetupInfo.epsilon
        let spentBudget = 0
        dataset.analysisPlans.forEach(plan =>{
            spentBudget += plan.epsilon
        })
        let maxBudget = Number((selectedDatasetBudget - spentBudget).toFixed(3))
        return maxBudget
    },
}