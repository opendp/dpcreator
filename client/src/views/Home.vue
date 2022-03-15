<template>
  <div class="home">
    pdfAPIReady: {{ pdfAPIReady }}
    <div id="adobe-dc-view" style="height: 360px; width: 500px;"></div>


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
    /*
  document.addEventListener("adobe_dc_view_sdk.ready", () => { this.pdfAPIReady = true; });
	//credit: https://community.adobe.com/t5/document-services-apis/adobe-dc-view-sdk-ready/m-p/11648022#M948
	if(window.AdobeDC) {
	  console.log('READY!')
	  this.pdfAPIReady = true;
  }
*/
    document.addEventListener("adobe_dc_view_sdk.ready", () => {
      console.log('adobe ready')
      var adobeDCView = new AdobeDC.View({clientId: this.ADOBE_KEY, divId: "adobe-dc-view"});
      adobeDCView.previewFile({
            content: {
              location:
                  {url: "https://documentcloud.adobe.com/view-sdk-demo/PDFs/Bodea%20Brochure.pdf"}
            },
            metaData: {fileName: "Bodea Brochure.pdf"}
          },
          {
            embedMode: "SIZED_CONTAINER"
          });
    });
    const handoffId = this.$route.query.id

    if (handoffId) {
      this.$store.dispatch('dataverse/setHandoffId', handoffId)
    } else {
      console.log('no handoffId')
    }
  },
  watch: {
    pdfAPIReady(val) {
      // should only be called when true, but be sure
      if (val) {
        console.log('WATCH READY!')
        this.adobeDCView = new AdobeDC.View({
          clientId: this.ADOBE_KEY,
          divId: "pdf-view"
        });
      }
    },
    showFile() {
      this.adobeDCView.previewFile({
        content: {
          location: {url: "https://documentcloud.adobe.com/view-sdk-demo/PDFs/Bodea Brochure.pdf"}
        },
        metaData: {fileName: "Bodea Brochure.pdf"}
      });
    }
  },
  data: () => ({
    ADOBE_KEY: '13c79907c6144590b17e8ef044324444',
    pdfAPIReady: false,
    adobeDCView: null,
    pdfSelected: false,
    showAlert: false,
    alertText: 'here is some text',
  })
};

</script>
