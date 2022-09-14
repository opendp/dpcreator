<template>
  <v-dialog
      v-model="dialog"
      :width="$vuetify.breakpoint.smAndDown ? '90%' : '50%'"
  >
    <v-card elevation="2" class="px-10 py-12">
      <v-icon
          style="position: absolute; right: 40px"
          @click="() => $emit('update:dialog', false)"
      >mdi-close
      </v-icon
      >
      <v-card-title data-test="editNoiseConfirm">
        <h2 class="title-size-2 mb-5">Are you sure you want to proceed?</h2>
      </v-card-title>

      <v-card-text class="text--primary">
      <div v-html="$t('create statistics.edit epsilon warning')"></div>
      </v-card-text>

      <v-card-actions>
        <Button
            color="primary"
            classes="mr-2 px-5"
            data-test="confirmButton"
            :click="() => $emit('confirm')"
            label="Yes"
        />

        <Button
            color="primary"
            outlined
            classes="px-5"
            :click="() => $emit('update:dialog', false)"
            label="Cancel"
        />
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import Button from "../../../DesignSystem/Button.vue";
export default {
  components: {Button},
  name: "EditNoiseParamsConfirmationDialog",
  props: ["dialog"]
};
</script>
