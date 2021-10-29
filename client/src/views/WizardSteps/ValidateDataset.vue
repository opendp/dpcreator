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
    <div>
      <div class="mb-10">
        <span class="font-weight-bold title-size-2 d-flex"
        ><v-icon color="primary" left>mdi-play</v-icon> Does your dataset
          depend on private information of subjects?</span
        >
        <v-radio-group
            data-test="radioPrivateInformation"
            v-model="radioDependOnPrivateInformation"
            class="pl-2"
            v-on:change="saveUserInput"
        >
          <RadioItem
              label="Yes."
              value="yes"
              data-test="radioPrivateInformationYes"
          />
          <RadioItem
              label="No."
              value="no"
              :on="{
              change: () =>
                handleInvalidDataset('radioDependOnPrivateInformation')
            }"
          />
          <RadioItem
              label="I'm unsure."
              value="unsure"
              :on="{
              change: () =>
                handleInvalidDataset('radioDependOnPrivateInformation')
            }"
          />
        </v-radio-group>
      </div>

      <div
          :class="`mb-10 ${radioBestDescribesShouldBeDisabled ? 'disabled' : ''}`"
      >
        <span class="font-weight-bold title-size-2 d-flex"
        ><v-icon color="primary" left>mdi-play</v-icon> Which of the following
          best describes your dataset?</span
        >
        <v-radio-group
            data-test="radioBestDescribes"
            :disabled="radioBestDescribesShouldBeDisabled"
            v-model="radioBestDescribes"
            class="pl-2"
        >
          <RadioItem
              label="Public information."
              :value="this.privacyTypes.PUBLIC"
              :data-test="this.privacyTypes.PUBLIC"
              :on="{
              change: () =>
                handleInvalidDataset('radioBestDescribes')
            }"
          />
          <RadioItem :value="this.privacyTypes.NOT_HARM"
                     :data-test="this.privacyTypes.NOT_HARM"
                     :on="{
                change: () =>
                  handleRadioBestDescribes(this.privacyTypes.NOT_HARM)
                }"
          >
            <template v-slot:label>
              <div>
                Information that, if disclosed,
                <strong>would not cause material harm</strong>, but which the
                university has chosen to <strong>keep confidential</strong>.
              </div>
            </template>
          </RadioItem>
          <RadioItem
              :value="this.privacyTypes.COULD_HARM"
              :on="{
              change: () =>
                handleRadioBestDescribes(this.privacyTypes.COULD_HARM)
            }"
          >
            <template v-slot:label>
              <div>
                Information that
                <strong>could cause risk of material harm </strong>to
                individuals or the university if disclosed.
              </div>
            </template>
          </RadioItem>
          <RadioItem
              :value="this.privacyTypes.LIKELY_HARM"
              :on="{
              change: () =>
                handleRadioBestDescribes(this.privacyTypes.LIKELY_HARM)
            }"
          >
            <template v-slot:label>
              <div>
                Information that
                <strong>would likely cause serious harm </strong>to individuals
                or the university if disclosed.
              </div>
            </template>
          </RadioItem>
          <RadioItem
              :value="this.privacyTypes.SEVERE_HARM"
              :on="{
              change: () =>
                handleInvalidDataset('radioBestDescribes')
            }"
          >
            <template v-slot:label>
              <div>
                Information that
                <strong>would cause severe harm </strong>to individuals or the
                university if disclosed.
              </div>
            </template>
          </RadioItem>
        </v-radio-group>
        <AdditionalInformationAlert>
          <template v-slot:content>
            If you are unsure, please reference our
            <a class="primary--text font-weight-bold d-inline-flex">
              data classification examples.
              <v-icon small color="blue darken-1" class="px-2">
                mdi-open-in-new
              </v-icon>
            </a>
          </template>
        </AdditionalInformationAlert>
      </div>

      <div
          :class="
          `mb-10 ${
            radioOnlyOneIndividualPerRowShouldBeDisabled ? 'disabled' : ''
          }`
        "
      >
        <span class="font-weight-bold title-size-2 d-flex"
        ><v-icon color="primary" left>mdi-play</v-icon> Does each individual appear in only one row?</span>
        <v-radio-group
            :disabled="radioOnlyOneIndividualPerRowShouldBeDisabled"
            v-model="radioOnlyOneIndividualPerRow"
            class="pl-2"
            v-on:change="saveUserInput"
        >
          <RadioItem label="Yes." value="yes"
                     data-test="radioOnlyOneIndividualPerRowYes"/>
          <RadioItem
              label="No."
              value="no"
              :on="{
              change: () => handleInvalidDataset('radioOnlyOneIndividualPerRow')
            }"
          />
          <RadioItem
              label="I'm unsure."
              value="unsure"
               :on="{
              change: () => handleInvalidDataset('radioOnlyOneIndividualPerRow')
            }"
          />
        </v-radio-group>
      </div>
    </div>
    <v-dialog
        :width="$vuetify.breakpoint.smAndDown ? '90%' : '50%'"
        v-model="suitableDatasetDialogIsOpen"
        @click:outside="handleGoBackInDialog"
    >
      <v-card class="pa-12">
        <v-icon
            style="position: absolute; right: 40px"
            @click="handleGoBackInDialog"
        >mdi-close
        </v-icon
        >
        <h2 class="title-size-2 font-weight-bold mb-8">
          The dataset should not be used in DPcreator
        </h2>
        <p class="mb-8 pr-16">
          According to your dataset's characteristics, it is not possible to
          continue with the differential privacy release generation process.
        </p>
        <Button
            color="primary"
            classes="mr-2 mb-2 font-weight-bold"
            :click="handleCloseProcess"
            label="Close process"
        />
        <Button
            color="primary"
            outlined
            classes="font-weight-bold mb-2"
            :click="handleGoBackInDialog"
            label="Go back"
        />
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import Button from "../../components/DesignSystem/Button.vue";
import RadioItem from "../../components/DesignSystem/RadioItem.vue";
import AdditionalInformationAlert from "../../components/DynamicHelpResources/AdditionalInformationAlert.vue";
import ColoredBorderAlert from "../../components/DynamicHelpResources/ColoredBorderAlert.vue";
import NETWORK_CONSTANTS from "../../router/NETWORK_CONSTANTS";

import {mapState, mapGetters} from "vuex";

export default {
  components: {
    AdditionalInformationAlert,
    ColoredBorderAlert,
    RadioItem,
    Button
  },
  name: "ValidateDataset",
  data: () => ({
    radioDependOnPrivateInformation: "",
    radioBestDescribes: "",
    radioOnlyOneIndividualPerRow: "",
    suitableDatasetDialogIsOpen: false,
    optionToUnset: "",
    defaultEpsilon: null,
    defaultDDelta: null,
    privacyTypes: {
      PUBLIC: "public",
      NOT_HARM: "notHarmButConfidential",
      COULD_HARM: "couldCauseHarm",
      LIKELY_HARM: "wouldLikelyCauseHarm",
      SEVERE_HARM: "wouldCauseSevereHarm"
    }


  }),
  created() {
    // Initialize questions with previously input values,
    // if they exist
    if (this.getDepositorSetupInfo.datasetQuestions !== null) {
      this.radioDependOnPrivateInformation =
          this.getDepositorSetupInfo.datasetQuestions.radioDependOnPrivateInformation
      this.radioOnlyOneIndividualPerRow =
          this.getDepositorSetupInfo.datasetQuestions.radioOnlyOneIndividualPerRow
      this.radioBestDescribes =
          this.getDepositorSetupInfo.datasetQuestions.radioBestDescribes

    }
  },
  computed: {
    ...mapState('dataset', ['datasetInfo']),
    ...mapGetters('dataset', ['getDepositorSetupInfo']),
    radioBestDescribesShouldBeDisabled: function () {
      return (
          this.radioDependOnPrivateInformation === "" ||
          this.radioDependOnPrivateInformation === "no"
      );
    },
    radioOnlyOneIndividualPerRowShouldBeDisabled: function () {
      return (
          this.radioBestDescribes === "" || this.radioBestDescribes === this.privacyTypes.PUBLIC
      );
    }
  },
  methods: {
    saveUserInput() {
      const userInput = {
        datasetQuestions: {
          radioDependOnPrivateInformation: this.radioDependOnPrivateInformation,
          radioBestDescribes: this.radioBestDescribes,
          radioOnlyOneIndividualPerRow: this.radioOnlyOneIndividualPerRow,
        },
        defaultEpsilon: this.defaultEpsilon,
        defaultDelta: this.defaultDDelta,
        // Have to set the actual epsilon, not just the default
        // in order to complete the depositor setup (which happens before
        // the Create Statistics page.)
        epsilon: this.defaultEpsilon,
        delta: this.defaultDDelta
      }
      const payload = {objectId: this.getDepositorSetupInfo.objectId, props: userInput}
      this.$store.dispatch('dataset/updateDepositorSetupInfo',
          payload)

    },
    /* Epsilon & Delta are derived from the answers to the level of harm question,
     taken from the original PSI application:

     Information the disclosure of which would not cause material harm,
     but which the University has chosen to keep confidential: (ε=1, δ=10-5=0.00001)

     Information that could cause risk of material harm to individuals
      or the University if disclosed: (ε=.25, δ=10-6=0.000001)

      Information that would likely cause serious harm to individuals
      or the University if disclosed: (ε=.05, δ=10-7=0.0000001)
     */
    updateEpsilonDelta(option) {

      // Set epsilon for the three valid privacyTypes.
      // The other types will require the user to go back and change their
      // answer, so in that case set the values to null.
      if (option === this.privacyTypes.NOT_HARM) {
        this.defaultEpsilon = 1
        this.defaultDDelta = 0.00001
      } else if (option === this.privacyTypes.COULD_HARM) {
        this.defaultEpsilon = .25
        this.defaultDDelta = 0.000001
      } else if (option === this.privacyTypes.LIKELY_HARM) {
        this.defaultEpsilon = .05
        this.defaultDDelta = .0000001
      }
      this.saveUserInput()
    },
    handleRadioBestDescribes: function (option) {
      console.log('updating epsilon/delta for radioBestDescribes = ' + option)
      this.updateEpsilonDelta(option)
    },
    handleInvalidDataset: function (invalidOption) {
      this.optionToUnset = invalidOption;
      this.suitableDatasetDialogIsOpen = true;
      this.$emit("stepCompleted", 0, false);
    },
    handleCloseProcess: function () {
      this.$router.push(NETWORK_CONSTANTS.WELCOME.PATH);
    },
    handleGoBackInDialog: function () {
      this[this.optionToUnset] = "";
      this.suitableDatasetDialogIsOpen = false;
    },
    resetRadioButtons: function () {
      this.radioDependOnPrivateInformation = "";
      this.radioBestDescribes = "";
      this.radioOnlyOneIndividualPerRow = "";
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
