<template>
  <div class="validateDatasetStep">
    <h1 class="title-size-1">Validate Dataset</h1>
    <p>
      Firstly, we need to confirm the dataset's characteristics to determine if
      it's adequate for the differential privacy release process.
    </p>
    <ColoredBorderAlert type="warning" class="mb-10 mt-10">
      <template v-slot:content>
        You must complete this questionnaire before starting the process.
      </template>
    </ColoredBorderAlert>
    <v-dialog
        width="50%"
        v-model="suitableDatasetDialog"
        @click:outside="handleGoBackInDialog"
    >
      <template v-slot:activator="{ on }">
        <div>
          <div class="mb-10">
            <span class="font-weight-bold title-size-2 d-flex"
            ><v-icon color="primary" left>mdi-play</v-icon> Does your dataset
              depend on private information of subjects?</span
            >
            <v-radio-group
                v-model="radioDependOnPrivateInformation"
                class="pl-2"
            >
              <v-radio label="Yes." value="yes"></v-radio>
              <v-radio label="No." value="no" v-on="on"></v-radio>
              <v-radio label="I'm unsure." value="unsure"></v-radio>
            </v-radio-group>
          </div>

          <div
              :class="
              `mb-10 ${radioBestDescribesShouldBeDisabled ? 'disabled' : ''}`
            "
          >
            <span class="font-weight-bold title-size-2 d-flex"
            ><v-icon color="primary" left>mdi-play</v-icon> Which of the
              following best describes your dataset?</span
            >
            <v-radio-group
                :disabled="radioBestDescribesShouldBeDisabled"
                v-model="radioBestDescribes"
                class="pl-2"
            >
              <v-radio
                  label="Public information."
                  value="public"
                  v-on="on"
              ></v-radio>
              <v-radio value="notHarmButConfidential">
                <template v-slot:label>
                  <div>
                    Information that, if disclosed,
                    <strong>would not cause material harm</strong>, but which
                    the university has chosen to
                    <strong>keep confidential</strong>.
                  </div>
                </template>
              </v-radio>
              <v-radio value="couldCauseHarm">
                <template v-slot:label>
                  <div>
                    Information that
                    <strong>could cause risk of material harm </strong>to
                    individuals or the university if disclosed.
                  </div>
                </template>
              </v-radio>
              <v-radio value="wouldLikelyCauseHarm">
                <template v-slot:label>
                  <div>
                    Information that
                    <strong>would likely cause serious harm </strong>to
                    individuals or the university if disclosed.
                  </div>
                </template>
              </v-radio>
              <v-radio :value="`wouldCauseSevereHarm`">
                <template v-slot:label>
                  <div>
                    Information that
                    <strong>would cause severe harm </strong>to individuals or
                    the university if disclosed.
                  </div>
                </template>
              </v-radio>
            </v-radio-group>
            <InformationOutlinedAlert>
              <template v-slot:content>
                If you are unsure, please reference our
                <a class="primary--text font-weight-bold d-inline-flex">
                  data classification examples.
                  <v-icon small color="blue darken-1" class="px-2">
                    mdi-open-in-new
                  </v-icon>
                </a>
              </template>
            </InformationOutlinedAlert>
          </div>

          <div
              :class="
              `mb-10 ${
                radioOnlyOneIndividualPerRowShouldBeDisabled ? 'disabled' : ''
              }`
            "
          >
            <span class="font-weight-bold title-size-2 d-flex"
            ><v-icon color="primary" left>mdi-play</v-icon> Does your dataset
              contain only one individual per row?</span
            >
            <v-radio-group
                :disabled="radioOnlyOneIndividualPerRowShouldBeDisabled"
                v-model="radioOnlyOneIndividualPerRow"
                class="pl-2"
            >
              <v-radio label="Yes." value="yes"></v-radio>
              <v-radio label="No." value="no" v-on="on"></v-radio>
              <v-radio label="I'm unsure." value="unsure"></v-radio>
            </v-radio-group>
          </div>
        </div>
      </template>
      <v-card class="pa-12">
        <h2 class="title-size-2 font-weight-bold mb-8">
          The dataset should not be used in DPcreator
        </h2>
        <p class="mb-8 pr-16">
          According to your dataset's characteristics, it is not possible to
          continue with the differential privacy release generation process.
        </p>
        <v-btn
            color="primary"
            class="mr-3 font-weight-bold"
            @click="handleCloseProcess"
        >Close process
        </v-btn
        >
        <v-btn
            color="primary"
            outlined
            class="font-weight-bold"
            @click="handleGoBackInDialog"
        >Go back
        </v-btn
        >
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import InformationOutlinedAlert from "../../components/DynamicHelpResources/DepressedInformationOutlinedAlert.vue";
import ColoredBorderAlert from "../../components/DynamicHelpResources/ColoredBorderAlert.vue";

export default {
  components: {InformationOutlinedAlert, ColoredBorderAlert},
  name: "ValidateDataset",
  data: () => ({
    radioDependOnPrivateInformation: "",
    radioBestDescribes: "",
    radioOnlyOneIndividualPerRow: "",
    suitableDatasetDialog: false
  }),
  computed: {
    radioBestDescribesShouldBeDisabled: function () {
      return (
          this.radioDependOnPrivateInformation === "" ||
          this.radioDependOnPrivateInformation === "no"
      );
    },
    radioOnlyOneIndividualPerRowShouldBeDisabled: function () {
      return (
          this.radioBestDescribes === "" || this.radioBestDescribes === "public"
      );
    }
  },
  methods: {
    handleCloseProcess: function () {
      this.$router.push("/welcome");
    },
    handleGoBackInDialog: function () {
      this.resetRadioButtons();
      this.suitableDatasetDialog = false;
      window.scrollTo(0, 0);
    },
    resetRadioButtons: function () {
      this.radioDependOnPrivateInformation = "";
      this.radioBestDescribes = "";
      this.radioOnlyOneIndividualPerRow = "";
      this.$emit("stepCompleted", 0, false);
    }
  },
  watch: {
    radioOnlyOneIndividualPerRow: function (newValue) {
      if (newValue !== "" && newValue !== "no") {
        this.$emit("stepCompleted", 0, true);
      }
    }
  }
};
</script>
