<template>
  <v-dialog
      v-model="dialogEditNoiseParams"
      :width="$vuetify.breakpoint.smAndDown ? '90%' : '50%'"
      @click:outside="handleCancelEditNoiseParamsDialog"
  >
    <v-card elevation="2" class="px-10 py-12 editNoiseParams">
      <v-icon
          style="position: absolute; right: 40px; top: 30px;"
          @click="handleCancelEditNoiseParamsDialog"
      >mdi-close
      </v-icon
      >
      <v-card-title>
        <h2 class="title-size-2 mb-5">
          Please confirm the epsilon (&epsilon;) and delta (&delta;) values.
        </h2>
      </v-card-title>
      <v-card-text class="text--primary">
        <span>
          <div v-html="$t('create statistics.confirm 1')"></div>
        </span>
        <span class="grey--text text--darken-2">
          (i.e.
          <span class="font-italic">
            “Information that could cause risk of harm to individuals or the
            university if disclosed”</span
          >)<br/>
          <span class="primary--text font-weight-bold pointer"
          >Modify this selection
            <v-icon small color="primary">mdi-open-in-new</v-icon></span
          >
        </span>
        <div
            class="borderBottom soft_primary grey--text text--darken-2 pa-3 my-5 top-borders-radius noise-params d-flex justify-space-between width50"
        >
          <span>Epsilon (&epsilon;)</span>
          <input
              class="text-right font-weight-bold"
              type="number"
              v-model="editEpsilon"
          />
        </div>
        <small class="mr-16 grey--text text--darken-2">
          <div v-html="$t('create statistics.confirm 2')"></div>
        </small>
        <div
            class="borderBottom soft_primary grey--text text--darken-2 pa-3 my-5 top-borders-radius noise-params d-flex justify-space-between width50"
        >
          <span>Delta (x)</span>
          <input
              class="text-right font-weight-bold"
              type="number"
              v-model="editDelta"
          />
        </div>
        <small class="mr-16 mb-5 d-block grey--text text--darken-2">
          <div v-html="$t('create statistics.confirm 3')"></div>
        </small>
        <div
            class="soft_primary grey--text text--darken-2 top-borders-radius width50 pl-3 mb-5 borderBottom"
        >
          <span class="d-inline-block width50">Confidence Level</span>
          <v-autocomplete
              v-model="editConfidenceLevel"
              :items="confidenceLevelOptions"
              class="d-inline-block confidenceLevel pl-5 pt-2 font-weight-bold width50 text-right"
              placeholder="Select..."
          ></v-autocomplete>
        </div>
        <AdditionalInformationAlert>
          <template v-slot:content>
            <span
            >
              <div v-html="$t('create statistics.confirm 4')"></div>
              <a href="http://" class="text-decoration-none primary--text"
              >Watch video to learn more.</a
              >
            </span>
          </template>
        </AdditionalInformationAlert>
      </v-card-text>
      <v-card-actions>
        <Button
            color="primary"
            classes="mr-2 px-5"
            :click="handleSaveEditNoiseParamsDialog"
            label="Confirm"
        />
        <Button
            color="primary"
            outlined
            classes="px-5"
            :click="handleCancelEditNoiseParamsDialog"
            label="Cancel"
        />
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<style lang="scss">
.v-application .borderBottom {
  border-bottom: 1px solid rgba(0, 0, 0, 0.42) !important;
}

.editNoiseParams {
  .confidenceLevel {
    .v-input__slot {
      margin-bottom: 0;
    }

    .v-input__slot:before {
      border: none;
    }

    .v-text-field__details {
      display: none;
    }
  }

  .v-autocomplete input {
    text-align: right;
  }
}
</style>

<script>
import Button from "../../../DesignSystem/Button.vue";
import AdditionalInformationAlert from "../../../DynamicHelpResources/AdditionalInformationAlert";

export default {
  name: "EditNoiseParamsDialog",
  components: {
    AdditionalInformationAlert,
    Button
  },
  data: function () {
    return {
      editEpsilon: this.epsilon,
      editDelta: this.delta,
      editConfidenceLevel: this.confidenceLevel,
      confidenceLevelOptions: [
        {text: "99%", value: .99},
        {text: "95%", value: .95},
        {text: "90%", value: .90},]
    };
  },
  props: ["dialogEditNoiseParams", "epsilon", "delta", "confidenceLevel"],
  methods: {
    handleCancelEditNoiseParamsDialog() {
      this.editEpsilon = this.epsilon;
      this.editDelta = this.delta;
      this.editConfidenceLevel = this.confidenceLevel;
      this.$emit("update:dialogEditNoiseParams", false);
    },
    handleSaveEditNoiseParamsDialog() {
      this.$emit(
          "noiseParamsUpdated",
          this.editEpsilon,
          this.editDelta,
          this.editConfidenceLevel
      );
      this.$emit("update:dialogEditNoiseParams", false);
    }
  }
};
</script>
