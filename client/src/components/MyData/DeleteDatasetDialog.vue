<template>
  <v-dialog v-model="dialogDelete" max-width="500px">
    <v-card elevation="2" class="px-10 py-12">
      <v-icon
          style="position: absolute; right: 40px"
          @click="() => $emit('cancel')"
      >mdi-close
      </v-icon
      >
      <v-card-title>
        <h2 class="title-size-2 mb-5 font-weight-bold">
          Are you sure?
        </h2>
      </v-card-title>
      <v-card-text class="text--primary">
        This will delete dataset "{{ datasetInfoName() }}".
      </v-card-text>
      <v-card-actions>
        <Button
            data-test="deleteDatasetConfirm"
            color="primary"
            :click="() => $emit('confirm')"
            label="OK"
        />
        <Button
            outlined
            data-test="deleteDatasetCancel"
            color="primary"
            :click="() => $emit('cancel')"
            label="Cancel"
        />
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import Button from "@/components/DesignSystem/Button";

export default {
  components: {Button},
  name: "DeleteDatasetDialog",
  props: ["dialogDelete", "selectedItem"],
  methods: {
    datasetInfoName() {
      let name = ""
      if (this.selectedItem !== null) {
        name = this.selectedItem.datasetInfo.name
      }
      return name
    }
  }
};
</script>
