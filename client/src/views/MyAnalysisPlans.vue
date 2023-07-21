<template>
    <div class="my-data">
        <v-container>
            <v-sheet rounded="lg">
                <v-container
                        :class="{
            'px-0': $vuetify.breakpoint.xsOnly
          }"
                >
                    <h1
                            class="title-size-1"
                            :class="{
              'px-5': $vuetify.breakpoint.xsOnly
            }"
                    >
                        My Analysis Plans
                    </h1>
                    <v-row
                            :class="{
              'px-5': $vuetify.breakpoint.xsOnly
            }"
                    >
                        <v-col cols="12" sm="7">
                            <p>
                                Check your differential privacy analysis plans and pending processes.
                                Click on View details to know more about them and their
                                statuses.
                            </p>
                        </v-col>
                        <v-col cols="12" v-if="$vuetify.breakpoint.xsOnly">
                            <ColoredBorderAlert type="warning">
                                <template v-slot:content>
                                    If you want to start or continue the process you have to
                                    <strong>use the desktop version of the app.</strong>
                                </template>
                            </ColoredBorderAlert>
                        </v-col>
                        <v-col offset-md="1">
                            <v-text-field
                                    v-model="search"
                                    label="Search Plans"
                                    outlined
                                    dense
                                    append-icon="mdi-magnify"
                            ></v-text-field>
                        </v-col>
                    </v-row>
                    <v-row justify="end">
                        <v-spacer/>
                        <v-col class="text-right">
                            <Button
                                    data-test="createPlanButton"
                                    color="Secondary"
                                    label="Create Analysis Plan"
                                    :class="{
                                    'width80 mx-auto d-block mb-2': $vuetify.breakpoint.xsOnly,
                                    'mr-2 mb-2': $vuetify.breakpoint.smAndUp
                                    }"
                                    :click="openDialog"
                            />
                        </v-col>
                    </v-row>
                    <MyPlansTable
                            v-if="!loading"
                            :class="{ 'my-5': $vuetify.breakpoint.smAndUp }"
                            :plans="analysisPlanList"
                            :searchTerm="search"
                            :itemsPerPage="5"
                    />
                </v-container>
            </v-sheet>
        </v-container>
        <!-- Add Analysis Plan Dialog -->
        <v-dialog  v-model="createDialogVisible" max-width="500px">
            <v-card data-test="createPlanDialog" >
                <v-card-title>
                    <span class="headline">Add Analysis Plan</span>
                </v-card-title>
                <v-card-text>
                    <v-select
                        data-test="selectPlanDataset"
                        v-model="newPlan.datasetId"
                        :items="datasetList"
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
    </div>
</template>
<style>
.budget-row {
    display: flex;
    align-items: center;
}
.help-text {
    font-size: 14px;
    color: #888;
    margin-top: 4px;
}
.max-budget {
    margin-left: 16px;
}
</style>

<script>

import MyPlansTable from "../components/MyAnalysisPlans/MyPlansTable.vue";
import ColoredBorderAlert from "@/components/DynamicHelpResources/ColoredBorderAlert.vue";
import SupportBanner from "@/components/SupportBanner.vue";
import UploadFiles from "@/components/DesignSystem/UploadFiles.vue";
import {mapState} from "vuex";
import Button from "@/components/DesignSystem/Button.vue";
import UsersAPI from "@/api/users";
const getDefaultExpirationDate =() => {
    const currentDate = new Date();
    const threeDaysAfter = new Date(currentDate.getTime() + (3 * 24 * 60 * 60 * 1000));
    return threeDaysAfter.toISOString().substr(0, 10);

}
export default {
    name: "MyAnalysisPlans",
    components: {Button, MyPlansTable, ColoredBorderAlert, SupportBanner, UploadFiles},

    created() {
        this.$store.dispatch('dataset/setAnalysisPlanList')
            .then(() => {
                this.loading = false
            })
        this.$store.dispatch('dataset/setDatasetList')
        UsersAPI.getUsers().then(resp => {
            this.users = resp.data.results
          } )
    },

    computed: {
        ...mapState('dataset', ['analysisPlanList',"datasetList"]),
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
    data: () => ({
        loading: true,
        search: "",
        users: null,
        plans: [],
        maxBudget: 0,
        createDialogVisible: false,
        newPlan: {
            datasetId: null,
            planName: null,
            description: null,
            analystId: null,
            expirationDate: getDefaultExpirationDate(),
            budget: null,
        }

    }),
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
            console.log('newPlan.datasetId: ' + this.newPlan.datasetId)
            console.log('value:' + value)
            console.log('this.maxBudget:'+ this.maxBudget)
            return (this.newPlan.datasetId == null  ||( value  && value <= this.maxBudget)) ||
             "Budget must be less than Max Budget." // Invalid budget input
        },
        openDialog() {
            console.log('openDialog')
            this.resetPlan()
            this.createDialogVisible = true;
        },

        closeDialog() {
            this.resetPlan()
            this.createDialogVisible = false;
            // Reset newPlan object

        },
        setMaxBudget( ) {
            let selectedDatasetBudget = 0;
            let spentBudget = 0
            this.datasetList.forEach(dataset => {
                if (dataset.objectId === this.newPlan.datasetId){
                    selectedDatasetBudget = dataset.depositorSetupInfo.epsilon
                    console.log('analysisPlans length: ' + dataset.analysisPlans.length)
                    dataset.analysisPlans.forEach(plan =>{
                        console.log('plan.epsilon: ' + plan.epsilon)
                        spentBudget += plan.epsilon
                        console.log('spentBudget: ' + spentBudget)
                    })
                }
            })
            console.log('spentBudget: ' + spentBudget+", selectedDatasetBudget: "+selectedDatasetBudget)
            this.maxBudget = Number((selectedDatasetBudget - spentBudget).toFixed(3))
        },
        createPlan() {
            console.log("calling create plan  with newPlan = " + JSON.stringify(this.newPlan))
            console.log('this.newPlan.budget: ' + this.newPlan.budget)
            this.newPlan.description = 'my description'
            this.newPlan.budget = Number(this.newPlan.budget)

            this.$store.dispatch('dataset/createAnalysisPlan',
               this.newPlan)

            this.closeDialog();
        },

    }
};
</script>
