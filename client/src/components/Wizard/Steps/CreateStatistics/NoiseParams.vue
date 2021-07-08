<template>
  <div>
    <v-row class="mb-10">
      <v-col>
        <div
            class="borderBottom soft_primary grey--text text--darken-2
		  pa-3 top-borders-radius noise-params d-flex 
		  justify-space-between"
        >
          <span>Epsilon (&epsilon;)</span>
          <span>
            {{ epsilon }}
            <v-icon right @click="emitEditEvent">mdi-pencil</v-icon>
          </span>
        </div>
        <a href="http://" class="primary--text caption"
        >More information about Epsilon
        </a>
      </v-col>
      <v-col>
        <div
            class="borderBottom soft_primary grey--text text--darken-2
		  pa-3 top-borders-radius noise-params d-flex 
		  justify-space-between"
        >
          <span>Delta (&delta;)</span>
          <span>
            {{ delta }}
            <v-icon right @click="emitEditEvent">mdi-pencil</v-icon>
          </span>
        </div>
        <a href="http://" class="primary--text caption">
          More information about Delta
        </a>
      </v-col>
      <v-col>
        <div
            class="borderBottom soft_primary grey--text text--darken-2 pa-3 top-borders-radius noise-params d-flex justify-space-between"
        >
          <span>Confidence Level</span>
          <span>
            {{ confidenceLevel }}
            <v-icon right @click="emitEditEvent">mdi-pencil</v-icon>
          </span>
        </div>
        <a href="http://" class="primary--text caption">
          More information about Confidence Levels
        </a>
      </v-col>
    </v-row>
  </div>
</template>

<style lang="scss">
.v-application .borderBottom {
  border-bottom: 1px solid rgba(0, 0, 0, 0.42) !important;
}
</style>

<script>
export default {
  name: "NoiseParams",
  props: ["epsilon", "delta", "confidenceLevel"],
  methods: {
    emitEditEvent: function () {
      this.$emit("editNoiseParams");
    }
  }
};
</script>
