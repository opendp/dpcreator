<template>
  <v-dialog
      v-model="dialogEditNoiseParams"
      width="60%"
      @click:outside="handleCancelEditNoiseParamsDialog"
  >
    <v-card elevation="2" class="px-10 py-12">
      <v-card-title>
        <h2 class="title-size-2 mb-5">
          Please confirm the epsilon (x) and delta (x) values.
        </h2>
      </v-card-title>
      <v-card-text class="text--primary">
        <span>
          <strong
          >The recommended values below are based upon your dataset type
            selection <br
            /></strong>
        </span>
        <span class="grey--text text--darken-2">
          (i.e.
          <span class="font-italic">
            “Information that could cause risk of harm to individuals or the
            university if disclosed”</span
          >)
          <span class="primary--text font-weight-bold pointer"
          >Modify this selection
            <v-icon small color="primary">mdi-open-in-new</v-icon></span
          >
        </span>
        <div
            class="blue lighten-4 grey--text text--darken-2 pa-3 my-5 top-borders-radius noise-params d-flex justify-space-between width50"
        >
          <span>Epsilon (x)</span>
          <input class="text-right" type="number" v-model="editEpsilon"/>
        </div>
        <p class="mr-16 grey--text text--darken-2">
          Note: Larger X corresponds to larger privacy loss budget, and hence,
          less privacy. We do not recommend X exceding 1.
        </p>
        <div
            class="blue lighten-4 grey--text text--darken-2 pa-3 my-5 top-borders-radius noise-params d-flex justify-space-between width50"
        >
          <span>Delta (x)</span>
          <input class="text-right" type="number" v-model="editDelta"/>
        </div>
        <p class="mr-16 grey--text text--darken-2">
          Note: X is the probability of a blatant privacy violation. X values
          larger than the reciprocal of the dataset size are not allowed.
        </p>
        <DepressedInformationOutlinedAlert>
          <template v-slot:content>
            <span
            >The level of privacy protection for individuals in the dataset is
              governed by two privacy-loss parametres - x & x.
              <a href="http://" class="text-decoration-none primary--text"
              >Watch video to learn more.</a
              >
            </span>
          </template>
        </DepressedInformationOutlinedAlert>
      </v-card-text>
      <v-card-actions>
        <v-btn
            color="primary"
            class="mr-2 px-5"
            @click="handleSaveEditNoiseParamsDialog"
        >
          Confirm
        </v-btn>
        <v-btn
            color="primary"
            outlined
            class="px-5"
            @click="handleCancelEditNoiseParamsDialog"
        >
          Cancel
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import DepressedInformationOutlinedAlert from "../../../DynamicHelpResources/DepressedInformationOutlinedAlert";

export default {
  name: "EditNoiseParamsDialog",
  components: {
    DepressedInformationOutlinedAlert
  },
  data: function () {
    return {
      editEpsilon: this.epsilon,
      editDelta: this.delta
    };
  },
  props: ["dialogEditNoiseParams", "epsilon", "delta"],
  methods: {
    handleCancelEditNoiseParamsDialog() {
      this.editEpsilon = this.epsilon;
      this.editDelta = this.delta;
      this.$emit("update:dialogEditNoiseParams", false);
    },
    handleSaveEditNoiseParamsDialog() {
      this.$emit("noiseParamsUpdated", this.editEpsilon, this.editDelta);
      this.$emit("update:dialogEditNoiseParams", false);
    }
  }
};
</script>
