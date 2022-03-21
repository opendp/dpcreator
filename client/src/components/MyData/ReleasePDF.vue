<template>
  <div>
    <div id="pdf-view" :style=style></div>
    <Button v-if="!viewResults" :click="() => handleView()">View Results</Button>
  </div>
</template>

<script>


import {mapState} from "vuex";
import Button from "../../components/DesignSystem/Button.vue";

export default {
  name: 'ReleasePDF',
  components: {Button},
  props: ['pdfUrl'],
  data: () => ({
    pdfAPIReady: false,
    adobeDCView: null,
    viewResults: false,
    // ADOBE_KEY: '34a0c926740d4ddb9758dbc6da2a4f39', // dev.dpcreator.org
    ADOBE_KEY: '44937032e26b4033a840626ed0cd8e79', // demo.dpcreator.org
    // ADOBE_KEY: '13c79907c6144590b17e8ef044324444', // localhost
  }),
  computed: {
    ...mapState('dataset', ['analysisPlan']),
    style() {
      if (this.viewResults) {
        return "height: 1200px; width: 1000px;"
      } else {
        return ""
      }
    }
  },
  methods: {
    handleView() {
      console.log('handle view')
      this.adobeDCView = new AdobeDC.View({
        clientId: this.ADOBE_KEY,
        divId: "pdf-view"
      });
      this.adobeDCView.previewFile(
          {
            content: {location: {url: this.analysisPlan.releaseInfo.downloadPdfUrl}},
            metaData: {fileName: "DP Creator Release"}
          }, {embedMode: "SIZED_CONTAINER"});
      this.viewResults = true
    },
    handleHide() {
      this.viewResults = false
    }
  },

  /*

	document.addEventListener("adobe_dc_view_sdk.ready", function(){
		var adobeDCView = new AdobeDC.View({clientId: "<YOUR_CLIENT_ID>", divId: "adobe-dc-view"});
		adobeDCView.previewFile({
			content:{location: {url: "https://documentcloud.adobe.com/view-sdk-demo/PDFs/Bodea Brochure.pdf"}},
			metaData:{fileName: "Bodea Brochure.pdf"}
		}, {embedMode: "IN_LINE"});
	});

   */
  created() {
    console.log("releasePDF created")
  },
  mounted() {
    document.addEventListener("adobe_dc_view_sdk.ready", () => {
      console.log(' ReleasePDF eventhandler triggered');
      this.pdfAPIReady = true;
    });
  },
  watch: {
    pdfAPIReady(val) {
      console.log('in watch')
      // should only be called when true, but be sure
      if (val) {
        console.log('creating view')
        this.adobeDCView = new AdobeDC.View({
          clientId: this.ADOBE_KEY,
          divId: "pdf-view"
        });
      }
    }
  },

}
</script>

