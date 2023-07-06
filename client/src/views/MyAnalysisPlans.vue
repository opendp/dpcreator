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
                         <!--   <upload-files></upload-files>  -->
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

    </div>
</template>

<script>

import MyPlansTable from "../components/MyAnalysisPlans/MyPlansTable.vue";
import ColoredBorderAlert from "@/components/DynamicHelpResources/ColoredBorderAlert.vue";
import SupportBanner from "@/components/SupportBanner.vue";
import UploadFiles from "@/components/DesignSystem/UploadFiles.vue";
import {mapState} from "vuex";

export default {
    name: "MyAnalysisPlans",
    components: {MyPlansTable , ColoredBorderAlert, SupportBanner, UploadFiles},

    created() {
        this.$store.dispatch('dataset/setAnalysisPlanList')
            .then(() => {
                this.loading = false
            })

    },

    computed: {
       ...mapState('dataset', ['analysisPlanList']),
    },
    data: () => ({
        loading: true,
        search: "",
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
        ]

    })
};
</script>
