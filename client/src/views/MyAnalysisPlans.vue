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
        <v-dialog v-model="createDialogVisible" max-width="500px">
            <v-card>
                <v-card-title>
                    <span class="headline">Add Analysis Plan</span>
                </v-card-title>
                <v-card-text>
                    <v-select
                        v-model="newPlan.datasetId"
                        :items="datasetList"
                        label="Dataset Name"
                        item-text="name"
                        item-value="objectId"
                    ></v-select>
                    <v-text-field v-model="newPlan.planName" label="Plan Name"></v-text-field>
                    <v-select
                        v-model="newPlan.analystId"
                        :items="users"
                        label="Analyst Name"
                        item-text="username"
                        item-value="objectId"
                    ></v-select>
                    <v-text-field v-model="newPlan.budget" label="Budget"></v-text-field>
                    <v-text-field v-model="newPlan.expirationDate" label="ExpirationDate"></v-text-field>
                    <v-date-picker v-model="newPlan.expirationDate" no-title></v-date-picker>

                </v-card-text>

                <v-card-actions>
                    <v-btn color="primary" @click="createPlan">Create</v-btn>
                    <v-btn color="secondary" @click="closeDialog">Cancel</v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
    </div>
</template>

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

    },
    data: () => ({
        loading: true,
        search: "",
        users: null,
        plans: [{
            analysisPlanId: "1",
            datasetName: "dataset name 1",
            planName: "plan name 1",
            analyst: "Ellen K",
            budget: ".5",
        },
            {
                analysisPlanId: "2",
                datasetName: "dataset name 2",
                planName: "plan name 2",
                analyst: "Raman P",
                budget: ".25",
            },
        ],
        createDialogVisible: false,

        newPlan: {
            datasetId: null, // Store the selected dataset ID
            planName: "",
            analyst: "",
            budget: "",
            expirationDate: getDefaultExpirationDate()
        }

    }),
    methods: {
        openDialog() {
            console.log('openDialog')
            this.createDialogVisible = true;
        },

        closeDialog() {
            this.createDialogVisible = false;
            // Reset newPlan object
            this.newPlan = {
                datasetId: "",
                datasetName: "",
                planName: "",
                analyst: "",
                expirationDate: getDefaultExpirationDate(),
                budget: "",
            };
        },

        createPlan() {
            // Perform your create action here with the newPlan data
            // You can access the new plan details from `this.newPlan`

            // After successful creation, close the dialog
            // Retrieve the selected dataset name
            const selectedDataset = this.datasetList.find(
                (dataset) => dataset.objectId === this.newPlan.datasetId
            );
            const datasetName = selectedDataset ? selectedDataset.name : "";

            // Perform your create action here with the newPlan data
            // You can access the new plan details from `this.newPlan`
            // and use `datasetName` for the dataset name
            console.log("create plan called with newPlan = " + JSON.stringify(this.newPlan))
            // After successful creation, close the dialog
            this.closeDialog();
        },

    }
};
</script>
