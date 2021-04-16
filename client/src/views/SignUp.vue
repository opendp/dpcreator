<template>
  <div class="sign-up mt-16">
    <v-container>
      <v-row>
        <v-col offset-md="2" md="8">
          <h1 class="title-size-1">Create new account</h1>
          <v-stepper v-model="signUpStep">
            <v-stepper-content :complete="signUpStep > 1" step="1">
              <SignUpTerms :signUpStep.sync="signUpStep"/>
            </v-stepper-content>
            <v-stepper-content :complete="signUpStep > 2" step="2">
              <SignUpForm/>
            </v-stepper-content>
            <div class="my-5 pl-6">
              <span
              >Already registered?
                <router-link
                    to="/log-in"
                    class="font-weight-bold text-decoration-none"
                >Log in</router-link
                ></span
              >
            </div>
          </v-stepper>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<style lang="scss">
.sign-up {
  .v-stepper {
    box-shadow: unset;
  }

  .v-card__text {
    max-height: 20vh;
    overflow: auto;
  }
}
</style>

<script>
import SignUpForm from "../components/Accounts/SignUp/SignUpForm.vue";
import SignUpTerms from "../components/Accounts/SignUp/SignUpTerms.vue";

export default {
  name: "SignUp",
  components: {SignUpTerms, SignUpForm},

  data: () => ({
    signUpStep: 1
  })
};
</script>
