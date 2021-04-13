<template>
  <v-dialog v-model="dialogDelete" max-width="500px">
    <v-card>
      <v-card-title
      >
        <v-spacer></v-spacer>
        Are you sure you want to delete this
        item?
        <v-spacer></v-spacer
        >
      </v-card-title>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="blue darken-1" text @click="$emit('cancel')"
        >Cancel
        </v-btn
        >
        <v-btn color="blue darken-1" text @click="$emit('confirm')">OK</v-btn>
        <v-spacer></v-spacer>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  name: "DeleteStatisticDialog",
  props: ["dialogDelete"]
};
</script>
