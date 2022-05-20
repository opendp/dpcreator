<template>
  <v-container>
    <v-row>
      <v-col offset-sm="1" sm="10" md="12" offset-md="0">
        <h2 class="title-size-1 text-center mb-10">{{ $t('more information.title') }}</h2>
        <LinearBox
            :class="{
            'mb-6': $vuetify.breakpoint.xsOnly,
            'mb-12': $vuetify.breakpoint.smAndUp
          }"
        >
          <template v-slot:content>

            <h2 id="more-info-dp" class="title-size-1" v-html="$t('more information.differential privacy title')"></h2>
            <p class="grey--text text--darken-2" v-html="$t('more information.differential privacy text')"></p>
          </template>
        </LinearBox>

        <!-- Registered Dataverses -->
        <LinearBox
            :class="{
            'mb-6': $vuetify.breakpoint.xsOnly,
            'mb-12': $vuetify.breakpoint.smAndUp
          }"
        >
          <template v-slot:content>
            <h2 class="title-size-1" id="more-info-dataverses" v-html="$t('more information.registered dataverses title')"></h2>
            <p class="grey--text text--darken-2" v-html="$t('more information.registered dataverses text')"></p>

            <!-- List the currently registered Dataverses -->
            <div v-if="registeredDvs && registeredDvs.length > 0">
              <hr/>
              <br/>
              <p>
                Dataverses currently registered:
              </p>

              <ul>
                <li v-for="item in registeredDvs">
                  <a :href="item.dataverseUrl" target="_blank">{{ item.name }}</a>
                </li>
              </ul>
            </div>

          </template>
        </LinearBox>

        <!-- Privacy Budget and Epsilon -->
        <LinearBox
            :class="{
            'mb-6': $vuetify.breakpoint.xsOnly,
            'mb-12': $vuetify.breakpoint.smAndUp
          }"
        >
          <template v-slot:content>
            <h2 id="more-info-epsilon" class="title-size-1" v-html="$t('more information.epsilon title')"></h2>
            <p class="grey--text text--darken-2" v-html="$t('more information.epsilon text')"></p>
          </template>
        </LinearBox>
        <!-- Delta -->
        <LinearBox
            :class="{
            'mb-6': $vuetify.breakpoint.xsOnly,
            'mb-12': $vuetify.breakpoint.smAndUp
          }"
        >
          <template v-slot:content>
            <h2 class="title-size-1" id="more-info-delta" v-html="$t('more information.delta title')"></h2>
            <p class="grey--text text--darken-2" v-html="$t('more information.delta text')"></p>
          </template>
        </LinearBox>
        <!-- Inferred Types -->
        <LinearBox
            :class="{
            'mb-6': $vuetify.breakpoint.xsOnly,
            'mb-12': $vuetify.breakpoint.smAndUp
          }"
        >
          <template v-slot:content>
            <h2 class="title-size-1" id="more-info-inferred-types" v-html="$t('more information.inferred-types title')"></h2>
            <p class="grey--text text--darken-2" v-html="$t('more information.inferred-types text')"></p>
          </template>
        </LinearBox>
        <!--
        <LinearBox

            :class="{
            'mb-6': $vuetify.breakpoint.xsOnly,
            'mb-12': $vuetify.breakpoint.smAndUp
          }"
        >
          <template v-slot:content>
            <h2 class="title-size-1" id="more-info-confidence">{{ $t('more information.confidence title') }}</h2>
            <p class="grey--text text--darken-2" v-html="$t('more information.confidence text')"></p>
          </template>
        </LinearBox>
-->
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
  name: "ExplanatoryText",
  props: ["registeredDvs"]
};
</script>
