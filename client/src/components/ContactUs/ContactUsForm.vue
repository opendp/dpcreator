<template>
  <div>
    <h1 class="title-size-1">Contact us</h1>
    <v-form
        v-model="validContactForm"
        ref="contactForm"
        @submit.prevent="handleFormSubmit"
    >
      <v-text-field
          v-model="name"
          label="Name"
          :rules="nameRules"
      ></v-text-field>
      <v-text-field
          v-model="email"
          label="Email"
          :rules="emailRules"
      ></v-text-field>
      <v-textarea
          v-model="message"
          class="mt-7 mb-4"
          label="Message"
          :rules="messageRules"
          filled
      ></v-textarea>
      <Button
          type="submit"
          color="primary"
          :disabled="!validContactForm"
          label="Send"
          :class="{
          'width80 mx-auto d-block mb-5': $vuetify.breakpoint.xsOnly
        }"
      />
    </v-form>
  </div>
</template>

<script>
import Button from "../DesignSystem/Button.vue";
export default {
  components: {Button},
  name: "ContactUsForm",
  methods: {
    handleFormSubmit: function () {
      if (this.$refs.contactForm.validate()) {
        //TODO: Implement Contact Form logic
        this.$emit("update:submitted", true);
      }
    }
  },
  data: () => ({
    name: "",
    nameRules: [v => !!v || "Your name is required"],
    email: "",
    emailRules: [
      v => !!v || "E-mail is required",
      v => /.+@.+\..+/.test(v) || "E-mail must be valid"
    ],
    message: "",
    messageRules: [v => !!v || "Your message is required"],
    validContactForm: false
  })
};
</script>
