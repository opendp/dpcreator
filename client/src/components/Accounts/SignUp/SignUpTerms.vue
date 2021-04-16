<template>
  <div>
    <h2
        class="title-size-2 mb-10"
        :class="{ 'ml-5': $vuetify.breakpoint.xsOnly }"
    >
      <strong>1/2. </strong>Check and accept Terms of Use:
    </h2>
    <ShadowBoxWithScroll>
      <template v-slot:title>
        Terms for depositing a DP release back to Dataverse
      </template>
      <template v-slot:scrollable-area>
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
      </template>
      <template v-slot:actions>
        <Checkbox
            :value.sync="confirmTerms1"
            text="I have read and agree to the Terms of Service."
        />
      </template>
    </ShadowBoxWithScroll>

    <ShadowBoxWithScroll>
      <template v-slot:title>
        Terms for depositing a DP release back to Dataverse
      </template>
      <template v-slot:scrollable-area>
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
      </template>
      <template v-slot:actions>
        <Checkbox
            :value.sync="confirmTerms2"
            text="I have read and agree to the Terms of Service."
        />
      </template>
    </ShadowBoxWithScroll>
    <Button
        :disabled="!confirmTerms1 || !confirmTerms2"
        classes="mt-6"
        :class="{
        'width80 mx-auto d-block': $vuetify.breakpoint.xsOnly,
        'mr-2': $vuetify.breakpoint.smAndUp
      }"
        color="primary"
        :click="handleContinue"
        label="Continue"
    />
    <Button
        color="primary"
        classes="mt-6"
        :class="{ 'width80 mx-auto d-block': $vuetify.breakpoint.xsOnly }"
        outlined
        :click="() => $router.push(NETWORK_CONSTANTS.HOME.PATH)"
        label="Cancel"
    />
  </div>
</template>

<style lang="scss">
.v-stepper__content {
  @media (max-width: 600px) {
    padding: 0 !important;
  }
}
</style>

<script>
import ShadowBoxWithScroll from "../../DesignSystem/Boxes/ShadowBoxWithScroll.vue";
import Button from "../../DesignSystem/Button.vue";
import Checkbox from "../../DesignSystem/Checkbox.vue";
import NETWORK_CONSTANTS from "../../../router/NETWORK_CONSTANTS";

export default {
  components: {ShadowBoxWithScroll, Checkbox, Button},
  name: "SignUpTerms",
  props: ["signUpStep"],
  data: () => ({
    confirmTerms1: false,
    confirmTerms2: false,
    NETWORK_CONSTANTS
  }),
  methods: {
    handleContinue: function () {
      window.scrollTo(0, 0);
      this.$emit("update:signUpStep", this.signUpStep + 1);
    }
  }
};
</script>
