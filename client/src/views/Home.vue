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
    const error = this.$route.query.error_code
    if (handoffId) {
      this.$store.dispatch('dataverse/setHandoffId', handoffId)
    } else if (error) {
      this.showAlert = true
      this.alertText = "Error handing off from Dataverse, error code = " + error

    }
  },

  data: () => ({
    showAlert: false,
    alertText: '',
  })
};

</script>
