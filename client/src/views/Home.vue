<template>
  <div class="home">
    <EventSuccessAlert text="Done! You are out." queryParam="logout"/>
    <StepsGrid/>
    <TermsOfService/>
    <AccountButtons/>
    <AccountButtonsWaypointActivator/>
    <AboutOpenDPBanner/>
  </div>
</template>

<script>
import AboutOpenDPBanner from "../components/Home/AboutOpenDPBanner.vue";
import AccountButtons from "../components/Home/AccountButtons.vue";
import AccountButtonsWaypointActivator from "../components/Home/AccountButtonsWaypointActivator.vue";
import EventSuccessAlert from "../components/Home/EventSuccessAlert.vue";
import StepsGrid from "../components/Home/StepsGrid.vue";
import TermsOfService from "../components/Home/TermsOfService.vue";

export default {
  name: "Home",
  components: {
    AccountButtons,
    AboutOpenDPBanner,
    EventSuccessAlert,
    TermsOfService,
    StepsGrid,
    AccountButtonsWaypointActivator
  },
  created() {
    const handoffId = this.$route.query.id

    if (handoffId) {
      this.$store.dispatch('dataverse/setHandoffId', handoffId)

    }
  }
};
</script>
