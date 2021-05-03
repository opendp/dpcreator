<template>
  <div class="home">
    <EventSuccessAlert text="Done! You are out." queryParam="logout"/>
    <BadRequestAlert
        :show-alert=showAlert
        :alert-text=alertText
    />
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
import BadRequestAlert from "@/components/Home/BadRequestAlert";

export default {
  name: "Home",
  components: {
    BadRequestAlert,
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
    } else {
      this.showAlert = true
      this.alertText = 'To create a DP Release, please make a request from an registered Dataverse installation.'
    }
  },
  data: () => ({
    showAlert: false,
    alertText: 'here is some text',
  })
};
</script>
