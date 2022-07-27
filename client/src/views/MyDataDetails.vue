<template>
  <div class="my-data-details mt-10">
    <v-container>
      <v-sheet rounded="lg">
        <v-container>
          <h1 class="title-size-2" style="line-height:150%">
            <b v-if="status === COMPLETED">DP Release</b>
            <b v-if="status !== COMPLETED">Data File</b>
            <br/>{{ datasetInfo.name }}</h1>
          Current Status:
          <StatusTag class="my-5" :status="status"/>
          <p></p>
          <v-row>
            <template v-if="status === COMPLETED">
              <v-col cols="6">
                <p>
                  Created: {{ analysisPlan.releaseInfo.dpRelease.created.humanReadable }}
                </p>
              </v-col>
              <v-col cols="6">
                <a v-if="analysisPlan.releaseInfo.dataverseDepositInfo && analysisPlan.releaseInfo.dataverseDepositInfo.jsonDepositRecord.depositSuccess"
                   data-test="dataverseLink"
                   class="text-decoration-none" :href="fileUrl"
                >Check DP release in Dataverse
                  <v-icon small color="primary">mdi-open-in-new</v-icon>
                </a>
              </v-col>
            </template>
          </v-row>

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
            <ReleasePDF></ReleasePDF>
            <p></p>
            <p> This information can also be downloaded in other formats:</p>
            <Button v-if="hasPDF"
                    data-test="pdfDownload"
                    :click="handlePDFDownload"
                    color="primary"
                    classes="d-block mb-2"
            >
              <v-icon left>mdi-download</v-icon>
              <span>DP Release PDF File</span>
            </Button>
            <Button v-if="hasJSON"
                    data-test="jsonDownload"
                    :click="handleJSONDownload"
                    color="primary"
                    classes="d-block mb-2"
            >
              <v-icon left>mdi-download</v-icon>
              <span>DP Release JSON File</span>
            </Button>
            <div style="padding-top:20px;">
              <hr/>
              <br/>
              <div v-if="analysisPlan.releaseInfo.dataverseDepositInfo">
                <h3 class="title-size-3">Dataverse deposits</h3>
                <p v-if="!analysisPlan.releaseInfo.dataverseDepositInfo.jsonDepositRecord.depositSuccess"
                   style="padding-bottom:20px; padding-top: 10px;">
                  <b>JSON file: </b><span
                    v-html="'' + analysisPlan.releaseInfo.dataverseDepositInfo.jsonDepositRecord.dvErrMsg"></span>
                </p>
                <p v-if="analysisPlan.releaseInfo.dataverseDepositInfo.jsonDepositRecord.depositSuccess"
                   style="padding-bottom:20px; padding-top: 10px;">
                  <a
                      data-test="dataverseLink"
                      class="text-decoration-none" :href="fileUrl"
                  >Check DP release in Dataverse
                    <v-icon small color="primary">mdi-open-in-new</v-icon>
                  </a>
                </p>
              </div>
            </div>

          </div>


          <Button
              v-for="(action, index) in statusInformation[
              status
            ].availableActions.filter(action => action !== VIEW_DETAILS)"
              :key="action + '-' + index"
              color="primary"
              :data-test="action"
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
          <DeleteDatasetDialog
              :dialogDelete="dialogDelete"
              :datasetInfo="datasetInfo"
              :analysisPlan="analysisPlan"
              v-on:cancel="closeDelete"
              v-on:close="datasetDeleted"
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
import Chart from "../components/MyData/Chart.vue";
import ReleasePDF from "@/components/MyData/ReleasePDF";
import DeleteDatasetDialog from "@/components/MyData/DeleteDatasetDialog";

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
    ReleasePDF,
    QuestionIconTooltip,
    ColoredBorderAlert,
    StatusTag,
    Button,
    SupportBanner,
    Chart,
    DeleteDatasetDialog
  },

  methods: {
    delete(item) {
      this.dialogDelete = true
    },
    closeDelete() {
      this.dialogDelete = false
    },
    datasetDeleted() {
      this.dialogDelete = false
      this.$router.push(NETWORK_CONSTANTS.MY_DATA.PATH)
    },
    handleButtonClick(action, item) {
      console.log('handling action: ' + action)
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
      window.location.href = this.analysisPlan.releaseInfo.downloadPdfUrl;
    },
    handleJSONDownload() {
      window.location.href = this.analysisPlan.releaseInfo.downloadJsonUrl;
    },
    toggleExpand(item) {
      const indexRow = item.index;
      const indexExpanded = this.expanded.findIndex(i => i === item);
      if (indexExpanded > -1) {
        this.expanded.splice(indexExpanded, 1)
      } else {
        this.expanded.push(item);
      }
    },
    expandedText: function (item) {
      return item.epsilon
    },
    displayExpandLink(item) {
      return (typeof (item.result.value) === 'object' &&
          item.result.value.values.length > this.maxResults)
    },
    getResult: function (item) {

      if (typeof (item.result.value) === 'object') {
        if (false) {
          let arrayString = JSON.stringify(item.result.value.values.slice(0, this.maxResults))
          return arrayString.substr(0, arrayString.length - 1) + '...'
        } else {
          return JSON.stringify(item.result.value.values)
        }
      }
      return item.result.value
    },
    getParameters(item) {
      let params = 'Epsilon: ' + (Number(item.epsilon)).toFixed(3) + ',&nbsp;&nbsp;&nbsp;'
      if (item.delta) {
        params += 'Delta: ' + item.delta + ',&nbsp;&nbsp;&nbsp;'
      } else {
        params += 'Delta: n/a,&nbsp;&nbsp;&nbsp;'
      }
      if (item.bounds) {
        params += 'Bounds: [' + item.bounds.min + ',' + item.bounds.max + '],&nbsp;&nbsp;&nbsp;'
      }
      if (item.result.value.categories) {
        params += 'Categories: ' + JSON.stringify(item.result.value.categories)
        params += ',&nbsp;&nbsp;&nbsp;'
        params += 'Category value pairs: ' + JSON.stringify(item.result.value.categoryValuePairs)
        params += ',&nbsp;&nbsp;&nbsp;'
      }
      params += 'Missing value type: ' + item.missingValueHandling.type + ',&nbsp;&nbsp;&nbsp;'
      params += 'Missing value: ' + item.missingValueHandling.fixedValue + ',&nbsp;&nbsp;&nbsp;'
      return params
    },
    getConfidenceLevel(item) {
      return 'There is a probability of ' + (Number(item.confidenceLevel) * 100) +
          '% that the DP ' + item.statistic + ' will differ from the true ' +
          item.statistic + ' by at most ' + (Number(item.accuracy.value)).toPrecision(2) + ' units. '

    },
    getDetailText(label, value) {
      return label + ': ' + value
    },
    getStatsDetails(statsItem) {
      let statsDetails = [
        {
          id: "result",
          label: "Result",
          value: this.getResult(statsItem)
        },
        {
          id: "params",
          label: "Parameters",
          value: this.getParameters(statsItem)
        },
        {
          id: "description",
          label: "Description",
          value: statsItem.description.html
        }
      ]
      return statsDetails
    },
    getAnchor(item) {
      return item.statistic + item.variable
    }
  },
  computed: {


    ...mapState('dataset', ['datasetInfo', 'analysisPlan']),
    ...mapGetters('dataset', ['userStep', "getTimeRemaining"]),
    hasJSON() {
      return !!this.analysisPlan.releaseInfo.downloadJsonUrl
    },
    hasPDF() {
      return !!this.analysisPlan.releaseInfo.downloadPdfUrl
    },
    hasJSONOnly() {
      return (this.analysisPlan.releaseInfo.downloadJsonUrl && !this.analysisPlan.releaseInfo.downloadPdfUrl) ? true : false
    },
    hasPDFOnly() {
      return (this.analysisPlan.releaseInfo.downloadPdfUrl && !this.analysisPlan.releaseInfo.downloadJsonUrl) ? true : false
    },
    hasJSONandPDF() {
      return (this.analysisPlan.releaseInfo.downloadPdfUrl && this.analysisPlan.releaseInfo.downloadJsonUrl) ? true : false
    },
    fileUrl: function () {
      const host = this.datasetInfo.datasetSchemaInfo.includedInDataCatalog.url
      return host + '/file.xhtml?fileId=' + this.datasetInfo.dataverseFileId

    },

    status: function () {
      return stepInformation[this.userStep].workflowStatus
    },
    generalError: function () {
      return this.status === ERROR;
    },
    permissionsError: function () {
      return false;
    },


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
    expandedPanels: [],
    expanded: [],
    maxResults: 10,
    generalErrorSummary: "Error summary: lorem ipsum dolor sit amet.",
    dialogDelete: false,
    statsHeaders: [
      {text: 'Variable', value: 'variable', sortable: false},
      {text: 'Statistic', value: 'statistic', sortable: false},
      {text: 'Result', value: 'result', sortable: false},
      {text: 'Confidence Level', value: 'description', sortable: false}
    ],
    NETWORK_CONSTANTS,

    getAxisData(item) {

      return item.result.value.categoryValuePairs.map(el => ({x: el[0], y: el[1]}))
    }


  })
};
</script>
