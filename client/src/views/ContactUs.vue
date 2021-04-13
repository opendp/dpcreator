<template>
  <div class="contact-us mt-16">
    <v-container>
      <v-row>
        <v-col offset-md="2" cols="10" :md="contactFormSubmitted ? 10 : 5">
          <ContactUsForm
              :submitted.sync="contactFormSubmitted"
              v-if="!contactFormSubmitted"
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
