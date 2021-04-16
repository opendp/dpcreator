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
        <v-radio-group v-model="radioDependOnPrivateInformation" class="pl-2">
          <RadioItem label="Yes." value="yes"/>
          <!-- TODO: add the :on attribute to all options that should invalidate the dataset -->
          <RadioItem
              label="No."
              value="no"
              :on="{
              change: () =>
                handleInvalidDataset('radioDependOnPrivateInformation')
            }"
          />
          <RadioItem label="I'm unsure." value="unsure"/>
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
            :disabled="radioBestDescribesShouldBeDisabled"
            v-model="radioBestDescribes"
            class="pl-2"
        >
          <RadioItem
              label="Public information."
              value="public"
              :on="{
              change: () => handleInvalidDataset('radioBestDescribes')
            }"
          />
          <RadioItem value="notHarmButConfidential">
            <template v-slot:label>
              <div>
                Information that, if disclosed,
                <strong>would not cause material harm</strong>, but which the
                university has chosen to <strong>keep confidential</strong>.
              </div>
            </template>
          </RadioItem>
          <RadioItem value="couldCauseHarm">
            <template v-slot:label>
              <div>
                Information that
                <strong>could cause risk of material harm </strong>to
                individuals or the university if disclosed.
              </div>
            </template>
          </RadioItem>
          <RadioItem value="wouldLikelyCauseHarm">
            <template v-slot:label>
              <div>
                Information that
                <strong>would likely cause serious harm </strong>to individuals
                or the university if disclosed.
              </div>
            </template>
          </RadioItem>
          <RadioItem value="wouldCauseSevereHarm">
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
        ><v-icon color="primary" left>mdi-play</v-icon> Does your dataset
          contain only one individual per row?</span
        >
        <v-radio-group
            :disabled="radioOnlyOneIndividualPerRowShouldBeDisabled"
            v-model="radioOnlyOneIndividualPerRow"
            class="pl-2"
        >
          <RadioItem label="Yes." value="yes"/>
          <RadioItem
              label="No."
              value="no"
              :on="{
              change: () => handleInvalidDataset('radioOnlyOneIndividualPerRow')
            }"
          />
          <RadioItem label="I'm unsure." value="unsure"/>
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
    optionToUnset: ""
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
