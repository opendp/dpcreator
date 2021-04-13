<template>
  <v-dialog v-model="dialog" width="50%">
    <v-card elevation="2" class="px-10 py-12">
      <v-card-title>
        <h2 class="title-size-2 mb-5">Are you sure you want to proceed?</h2>
      </v-card-title>

      <v-card-text class="text--primary">
        Changing the epsilon or delta values will
        <strong>directly impact the privacy settings. </strong>We recommend
        using the default values provided by the system.
      </v-card-text>

      <v-card-actions>
        <v-btn color="primary" class="mr-2 px-5" @click="$emit('confirm')">
          Yes
        </v-btn>
        <v-btn
            color="primary"
            outlined
            class="px-5"
            @click="$emit('update:dialog', false)"
        >
          Cancel
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  name: "EditNoiseParamsConfirmationDialog",
  props: ["dialog"]
};
</script>
