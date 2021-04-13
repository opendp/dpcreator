<template>
  <div class="my-data-details mt-16">
    <v-container>
      <v-sheet rounded="lg">
        <v-container>
          <h1 class="title-size-2">{{ datasetTitle }}</h1>
          <v-chip :color="statusInformation[status].color" label class="my-5">
            <v-icon left small>
              {{ statusInformation[status].icon }}
            </v-icon>
            {{ statusInformation[status].label }}
          </v-chip>
          <div class="mb-5" v-if="status === 'completed'">
            <p class="primary--text font-weight-bold">Download DP Release:</p>
            <v-btn
                @click="handlePDFDownload"
                color="primary"
                class="d-block mb-3"
                outlined
            >
              <v-icon left>mdi-download</v-icon>
              <span>PDF file</span>
            </v-btn>
            <v-btn
                @click="handleJSONDownload"
                color="primary"
                class="d-block mb-3"
                outlined
            >
              <v-icon left>mdi-download</v-icon>
              <span>JSON file</span>
            </v-btn>
            <v-btn
                @click="handleHTMLDownload"
                color="primary"
                class="d-block mb-3"
                outlined
            >
              <v-icon left>mdi-download</v-icon>
              <span>HTML file</span>
            </v-btn>
            <v-btn
                @click="handleXMLDownload"
                color="primary"
                class="d-block mb-3"
                outlined
            >
              <v-icon left>mdi-download</v-icon>
              <span>XML file</span>
            </v-btn>
            <a
                class="font-weight-bold text-decoration-none d-block mt-10"
                href=""
            >Check DP release in Dataverse
              <v-icon small color="primary">mdi-open-in-new</v-icon>
            </a
            >
          </div>
          <div class="pt-5 pb-10">
            <div v-for="(detail, index) in datasetDetails" :key="index">
              <v-row class="py-3">
                <v-col cols="4" class="grey--text text--darken-2 d-flex">
                  <span>
                    {{ detail.label }}
                  </span>
                  <QuestionIconTooltip :text="detail.tooltip"/>
                </v-col>
                <v-col cols="8">{{ detail.value }}</v-col>
              </v-row>
              <v-divider/>
            </div>
          </div>
          <v-alert
              v-if="permissionsError"
              class="mb-10"
              border="right"
              colored-border
              type="error"
              elevation="2"
              icon="mdi-cancel"
          >
            Check the file permissions in
            <a href="" class="black--text">Dataverse</a> to continue with the
            process.
          </v-alert>
          <v-alert
              v-if="generalError"
              class="mb-10"
              border="right"
              colored-border
              type="error"
              elevation="2"
              icon="mdi-cancel"
          >
            {{ generalErrorSummary }}
          </v-alert>
          <ColoredBorderAlert type="warning" v-if="status === IN_EXECUTION">
            <template v-slot:content>
              If canceling, this action cannot be undone.
            </template>
          </ColoredBorderAlert>

          <v-btn
              v-for="action in statusInformation[status].availableActions.filter(
              action => action !== 'viewDetails'
            )"
              :key="action"
              color="primary"
              class="mr-3"
              @click="handleButtonClick(action, datasetTitle)"
          >
            {{ actionsInformation[action] }}
          </v-btn>
          <v-btn color="primary" outlined @click="$router.push('/my-data')"
          >Back to My Data
          </v-btn
          >
        </v-container>
      </v-sheet>
    </v-container>
  </div>
</template>

<script>
import statusInformation from "../data/statusInformation";
import actionsInformation from "../data/actionsInformation";
import QuestionIconTooltip from "../components/DynamicHelpResources/QuestionIconTooltip.vue";
import ColoredBorderAlert from "../components/DynamicHelpResources/ColoredBorderAlert.vue";

const IN_PROGRESS = "in_progress";
const IN_EXECUTION = "in_execution";
const ERROR = "error";
const COMPLETED = "completed";

const statuses = [IN_PROGRESS, IN_EXECUTION, ERROR, COMPLETED];

export default {
  name: "MyDataDetails",
  components: {QuestionIconTooltip, ColoredBorderAlert},
  methods: {
    handleButtonClick(action, item) {
      this[action](item);
    },
    continueWorkflow(item) {
      alert("continue workflow " + item);
    },
    cancelExecution(item) {
      alert("cancel execution " + item);
    },
    handlePDFDownload() {
      alert("PDF download!");
    },
    handleJSONDownload() {
      alert("JSON download!");
    },
    handleHTMLDownload() {
      alert("HTML download!");
    },
    handleXMLDownload() {
      alert("XML download!");
    }
  },
  data: () => ({
    IN_PROGRESS,
    IN_EXECUTION,
    ERROR,
    COMPLETED,
    statusInformation,
    actionsInformation,
    datasetTitle: "California Demographic Dataset",
    permissionsError: true,
    generalError: true,
    generalErrorSummary: "Error summary: lorem ipsum dolor sit amet.",
    datasetDetails: [
      {
        label: "DV Installation",
        tooltip: "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        value: "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
      },
      {
        label: "DV File ID / DOI",
        tooltip: "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        value: "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
      },
      {
        label: "Last state in Workflow",
        tooltip: "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        value: "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
      },
      {
        label: "Citation",
        tooltip: "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        value: "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
      },
      {
        label: "Email address to send notification",
        tooltip: "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        value: "example@gmail.com"
      }
    ],
    status: statuses[Math.floor(Math.random() * statuses.length)]
  })
};
</script>
