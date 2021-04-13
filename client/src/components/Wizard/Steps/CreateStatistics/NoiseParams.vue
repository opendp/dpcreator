<template>
  <div>
    <v-row class="mb-10">
      <v-col>
        <div
            class="blue lighten-4 grey--text text--darken-2
		  pa-3 top-borders-radius noise-params d-flex 
		  justify-space-between"
        >
          <span>Epsilon (x)</span>
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
            class="blue lighten-4 grey--text text--darken-2
		  pa-3 top-borders-radius noise-params d-flex 
		  justify-space-between"
        >
          <span>Delta (x)</span>
          <span>
            {{ delta }}
            <v-icon right @click="emitEditEvent">mdi-pencil</v-icon>
          </span>
        </div>
        <a href="http://" class="primary--text caption">
          More information about Epsilon
        </a>
      </v-col>
      <v-col>
        <div
            class="blue lighten-4 grey--text text--darken-2 pa-3 top-borders-radius noise-params d-flex justify-space-between"
        >
          <span>Confidence level</span>
          <span>
            {{ confidenceLevel }}
            <v-icon right @click="emitEditEvent">mdi-pencil</v-icon>
          </span>
        </div>
        <a href="http://" class="primary--text caption">
          More information about Epsilon
        </a>
      </v-col>
    </v-row>
  </div>
</template>

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
