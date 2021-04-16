<template>
  <v-container>
    <v-row>
      <v-col offset-sm="1" sm="10" md="12" offset-md="0">
        <h2 class="title-size-1 text-center mb-10">Terms of Service</h2>
        <LinearBox
            v-for="(term, index) in termsOfService"
            :key="index"
            :class="{
            'mb-6': $vuetify.breakpoint.xsOnly,
            'mb-12': $vuetify.breakpoint.smAndUp
          }"
        >
          <template v-slot:content>
            <h2 class="title-size-1">{{ term.title }}</h2>
            <p class="grey--text text--darken-2">{{ term.content }}</p>
          </template>
        </LinearBox>
      </v-col>
    </v-row>
    <v-row>
      <v-col class="d-flex justify-center">
        <Checkbox
            :class="{ 'width80 mx-auto': $vuetify.breakpoint.xsOnly }"
            :value.sync="termsOfServiceCheckbox"
            text="I have read and agree to the Terms of Service."
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
    termsOfService: [
      {
        title: "Who should use this tool and why?",
        content:
            "Lorem ipsum dolor sit amet consectetur adipisicing elit. Animi iusto in, voluptas quia fugiat soluta labore consectetur harum repellendus accusamus quisquam quasi velit vero totam, optio assumenda atque obcaecati eum!"
      },
      {
        title: "What statistics can be released using this tool?",
        content:
            "Lorem ipsum dolor sit amet consectetur adipisicing elit. Animi iusto in, voluptas quia fugiat soluta labore consectetur harum repellendus accusamus quisquam quasi velit vero totam, optio assumenda atque obcaecati eum!"
      },
      {
        title: "What type of files are appropiate?",
        content:
            "Lorem ipsum dolor sit amet consectetur adipisicing elit. Animi iusto in, voluptas quia fugiat soluta labore consectetur harum repellendus accusamus quisquam quasi velit vero totam, optio assumenda atque obcaecati eum!"
      },
      {
        title: "What can be done with the DP release?",
        content:
            "Lorem ipsum dolor sit amet consectetur adipisicing elit. Animi iusto in, voluptas quia fugiat soluta labore consectetur harum repellendus accusamus quisquam quasi velit vero totam, optio assumenda atque obcaecati eum!"
      }
    ]
  })
};
</script>
