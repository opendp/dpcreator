<template>
  <v-container>
    <v-row>
      <v-col>
        <h2 class="title-size-1 text-center mb-10">Terms of Service</h2>
        <LinearBox
            v-for="(term, index) in termsOfService"
            :key="index"
            class="mb-12"
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
        <v-checkbox
            v-model="termsOfServiceCheckbox"
            label="I have read and agree to the Terms of Service."
            @change="termsOfServiceChange"
        >
        </v-checkbox>
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
  name: "TermsOfService",
  methods: {
    termsOfServiceChange: function () {
      this.$root.$emit(
          "termsOfServiceCheckboxChanged",
          this.termsOfServiceCheckbox
      );
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
