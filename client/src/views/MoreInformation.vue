<template>
  <ExplanatoryText/>
</template>

<script>
import ExplanatoryText from "../components/MoreInformation/ExplanatoryText.vue";

export default {
  name: "MoreInformation",
  components: {
    ExplanatoryText
  },

  data: () => ({
    showAlert: false,
    alertText: 'here is some text',
  })
};
</script>
