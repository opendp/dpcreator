<template>
  <ExplanatoryText :registered-dvs="registeredDvs"/>
</template>

<script>
import ExplanatoryText from "../components/MoreInformation/ExplanatoryText.vue";
import dataverse from "@/api/dataverse";
export default {
  name: "MoreInformation",
  components: {
    ExplanatoryText
  },
  created() {
    dataverse.getRegisteredDataverses().then((data) => {
      this.registeredDvs = data.data.data.dataverses
    })
  },
  data: () => ({
    registeredDvs: null
  })
};
</script>
