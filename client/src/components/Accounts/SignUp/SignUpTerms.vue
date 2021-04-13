<template>
  <div>
    <h2 class="title-size-2 mb-10">
      <strong>1/2. </strong>Check and accept Terms of Use
    </h2>
    <v-card class="mb-5 rounded-lg terms-card" elevation="2">
      <v-card-title
      >Terms for depositing a DP release back to Dataverse
      </v-card-title
      >
      <v-card-text>
        <p>
          Lorem ipsum dolor sit amet consectetur adipisicing elit. Autem tempora
          reiciendis eum asperiores, doloribus totam excepturi quaerat eligendi
          porro nemo inventore, ducimus qui dicta nostrum deleniti maxime,
          quisquam soluta voluptatum. Lorem ipsum dolor sit amet consectetur
          adipisicing elit. Necessitatibus magni at aut sed dignissimos velit
          dolor beatae cumque assumenda quisquam pariatur quidem ullam, incidunt
          eligendi voluptatem deleniti iste! Veritatis, voluptate!
        </p>
        <p>
          Lorem ipsum dolor sit amet consectetur adipisicing elit. Autem tempora
          reiciendis eum asperiores, doloribus totam excepturi quaerat eligendi
          porro nemo inventore, ducimus qui dicta nostrum deleniti maxime,
          quisquam soluta voluptatum. Lorem ipsum dolor sit amet consectetur
          adipisicing elit. Necessitatibus magni at aut sed dignissimos velit
          dolor beatae cumque assumenda quisquam pariatur quidem ullam, incidunt
          eligendi voluptatem deleniti iste! Veritatis, voluptate!
        </p>
        <p>
          Lorem ipsum dolor sit amet consectetur adipisicing elit. Autem tempora
          reiciendis eum asperiores, doloribus totam excepturi quaerat eligendi
          porro nemo inventore, ducimus qui dicta nostrum deleniti maxime,
          quisquam soluta voluptatum. Lorem ipsum dolor sit amet consectetur
          adipisicing elit. Necessitatibus magni at aut sed dignissimos velit
          dolor beatae cumque assumenda quisquam pariatur quidem ullam, incidunt
          eligendi voluptatem deleniti iste! Veritatis, voluptate!
        </p>
        <p>
          Lorem ipsum dolor sit amet consectetur adipisicing elit. Autem tempora
          reiciendis eum asperiores, doloribus totam excepturi quaerat eligendi
          porro nemo inventore, ducimus qui dicta nostrum deleniti maxime,
          quisquam soluta voluptatum. Lorem ipsum dolor sit amet consectetur
          adipisicing elit. Necessitatibus magni at aut sed dignissimos velit
          dolor beatae cumque assumenda quisquam pariatur quidem ullam, incidunt
          eligendi voluptatem deleniti iste! Veritatis, voluptate!
        </p>
      </v-card-text>
      <v-card-actions>
        <v-checkbox v-model="confirmTerms1"
        >
          <template v-slot:label
          >
            <div class="primary--text">
              I have read and agree to the Terms of Service.
            </div>
          </template
          >
        </v-checkbox
        >
      </v-card-actions>
    </v-card>

    <v-card class="mb-5 rounded-lg terms-card" elevation="2">
      <v-card-title
      >Terms for depositing a DP release back to Dataverse
      </v-card-title
      >
      <v-card-text>
        <p>
          Lorem ipsum dolor sit amet consectetur adipisicing elit. Autem tempora
          reiciendis eum asperiores, doloribus totam excepturi quaerat eligendi
          porro nemo inventore, ducimus qui dicta nostrum deleniti maxime,
          quisquam soluta voluptatum. Lorem ipsum dolor sit amet consectetur
          adipisicing elit. Necessitatibus magni at aut sed dignissimos velit
          dolor beatae cumque assumenda quisquam pariatur quidem ullam, incidunt
          eligendi voluptatem deleniti iste! Veritatis, voluptate!
        </p>
        <p>
          Lorem ipsum dolor sit amet consectetur adipisicing elit. Autem tempora
          reiciendis eum asperiores, doloribus totam excepturi quaerat eligendi
          porro nemo inventore, ducimus qui dicta nostrum deleniti maxime,
          quisquam soluta voluptatum. Lorem ipsum dolor sit amet consectetur
          adipisicing elit. Necessitatibus magni at aut sed dignissimos velit
          dolor beatae cumque assumenda quisquam pariatur quidem ullam, incidunt
          eligendi voluptatem deleniti iste! Veritatis, voluptate!
        </p>
        <p>
          Lorem ipsum dolor sit amet consectetur adipisicing elit. Autem tempora
          reiciendis eum asperiores, doloribus totam excepturi quaerat eligendi
          porro nemo inventore, ducimus qui dicta nostrum deleniti maxime,
          quisquam soluta voluptatum. Lorem ipsum dolor sit amet consectetur
          adipisicing elit. Necessitatibus magni at aut sed dignissimos velit
          dolor beatae cumque assumenda quisquam pariatur quidem ullam, incidunt
          eligendi voluptatem deleniti iste! Veritatis, voluptate!
        </p>
        <p>
          Lorem ipsum dolor sit amet consectetur adipisicing elit. Autem tempora
          reiciendis eum asperiores, doloribus totam excepturi quaerat eligendi
          porro nemo inventore, ducimus qui dicta nostrum deleniti maxime,
          quisquam soluta voluptatum. Lorem ipsum dolor sit amet consectetur
          adipisicing elit. Necessitatibus magni at aut sed dignissimos velit
          dolor beatae cumque assumenda quisquam pariatur quidem ullam, incidunt
          eligendi voluptatem deleniti iste! Veritatis, voluptate!
        </p>
      </v-card-text>
      <v-card-actions>
        <v-checkbox v-model="confirmTerms2"
        >
          <template v-slot:label
          >
            <div class="primary--text">
              I have read and agree to the Terms of Service.
            </div>
          </template
          >
        </v-checkbox
        >
      </v-card-actions>
    </v-card>
    <v-btn
        :disabled="!confirmTerms1 || !confirmTerms2"
        class="mr-4 mt-6"
        color="primary"
        @click="$emit('update:signUpStep', signUpStep + 1)"
    >Continue
    </v-btn
    >
    <v-btn color="primary" class="mt-6" outlined @click="$router.push('/')"
    >Cancel
    </v-btn
    >
  </div>
</template>

<style lang="scss" scoped>
.terms-card {
  border: 1px solid #c2c2c2;
  box-shadow: 2px 2px 6px 0 rgba(0, 0, 0, 0.2);
}

.v-card__actions {
  padding-left: 16px;
}
</style>

<script>
export default {
  name: "SignUpTerms",
  props: ["signUpStep"],
  data: () => ({
    confirmTerms1: false,
    confirmTerms2: false
  })
};
</script>
