<template>
<div id="app"><FormWizard @on-complete="onComplete">
    <TabContent title="Personal details"
                 icon="ti-user">
      My first tab content
    </TabContent>
    <TabContent title="Additional Info"
                 icon="ti-settings">
      My second tab content
    </TabContent>
    <TabContent title="Last step"
                 icon="ti-check">
      Yuhuuu! This seems pretty damn simple
    </TabContent>
  </FormWizard>
</div>
</template>
<script>
import {FormWizard, TabContent} from 'vue-form-wizard'
import {VueFormGenerator} from 'vue-form-generator'
import 'vue-form-wizard/dist/vue-form-wizard.min.css'
export default {
  name: 'app',
  components: {
    FormWizard,
    TabContent
    },
  methods: {
    onComplete: function(){
      alert('Yay. Done!');
    }
  }
}
</script>

<style>

</style>
