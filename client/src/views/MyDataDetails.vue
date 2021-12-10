<template>
  <div class="my-data-details mt-10">
    <v-container>
      <v-sheet rounded="lg">
        <v-container>
          <h1 class="title-size-2">{{ datasetInfo.datasetSchemaInfo.name }}</h1>
          <StatusTag class="my-5" :status="status"/>
          <ColoredBorderAlert type="warning" v-if="$vuetify.breakpoint.xsOnly">
            <template v-slot:content>
              If you want to start or continue the process you have to
              <strong>use the desktop version of the app.</strong>
            </template>
          </ColoredBorderAlert>
          <ColoredBorderAlert type="error" v-if="permissionsError">
            <template v-slot:content>
              Check the file permissions in
              <a href="" class="black--text">Dataverse</a> to continue with the
              process.
            </template>
          </ColoredBorderAlert>
          <ColoredBorderAlert type="error" v-if="generalError">
            <template v-slot:content>
              {{ generalErrorSummary }}
            </template>
          </ColoredBorderAlert>

          <div class="mb-5" v-if="status === COMPLETED">
            <p class="primary--text">DP Release Information:</p>

            <p>This release contains {{ analysisPlan.releaseInfo.dpRelease.statistics.length }} statistic<span
                v-if="analysisPlan.releaseInfo.dpRelease.statistics.length > 1">s</span>:</p>
            <p>&nbsp;</p>
            <div v-for="(statistic, index) in analysisPlan.releaseInfo.dpRelease.statistics"
                 style="padding-left:20px; padding-right:40px;">
              <p data-test="statistic description" style="">
                ({{ index + 1 }}) <span v-html="statistic.description.html"></span></p>

            </div>
            <p style="padding-left:20px; padding-right:40px;">Created:
              {{ analysisPlan.releaseInfo.dpRelease.created.humanReadable }}</p>
            <div :v-if="analysisPlan.releaseInfo.dataverseDepositInfo">
              <p>&nbsp;</p>
              <p v-if="analysisPlan.releaseInfo.dataverseDepositInfo.jsonDepositRecord.depositSuccess"
                 style="padding-left:20px; padding-right:40px;">
                <span v-html="analysisPlan.releaseInfo.dataverseDepositInfo.jsonDepositRecord.userMsgHtml"></span>
              </p>
              <p v-if="!analysisPlan.releaseInfo.dataverseDepositInfo.jsonDepositRecord.depositSuccess"
                 style="padding-left:20px; padding-right:40px;">
                <b>Dataverse Deposit Error : </b><span
                  v-html="'JSON ' + analysisPlan.releaseInfo.dataverseDepositInfo.jsonDepositRecord.dvErrMsg"></span>
              </p>
            </div>

            <p>Please see the panels below for details on the
              <span v-if="analysisPlan.releaseInfo.dpRelease.statistics.length == 1">statistic</span><span
                  v-if="analysisPlan.releaseInfo.dpRelease.statistics.length> 1">statistics</span>, including the
              privacy parameters used to generate them.
            </p>
          </div>
          <div class="mb-5" v-if="status === COMPLETED">
            <v-expansion-panels multiple v-model="expandedPanels">
              <v-expansion-panel data-test="DP Statistics Panel">
                <v-expansion-panel-header>DP Statistics</v-expansion-panel-header>
                <v-expansion-panel-content>
                  <json-viewer :expand-depth="5" :expanded=true :value="analysisPlan.releaseInfo.dpRelease.statistics">
                  </json-viewer>
                </v-expansion-panel-content>
              </v-expansion-panel>
              <v-expansion-panel>
                <v-expansion-panel-header>Dataset</v-expansion-panel-header>
                <v-expansion-panel-content>
                  <json-viewer :expand-depth="5" :expanded=true
                               :value="analysisPlan.releaseInfo.dpRelease.dataset">
                  </json-viewer>
                </v-expansion-panel-content>
              </v-expansion-panel>
              <v-expansion-panel>
                <v-expansion-panel-header>DP Library</v-expansion-panel-header>
                <v-expansion-panel-content>
                  <json-viewer :expand-depth="5" :expanded=true
                               :value="analysisPlan.releaseInfo.dpRelease.differentiallyPrivateLibrary">
                  </json-viewer>
                </v-expansion-panel-content>
              </v-expansion-panel>
            </v-expansion-panels>
          </div>
          <div class="mb-5" v-if="status === COMPLETED">
            <p class="primary--text">Download DP Release:</p>
            <Button v-if="analysisPlan.releaseInfo.downloadPdfUrl"
                    data-test="pdfDownload"
                    :click="handlePDFDownload"
                    color="primary"
                    classes="d-block mb-2"
            >
              <v-icon left>mdi-download</v-icon>
              <span>PDF file</span>
            </Button>
            <Button v-if="analysisPlan.releaseInfo.downloadJsonUrl"
                    data-test="jsonDownload"
                    :click="handleJSONDownload"
                    color="primary"
                    classes="d-block mb-2"
            >
              <v-icon left>mdi-download</v-icon>
              <span>JSON file</span>
            </Button>

            <div v-if="analysisPlan.releaseInfo.dataverseDepositInfo" data-test="dataverseLink">
              <a class="text-decoration-none d-block mt-10" :href="fileUrl"
              >Check DP release in Dataverse
                <v-icon small color="primary">mdi-open-in-new</v-icon>
              </a
              >
            </div>
          </div>
           <div class="pt-5 pb-10">
             <div v-for="(detail, index) in datasetDetails" :key="index">
               <v-row class="py-3">
                 <v-col
                     cols="12"
                     sm="4"
                     class="grey--text text--darken-2 d-flex"
                     :class="{
                    'py-0': $vuetify.breakpoint.xsOnly
                  }"
                 >
                  <span>
                    {{ detail.label }}
                  </span>
                  <QuestionIconTooltip :text="detail.tooltip"/>
                </v-col>
                <v-col
                    cols="12"
                    sm="8"
                    :class="{
                    'pt-0 pb-5': $vuetify.breakpoint.xsOnly
                  }"
                >{{ detail.value }}
                </v-col
                >
              </v-row>
              <v-divider class="hidden-xs-only"/>
            </div>
          </div>

          <Button
              v-for="(action, index) in statusInformation[
              status
            ].availableActions.filter(action => action !== VIEW_DETAILS)"
              :key="action + '-' + index"
              color="primary"
              :click="() => handleButtonClick(action, datasetTitle)"
              :label="actionsInformation[action]"
              :class="{
              'width80 mx-auto d-block mb-2': $vuetify.breakpoint.xsOnly,
              'mr-2': $vuetify.breakpoint.smAndUp
            }"
              :disabled="
              action === CONTINUE_WORKFLOW && $vuetify.breakpoint.xsOnly
            "
          />
          <Button
              color="primary"
              outlined
              :click="() => $router.push(NETWORK_CONSTANTS.MY_DATA.PATH)"
              label="Back to My Data"
              :class="{
              'width80 mx-auto d-block': $vuetify.breakpoint.xsOnly
            }"
          />
        </v-container>
      </v-sheet>
    </v-container>
    <SupportBanner/>
  </div>
</template>

<script>
import statusInformation from "../data/statusInformation";
import actionsInformation from "../data/actionsInformation";
import QuestionIconTooltip from "../components/DynamicHelpResources/QuestionIconTooltip.vue";
import ColoredBorderAlert from "../components/DynamicHelpResources/ColoredBorderAlert.vue";
import StatusTag from "../components/DesignSystem/StatusTag.vue";
import Button from "../components/DesignSystem/Button.vue";
import SupportBanner from "../components/SupportBanner.vue";
import NETWORK_CONSTANTS from "../router/NETWORK_CONSTANTS";
import {mapGetters, mapState} from "vuex";
import stepInformation from "@/data/stepInformation";

const {
  IN_PROGRESS,
  IN_EXECUTION,
  ERROR,
  COMPLETED
} = statusInformation.statuses;

const {
  VIEW_DETAILS,
  CONTINUE_WORKFLOW,
  CANCEL_EXECUTION
} = actionsInformation.actions;

export default {
  name: "MyDataDetails",
  components: {
    QuestionIconTooltip,
    ColoredBorderAlert,
    StatusTag,
    Button,
    SupportBanner
  },

  methods: {
    handleButtonClick(action, item) {
      this[action](item);
    },
    continueWorkflow(item) {
      this.$router.push(`${NETWORK_CONSTANTS.WIZARD.PATH}`)
    },
    cancelExecution(item) {
      //TODO: Implement Handler
      alert("cancel execution " + item);
    },
    handlePDFDownload() {
      //TODO: Implement Handler
      alert("PDF download!");
    },
    handleJSONDownload() {
      //TODO: Implement Handler
      alert("JSON download!");
    },
    handleHTMLDownload() {
      //TODO: Implement Handler
      alert("HTML download!");
    },
    handleXMLDownload() {
      //TODO: Implement Handler
      alert("XML download!");
    }
  },
  computed: {


    ...mapState('dataset', ['datasetInfo', 'analysisPlan']),
    ...mapGetters('dataset', ['userStep', "getTimeRemaining"]),
    fileUrl: function () {
      const host = this.datasetInfo.datasetSchemaInfo.includedInDataCatalog.url
      return host + '/file.xhtml?fileId=' + this.datasetInfo.dataverseFileId

    },
    datasetDetails: function () {

      let datasetDetails = [
        {
          label: "DV Installation",
          tooltip: "The Dataverse Installation where dataset originated",
          value: this.datasetInfo.installationName
        },

        {
          label: "Remaining time to complete release",
          tooltip: "3 Days from start of the process",
          value: this.getTimeRemaining
        },
        {
          label: "DV File ID / DOI",
          tooltip: "Persistent Identifier",
          value: this.datasetInfo.fileDoi
        },
        {
          label: "Last state in Workflow",
          tooltip: "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
          value: stepInformation[this.userStep].label
        },
        {
          label: "Citation",
          tooltip: "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
          value: this.datasetInfo.datasetDoi + ' | ' + this.datasetInfo.datasetSchemaInfo.name + ' | ' + this.datasetInfo.fileSchemaInfo.name
        },
      ]
      return datasetDetails;
    },
    status: function () {
      return stepInformation[this.userStep].workflowStatus
    },
    generalError: function () {
      return this.status === ERROR;
    },
    permissionsError: function () {
      return false;
    }
  },
  data: () => ({
    IN_PROGRESS,
    IN_EXECUTION,
    ERROR,
    COMPLETED,
    VIEW_DETAILS,
    CONTINUE_WORKFLOW,
    CANCEL_EXECUTION,
    statusInformation,
    actionsInformation,
    datasetTitle: "",
    expandedPanels: [0, 1],
    generalErrorSummary: "Error summary: lorem ipsum dolor sit amet.",

    NETWORK_CONSTANTS
  })
};
</script>
