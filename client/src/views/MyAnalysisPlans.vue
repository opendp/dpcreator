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
                                    :disabled="!budgetAvailableForCreate()"
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
      <CreateAnalysisPlanDialog
          :dialog-visible.sync="createDialogVisible"
          :users="users"
          :dataset-list="datasetList"
          v-on:close="closeDialog">
      </CreateAnalysisPlanDialog>
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

</style>

<script>

import MyPlansTable from "../components/MyAnalysisPlans/MyPlansTable.vue";
import ColoredBorderAlert from "@/components/DynamicHelpResources/ColoredBorderAlert.vue";
import SupportBanner from "@/components/SupportBanner.vue";
import UploadFiles from "@/components/DesignSystem/UploadFiles.vue";
import {mapState} from "vuex";
import Button from "@/components/DesignSystem/Button.vue";
import UsersAPI from "@/api/users";
import CreateAnalysisPlanDialog from "@/components/MyAnalysisPlans/CreateAnalysisPlanDialog.vue";
import epsilonBudget from "@/shared/epsilonBudget";

export default {
    name: "MyAnalysisPlans",
    components: {CreateAnalysisPlanDialog, Button, MyPlansTable, ColoredBorderAlert, SupportBanner, UploadFiles},

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
        plans: [],
        maxBudget: 0,
        createDialogVisible: false,


    }),
    methods: {


        // Return true if there is available budget for the user to create an analysis plan
        // (ie the user owns at least one dataset that has > 0 unused epsilon. )
        budgetAvailableForCreate() {
          let availableBudget = false
          if (this.datasetList)
            this.datasetList.forEach(dataset => {
              const maxBudget = epsilonBudget.getDatasetMaxBudget(dataset)
              if (maxBudget > 0){
                availableBudget = true
              }
          })
          return availableBudget
        },

      openDialog() {

        this.createDialogVisible = true;
      },

      closeDialog() {
        this.createDialogVisible = false;


      },






    }
};
</script>
