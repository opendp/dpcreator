<template>
  <v-container>
    <v-row>
      <v-col offset-sm="1" sm="10" md="12" offset-md="0">
        <h2 class="title-size-1 text-center mb-10">{{ $t('home.service section title') }}</h2>
        <LinearBox
            :class="{
            'mb-6': $vuetify.breakpoint.xsOnly,
            'mb-12': $vuetify.breakpoint.smAndUp
          }"
        >
          <template v-slot:content>
            <h2 class="title-size-1">{{ $t('home.service1 title') }}</h2>
            <p class="grey--text text--darken-2">{{ $t('home.service1 text') }}</p>
          </template>
        </LinearBox>
        <LinearBox
            :class="{
            'mb-6': $vuetify.breakpoint.xsOnly,
            'mb-12': $vuetify.breakpoint.smAndUp
          }"
        >
          <template v-slot:content>
            <h2 class="title-size-1">{{ $t('home.service2 title') }}</h2>
            <p class="grey--text text--darken-2">{{ $t('home.service2 text') }}</p>
          </template>
        </LinearBox>
        <LinearBox
            :class="{
            'mb-6': $vuetify.breakpoint.xsOnly,
            'mb-12': $vuetify.breakpoint.smAndUp
          }"
        >
          <template v-slot:content>
            <h2 class="title-size-1">{{ $t('home.service3 title') }}</h2>
            <p class="grey--text text--darken-2">{{ $t('home.service3 text') }}</p>
          </template>
        </LinearBox>
        <LinearBox
            :class="{
            'mb-6': $vuetify.breakpoint.xsOnly,
            'mb-12': $vuetify.breakpoint.smAndUp
          }"
        >
          <template v-slot:content>
            <h2 class="title-size-1">{{ $t('home.service4 title') }}</h2>
            <p class="grey--text text--darken-2">{{ $t('home.service4 text') }}</p>
          </template>
        </LinearBox>
      </v-col>
    </v-row>
    <v-row>
      <v-col class="d-flex justify-center">
        <Checkbox
            :class="{ 'width80 mx-auto': $vuetify.breakpoint.xsOnly }"
            :value.sync="termsOfServiceCheckbox"
            :text=checkboxString
        />
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
import Checkbox from "../DesignSystem/Checkbox.vue";
export default {
  components: {LinearBox, Checkbox},
  name: "TermsOfService",
  watch: {
    termsOfServiceCheckbox: function (newCheckboxValue) {
      this.$root.$emit("termsOfServiceCheckboxChanged", newCheckboxValue);
    }
  },
  data: () => ({
    termsOfServiceCheckbox: false,

  }),
  computed: {
    checkboxString() {
      return this.$t('home.checkbox')
    }
  }


};
</script>
