<template>
  <v-container>
    <v-row>
      <v-col offset-sm="1" sm="10" md="12" offset-md="0">
        <h2 class="title-size-1 text-center mb-10">DP Creator Concepts</h2>
        <LinearBox
            :class="{
            'mb-6': $vuetify.breakpoint.xsOnly,
            'mb-12': $vuetify.breakpoint.smAndUp
          }"
        >
          <template v-slot:content>
            <h2 class="title-size-1">More Information on Epsilon</h2>
            <p class="grey--text text--darken-2">More information epsilon text</p>
          </template>
        </LinearBox>
        <LinearBox
            id="more-info-delta"
            :class="{
            'mb-6': $vuetify.breakpoint.xsOnly,
            'mb-12': $vuetify.breakpoint.smAndUp
          }"
        >
          <template v-slot:content>
            <h2 class="title-size-1">More Information on Delta</h2>
            <p class="grey--text text--darken-2">More information delta text</p>
          </template>
        </LinearBox>
        <LinearBox

            :class="{
            'mb-6': $vuetify.breakpoint.xsOnly,
            'mb-12': $vuetify.breakpoint.smAndUp
          }"
        >
          <template v-slot:content>
            <h2 class="title-size-1">More Information on Confidence Level</h2>
            <p id="more-info-confidence" class="grey--text text--darken-2">more information confidence Level Text</p>
          </template>
        </LinearBox>

      </v-col>
    </v-row>
    <span></span>
  </v-container>
</template>

<style lang="scss" scoped>
.linear-box:last-child {
  margin-bottom: 15px !important;
}
</style>

<script>
import LinearBox from "../DesignSystem/Boxes/LinearBox.vue";

export default {
  components: {LinearBox},
  name: "ExplanatoryText"
};
</script>
