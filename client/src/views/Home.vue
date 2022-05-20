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
    const unregistered_dv_url = this.$route.query.unreg_dv_url
    if (handoffId) {
      this.$store.dispatch('dataverse/setHandoffId', handoffId)
    } else if (error) {
      this.showAlert = true
      if (unregistered_dv_url) {
        this.alertText = "Sorry! This Dataverse was not recognized: <br /><br /><b>" + unregistered_dv_url + "</b>"
         + "<br /><br />Please contact the <a href='mailto:info@opendp.org?subject=Unregistered Dataverse: " + unregistered_dv_url + "'>administrator</a>."
      }else{
        this.alertText = "Sorry! There was a problem with the Dataverse information."
        + "<br /><br />Please contact the <a href='mailto:info@opendp.org?subject=Dataverse handoff error: " + error + "'>administrator</a>.  (error code: " + error + "). "
      }
    }
  },

  data: () => ({
    showAlert: false,
    alertText: '',
  })
};

</script>
