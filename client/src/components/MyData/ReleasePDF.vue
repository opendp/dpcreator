<template>
  <div>
    <h3>Release Component</h3>
    <div id="pdf-view"></div>
    <button @click="handleClick">show pdf</button>
  </div>
</template>

<script>


export default {
  name: 'ReleasePDF',
  props: ['pdfUrl'],
  data: () => ({
    pdfAPIReady: false,
    adobeDCView: null,
    pdfSelected: false,
    ADOBE_KEY: '13c79907c6144590b17e8ef044324444',
  }),
  computed: {},
  methods: {
    handleClick() {

      this.adobeDCView = new AdobeDC.View({
        clientId: this.ADOBE_KEY,
        divId: "pdf-view"
      });
      this.adobeDCView.previewFile(
          {
            content: {location: {url: "https://documentcloud.adobe.com/view-sdk-demo/PDFs/Bodea Brochure.pdf"}},
            metaData: {fileName: "Bodea Brochure.pdf"}
          });
    }
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

