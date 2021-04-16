<template>
  <section class="py-11 mt-16 soft_secondary">
    <v-container
        :class="{
        'px-0': $vuetify.breakpoint.xsOnly
      }"
    >
      <v-row>
        <v-col>
          <h2 class="title-size-2 font-weight-bold mb-5">
            Do you need support?
          </h2>
          <p>
            Contact us at
            <a
                class="font-weight-bold text-decoration-none"
                href="mailto:support@opendp.com"
            >support@opendp.com</a
            >
          </p>
        </v-col>
      </v-row>
    </v-container>
  </section>
</template>

<script>
export default {
  name: "SupportBanner"
};
</script>
