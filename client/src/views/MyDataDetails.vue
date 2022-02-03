<template>
  <div class="my-data-details mt-10">
    <v-container>
      <v-sheet rounded="lg">
        <v-container>
          <h1 class="title-size-2">{{ datasetInfo.datasetSchemaInfo.name }}</h1>
          <StatusTag class="my-5" :status="status"/>

          <v-row>
            <v-col cols="6">
              Created: {{ analysisPlan.releaseInfo.dpRelease.created.humanReadable }}
            </v-col>

            <v-col cols="6">
              <a v-if="analysisPlan.releaseInfo.dataverseDepositInfo"
                 data-test="dataverseLink"
                 class="text-decoration-none" :href="fileUrl"
              >Check DP release in Dataverse
                <v-icon small color="primary">mdi-open-in-new</v-icon>
              </a>
            </v-col>
          </v-row>
          <p v-if="!analysisPlan.releaseInfo.dataverseDepositInfo.jsonDepositRecord.depositSuccess"
             style="padding-bottom:20px; padding-top: 10px;">
            <b>Dataverse Deposit Error : </b><span
              v-html="'JSON ' + analysisPlan.releaseInfo.dataverseDepositInfo.jsonDepositRecord.dvErrMsg"></span>
          </p>
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

            <p><b>Statistics</b></p>
            <p>Please see the table below for details on the
              <span v-if="analysisPlan.releaseInfo.dpRelease.statistics.length == 1">statistic</span><span
                  v-if="analysisPlan.releaseInfo.dpRelease.statistics.length> 1">statistics</span>, including the
              privacy parameters used to generate them.
              <template v-if="hasJSONandPDF">
                The following information can also be downloaded as a
                <a v-on:click="handleJSONDownload">JSON</a>
                or <a v-on:click="handlePDFDownload">PDF</a> file.

              </template>
              <template v-if="hasJSONOnly">
                The following information can also be downloaded as a
                <a data-test="jsonDownload" v-on:click="handleJSONDownload">JSON</a>
                file.
              </template>
            </p>

            <v-data-table
                :headers="statsHeaders"
                :items="statsItems"
                :single-expand="false"
                :expanded.sync="expanded"
                item-key="variable+statistic"
                show-expand
                class="elevation-1"
                sortable="false"
            >

              <template v-slot:[`item.description`]="{ item }">
                <div data-test="statistic description" v-html="getConfidenceLevel(item)"></div>

              </template>
              <template v-slot:[`item.result`]="{ item }">
                <div v-html="getResult(item)"></div>
                <a v-if="displayExpandLink(item)" v-on:click="() => toggleExpand(item)">Show more</a>

              </template>

              <template v-slot:expanded-item="{ headers, item }">

                <td :colspan="statsHeaders.length+1">
                  <v-container>
                    <v-row>
                      <v-col cols="2">Parameters:</v-col>
                      <v-col cols="10">
                        <div v-html="getParameters(item)"></div>

                      </v-col>
                    </v-row>
                    <v-row v-if="item.statistic === 'histogram'" cols="12">
                      <Chart
                          :axisData="getAxisData(item)"
                          :title="item.variable + ' Values'"
                          :index="item.index"
                          :variable="item.variable"

                      />
                    </v-row>
                  </v-container>
                </td>
              </template>
            </v-data-table>

            <div :v-if="analysisPlan.releaseInfo.dataverseDepositInfo">
              <p>&nbsp;</p>
              <p v-if="analysisPlan.releaseInfo.dataverseDepositInfo.jsonDepositRecord.depositSuccess"
                 style="padding-left:20px; padding-right:40px;">
                <span v-html="analysisPlan.releaseInfo.dataverseDepositInfo.jsonDepositRecord.userMsgHtml"></span>
              </p>

            </div>
            <div class="pt-5 pb-10">
              <p><b>Library Details</b></p>
              <div v-for="(detail, index) in libraryDetails" :key="index">
                <v-row v-if="status!==COMPLETED || detail.id!=='timeRemaining'" class="py-3">
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
              <p style="padding-top:20px;"><b>Dataset Details</b></p>
              <div v-for="(detail, index) in datasetDetails" :key="index">
                <v-row v-if="status!==COMPLETED || detail.id!=='timeRemaining'" class="py-3">
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
import Chart from "../components/MyData/Chart.vue";

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
    SupportBanner,
    Chart
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
        if (item.result.value.values.length > this.maxResults) {
          let arrayString = JSON.stringify(item.result.value.values.slice(0, this.maxResults))
          return arrayString.substr(0, arrayString.length - 1) + '...'
        } else {
          return JSON.stringify(item.result.value.values)
        }
      }
      return item.result.value
    },
    getParameters(item) {
      let params = 'Epsilon: ' + item.epsilon + ',&nbsp;&nbsp;&nbsp;'
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
          item.statistic + ' by at most ' + item.accuracy.value + ' units. '

    }
  },
  computed: {


    ...mapState('dataset', ['datasetInfo', 'analysisPlan']),
    ...mapGetters('dataset', ['userStep', "getTimeRemaining"]),
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
    libraryDetails: function () {
      let libraryDetails = [
        {
          id: "libraryName",
          label: "Name",
          tooltip: "Name of DP Library",
          value: this.analysisPlan.releaseInfo.dpRelease.differentiallyPrivateLibrary.name
        },
        {
          id: "libraryVersion",
          label: "Version",
          tooltip: "Version of DP Library",
          value: this.analysisPlan.releaseInfo.dpRelease.differentiallyPrivateLibrary.version
        }
      ]
      return libraryDetails
    },
    datasetDetails: function () {
      let datasetDetails = [

        {
          id: "installation",
          label: "Dataverse Installation",
          tooltip: "The Dataverse Installation where dataset originated",
          value: this.datasetInfo.installationName
        },

        {
          id: "timeRemaining",
          label: "Remaining time to complete release",
          tooltip: "3 Days from start of the process",
          value: this.getTimeRemaining
        },
        {
          id: "doi",
          label: "DV File ID / DOI",
          tooltip: "Persistent Identifier",
          value: this.datasetInfo.fileDoi
        },
        {
          id: "step",
          label: "Last state in Workflow",
          tooltip: "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
          value: stepInformation[this.userStep].label
        },
        {
          id: "citation",
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
    },

    getExpanded: function () {
      if (this.analysisPlan !== undefined) {
        return this.analysisPlan.releaseInfo.dpRelease.statistics
      } else {
        return []
      }
    },

  },
  created() {
    if (this.analysisPlan !== undefined) {
      let index = 0;
      this.analysisPlan.releaseInfo.dpRelease.statistics.forEach((stat) => {
        let statsItem = stat
        statsItem.id = index
        this.statsItems.push(statsItem)
        // Make only the first statistic expanded
        if (index === 0) {
          this.expanded.push(statsItem)
        }
        index++
      })
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
    expandedPanels: [],
    expanded: [],
    statsItems: [],
    maxResults: 10,
    generalErrorSummary: "Error summary: lorem ipsum dolor sit amet.",
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
