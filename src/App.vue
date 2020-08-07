<template>
<div id="app"><FormWizard @on-complete="onComplete">
    <TabContent title="Personal details" icon="ti-user">
      <!-- :before-change="validateFirstTab" -->
      <!-- > -->
      <!-- <VueFormGenerator :model="model"  -->
      <!--                   :schema="firstTabSchema" -->
      <!--                   :options="formOptions" -->
      <!--                   ref="firstTabForm" -->
      <!--                   > -->
        <!-- </VueFormGenerator> -->
      What is your name?
    </TabContent>
    <TabContent title="Additional Info"
                icon="ti-settings">
      <!-- :before-change="validateSecondTab" -->
      <!-- > -->
      <!-- <VueFormGenerator :model="model"  -->
      <!--                   :schema="secondTabSchema" -->
      <!--                   :options="formOptions" -->
      <!--                   ref="secondTabForm" -->
      <!--                   >                   -->
        <!-- </VueFormGenerator> -->
      Where did you go to high school?
    </TabContent>
    <TabContent title="Last step"
                icon="ti-check">
      <!-- <h4>Your json is ready!</h4> -->
      <!-- <div class="panel-body"> -->
	<!--   <pre v-if="model" v-html="prettyJSON(model)"></pre> -->
        <!-- </div> -->
      This seems pretty simple
    </TabContent>
  </FormWizard>
</div>
</template>
<script>
import {FormWizard, TabContent} from 'vue-form-wizard'
//import {VueFormGenerator} from "vue-form-generator"
import 'vue-form-wizard/dist/vue-form-wizard.min.css'
export default {
  name: 'app',
  components: {
    FormWizard,
    TabContent,
//    VueFormGenerator
  },
  methods: {
    onComplete: function(){
      alert('Yay. Done!');
    },
    validateFirstTab: function(){
      return this.$refs.firstTabForm.validate();
    },
    validateSecondTab: function(){
      return this.$refs.secondTabForm.validate();
    },
  },
  prettyJSON: function(json) {
    if (json) {
      json = JSON.stringify(json, undefined, 4);
      json = json.replace(/&/g, '&').replace(/</g, '<').replace(/>/g, '>');
      return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+-]?\d+)?)/g, function(match) {
        var cls = 'number';
        if (/^"/.test(match)) {
          if (/:$/.test(match)) {
            cls = 'key';
          } else {
            cls = 'string';
          }
        } else if (/true|false/.test(match)) {
          cls = 'boolean';
        } else if (/null/.test(match)) {
          cls = 'null';
        }
        return '<span class="' + cls + '">' + match + '</span>';
      });
    }
  },
  data: function() {
    return{
      model: {
        firstName:'',
        lastName:'',
        email:'',
        streetName:'',
        streetNumber:'',
        city:'',
        country:''
      },
      formOptions: {
        validationErrorClass: "has-error",
        validationSuccessClass: "has-success",
        validateAfterChanged: true
      },
      firstTabSchema: {
        fields:[{
          type: "input",
          inputType: "text",
          label: "First name",
          model: "firstName",
          required:true,
//          validator:VueFormGenerator.validators.string,
          styleClasses:'col-xs-6'
        },
                {
                  type: "input",
                  inputType: "text",
                  label: "Last name",
                  model: "lastName",
                  required:true,
//                  validator:VueFormGenerator.validators.string,
                  styleClasses:'col-xs-6'
                },
                {
                  type: "input",
                  inputType: "text",
                  label: "Email",
                  model: "email",
                  required:true,
//                  validator:VueFormGenerator.validators.email,
                  styleClasses:'col-xs-12'
                }
               ]
      },
      secondTabSchema: {
        fields:[
          {
            type: "input",
            inputType: "text",
            label: "Street name",
            model: "streetName",
            required:true,
//            validator:VueFormGenerator.validators.string,
            styleClasses:'col-xs-9'
          },
          {
            type: "input",
            inputType: "text",
            label: "Street number",
            model: "streetNumber",
            required:true,
//            validator:VueFormGenerator.validators.string,
            styleClasses:'col-xs-3'
          },
          {
            type: "input",
            inputType: "text",
            label: "City",
            model: "city",
            required:true,
//            validator:VueFormGenerator.validators.string,
            styleClasses:'col-xs-6'
          },
          {
            type: "select",
            label: "Country",
            model: "country",
            required:true,
//            validator:VueFormGenerator.validators.string,
            values:['United Kingdom','Romania','Germany'],
            styleClasses:'col-xs-6'
          },
        ]
      }
    }
  },
}
</script>

<style>
pre {
    overflow: auto;
}
pre .string { color: #885800; }
pre .number { color: blue; }
pre .boolean { color: magenta; }
pre .null { color: red; }
pre .key { color: green; }
</style>
