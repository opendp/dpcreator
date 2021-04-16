<template>
  <div class="contact-us">
    <v-container
        :class="{
        'px-10': $vuetify.breakpoint.xsOnly
      }"
    >
      <v-row>
        <v-col
            offset-md="2"
            offset-sm="1"
            sm="10"
            cols="12"
            :md="contactFormSubmitted ? 10 : 5"
        >
          <ContactUsForm
              :submitted.sync="contactFormSubmitted"
              v-if="!contactFormSubmitted"
              :class="{ 'mb-10': $vuetify.breakpoint.smOnly }"
          />
          <ContactUsSubmitted v-else/>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import ContactUsForm from "../components/ContactUs/ContactUsForm.vue";
import ContactUsSubmitted from "../components/ContactUs/ContactUsSubmitted.vue";
export default {
  name: "ContactUs",
  components: {ContactUsForm, ContactUsSubmitted},
  data: () => ({
    contactFormSubmitted: false
  })
};
</script>
