<template>
  <section class="light-blue-bg">
    <v-container
        class="py-16"
        :class="{ 'px-11': $vuetify.breakpoint.smAndDown }"
    >
      <v-row>
        <v-col offset-md="1" class="d-flex align-center" id="img-wrapper">
          <v-img
              max-height="60%"
              max-width="30%"
              min-width="250px"
              src="../../assets/OpenDPLogo.png"
              class="hidden-sm-and-down"
          ></v-img>
          <v-img
              max-width="60%"
              src="../../assets/OpenDPLogo.png"
              class="hidden-md-and-up mb-5"
          ></v-img>
        </v-col>
        <v-col offset-md="1" cols="12" md="4" id="text-wrapper">
          <h2 class="title-size-1">This is a sentence about Open DP</h2>
          <p>
            Lorem ipsum dolor sit amet consectetur adipisicing elit. Modi in
            veniam explicabo porro autem voluptas, aperiam perferendis soluta
            velit laborum voluptates similique repellendus, natus tempora, quia
            saepe.
          </p>
          <v-btn color="primary" class="my-5">Learn More</v-btn>
        </v-col>
      </v-row>
    </v-container>
  </section>
</template>

<style lang="scss" scoped>
#img-wrapper {
  @media screen and (min-width: 960px) {
    order: 2;
  }
}

#text-wrapper {
  @media screen and (min-width: 960px) {
    order: 1;
  }
}
</style>

<script>
export default {
  name: "AboutOpenDPBanner"
};
</script>
