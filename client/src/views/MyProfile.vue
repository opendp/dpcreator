<template>
  <div class="my-profile mt-16">
    <v-container>
      <v-sheet rounded="lg">
        <v-container class="py-5">
          <v-row>
            <v-col offset-md="2" md="4">
              <h1 class="title-size-1">My Profile</h1>
              <h2 class="title-size-2 mt-8">Edit account information</h2>
              <v-form @submit.prevent="handleEditAccountInformation">
                <v-text-field
                    v-model="username"
                    label="Username"
                    required
                ></v-text-field>
                <v-text-field
                    v-model="email"
                    label="Email"
                    required
                    :rules="emailRules"
                    type="email"
                ></v-text-field>
                <div class="mt-5 mb-10">
                  <v-btn type="submit" color="primary" class="mr-5"
                  >Save changes
                  </v-btn
                  >
                  <v-btn color="primary" outlined @click="$router.push('/')"
                  >Cancel
                  </v-btn>
                </div>
              </v-form>
              <h2 class="title-size-2 mt-10">Change password</h2>
              <v-form @submit.prevent="handleChangePassword">
                <v-text-field
                    v-model="password"
                    :append-icon="show1 ? 'mdi-eye' : 'mdi-eye-off'"
                    :type="show1 ? 'text' : 'password'"
                    name="input-10-1"
                    label="Current password"
                    @click:append="show1 = !show1"
                ></v-text-field>
                <v-text-field
                    v-model="newPassword"
                    :append-icon="show2 ? 'mdi-eye' : 'mdi-eye-off'"
                    :type="show2 ? 'text' : 'password'"
                    name="input-10-2"
                    label="Password"
                    :rules="passwordRules"
                    counter
                    @click:append="show2 = !show2"
                ></v-text-field>
                <span class="pl-6 d-block grey--text text--darken-2"
                >Your <strong>password</strong> must be at least 6 characters
                  long and must contain letters, numbers and special characters.
                  Cannot contain whitespace.</span
                >
                <v-text-field
                    v-model="confirmNewPassword"
                    :append-icon="show3 ? 'mdi-eye' : 'mdi-eye-off'"
                    :type="show3 ? 'text' : 'password'"
                    :rules="[confirmNewPasswordRules]"
                    name="input-10-3"
                    label="Confirm password"
                    counter
                    @click:append="show3 = !show3"
                ></v-text-field>
                <div class="mt-5 mb-10">
                  <v-btn type="submit" color="primary" class="mr-5"
                  >Save changes
                  </v-btn
                  >
                  <v-btn color="primary" outlined @click="$router.push('/')"
                  >Cancel
                  </v-btn>
                </div>
              </v-form>
            </v-col>
          </v-row>
        </v-container>
      </v-sheet>
    </v-container>
  </div>
</template>

<script>
export default {
  name: "MyProfile",
  methods: {
    confirmNewPasswordRules() {
      return (
          this.newPassword === this.confirmNewPassword || `Passwords don't match`
      );
    },
    handleEditAccountInformation() {
      alert("edit account information form submitted!");
    },
    handleChangePassword() {
      alert("change password form submitted!");
    }
  },

  data: () => ({
    show1: false,
    show2: false,
    show3: false,
    username: "",
    email: "",
    password: "",
    newPassword: "",
    confirmNewPassword: "",
    emailRules: [
      v => !!v || "E-mail is required",
      v => /.+@.+\..+/.test(v) || "E-mail must be valid"
    ],
    passwordRules: [
      v => {
        const pattern = /[\s]+/;
        return !pattern.test(v) || "Your password can't contain whitespaces";
      },
      v =>
          (v || "").length >= 6 ||
          "Your password has to be at least 6 characters long",
      v => {
        const pattern = /[a-zA-Z]+/;
        return (
            pattern.test(v) || "Your password has to have at least one letter"
        );
      },
      v => {
        const pattern = /[0-9]+/;
        return (
            pattern.test(v) || "Your password has to have at least one number"
        );
      },
      v => {
        const pattern = /[\W]+/;
        return (
            pattern.test(v) ||
            "Your password has to have at least one special character"
        );
      }
    ]
  })
};
</script>
