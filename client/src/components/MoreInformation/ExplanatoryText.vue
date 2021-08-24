<template>
  <v-container>
    <v-row>
      <v-col offset-sm="1" sm="10" md="12" offset-md="0">
        <h2 class="title-size-1 text-center mb-10">{{ $t('more information.title') }}</h2>
        <LinearBox
            :class="{
            'mb-6': $vuetify.breakpoint.xsOnly,
            'mb-12': $vuetify.breakpoint.smAndUp
          }"
        >
          <template v-slot:content>
            <h2 class="title-size-1">{{ $t('more information.differential privacy title') }}</h2>
            <p id="more-info-dp" class="grey--text text--darken-2">{{
                $t('more information.differential privacy text')
              }}</p>
          </template>
        </LinearBox>
        <LinearBox
            :class="{
            'mb-6': $vuetify.breakpoint.xsOnly,
            'mb-12': $vuetify.breakpoint.smAndUp
          }"
        >
          <template v-slot:content>
            <h2 class="title-size-1">{{ $t('more information.registered dataverses title') }}</h2>
            <p id="more-info-dataverses" class="grey--text text--darken-2">
              {{ $t('more information.registered dataverses text') }}</p>
            <ul>
              <li v-for="item in registeredDvs">
                <a :href="item.dataverseUrl">{{ item.name }}</a>
              </li>
            </ul>

          </template>
        </LinearBox>
        <LinearBox
            :class="{
            'mb-6': $vuetify.breakpoint.xsOnly,
            'mb-12': $vuetify.breakpoint.smAndUp
          }"
        >
          <template v-slot:content>
            <h2 class="title-size-1">{{ $t('more information.epsilon title') }}</h2>
            <p id="more-info-epsilon" class="grey--text text--darken-2">{{ $t('more information.epsilon text') }}</p>
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
            <h2 class="title-size-1">{{ $t('more information.delta title') }}</h2>
            <p class="grey--text text--darken-2">{{ $t('more information.delta text') }}</p>
          </template>
        </LinearBox>
        <LinearBox

            :class="{
            'mb-6': $vuetify.breakpoint.xsOnly,
            'mb-12': $vuetify.breakpoint.smAndUp
          }"
        >
          <template v-slot:content>
            <h2 class="title-size-1">{{ $t('more information.confidence title') }}</h2>
            <p id="more-info-confidence" class="grey--text text--darken-2">{{
                $t('more information.confidence text')
              }}</p>
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
  name: "ExplanatoryText",
  props: ["registeredDvs"]
};
</script>
