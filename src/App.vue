<template>
<div id="app">
<div id="navigation">
    <Sidebar>
      <ul class="sidebar-panel-nav">
	<li>Introduction</li>
	<ul class="sidebar-panel-subnav">
          <li><a href="#background">Background</a></li>
	</ul>
	<li>Import Data</li>
	<ul class="sidebar-panel-subnav">
          <li><a href="#upload-dataset">Upload dataset</a></li>
          <li><a href="#confirm-dataset">Confirm dataset</a></li>
          <li><a href="#select-dataset-type">Select dataset type</a></li>
          <li><a href="#confirm-dataset-contents">Confirm contents of dataset</a></li>
          <li><a href="#specify-dataset-info">Specify dataset information</a></li>                </ul>
	<li>Specify Metadata</li>
	<ul class="sidebar-panel-subnav">
          <li><a href="#create-custom-vars">Create custom variables</a></li>
          <li><a href="#confirm-var-types">Confirm variable types</a></li>
          <li><a href="#set-var-ranges">Set variable ranges</a></li>
          <li><a href="#confirm-vars-of-interest">Confirm variables of interest</a></li>
	</ul>
	<li>Set Parameters</li>
	<ul class="sidebar-panel-subnav">
          <li><a href="#set-priv-loss-params">Set privacy loss parameters</a></li>
	</ul>
	<li>Create Statistics</li>
	<ul class="sidebar-panel-subnav">
          <li><a href="#create-stats">Create statistics</a></li>
	</ul>
	<li>Generate Report</li>
	<ul class="sidebar-panel-subnav">
          <li><a href="#confirm-err-and-submit">Confirm error and submit</a></li>
          <li><a href="#view-report">View report</a></li>
	</ul>
      </ul>
    </Sidebar>
</div>
<div id="canvas">
  <FormWizard @on-complete="onComplete" title="OpenDP" subtitle="form screens">
    <TabContent title="Welcome" icon="ti-user">
      screen-welcome-accept
    </TabContent>
    <TabContent title="Data"
                icon="ti-settings">
      screen-data-choose
    </TabContent>
    <TabContent title="Confirm Data"
                icon="ti-settings">
      screen-data-confirm
    </TabContent>
    <TabContent title="Classify Data Privacy"
                icon="ti-settings">
      screen-data-privacy-classification
    </TabContent>
    <TabContent title="Data Sample Details"
                icon="ti-settings">
      screen-data-sample-population-details
    </TabContent>
    <TabContent title="Create Custom Variables"
                icon="ti-settings">
      screen-data-custom-variables-create
    </TabContent>
    <TabContent title="Confirm Custom Variables"
                icon="ti-settings">
      screen-data-custom-variables-confirm
    </TabContent>
    <TabContent title="Provide Variable Bounds"
                icon="ti-settings">
      screen-data-custom-variables-bounds
    </TabContent>
    <TabContent title="Provide Variable Categories"
                icon="ti-settings">
      screen-data-variables-categories
    </TabContent>
    <TabContent title="Provide Variable Visibilities"
                icon="ti-settings">
      screen-data-variables-visibility
    </TabContent>
    <TabContent title="Provide Privacy Loss Parameters"
                icon="ti-settings">
      screen-data-privacy-loss-parameters
    </TabContent>
    <TabContent title="Create Statistics"
                icon="ti-settings">
      screen-data-create-statistic-list
      screen-data-create-statistic-add
      screen-data-create-statistic-edit
    </TabContent>
    <TabContent title="Review Selections"
                icon="ti-settings">
      screen-submit-accept
    </TabContent>
    <TabContent title="View Report"
                icon="ti-check">
      screen-report-view
    </TabContent>
  </FormWizard>
  </div>
</div>
</template>
<script>
import {FormWizard, TabContent} from 'vue-form-wizard'
//import {VueFormGenerator} from "vue-form-generator"
import 'vue-form-wizard/dist/vue-form-wizard.min.css'
import Sidebar from './components/Menu/Sidebar.vue';
export default {
  name: 'app',
  components: {
    FormWizard,
    TabContent,
    Sidebar
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
          styleClasses:'col-xs-6'
        },
                {
                  type: "input",
                  inputType: "text",
                  label: "Last name",
                  model: "lastName",
                  required:true,
                  styleClasses:'col-xs-6'
                },
                {
                  type: "input",
                  inputType: "text",
                  label: "Email",
                  model: "email",
                  required:true,
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
            styleClasses:'col-xs-9'
          },
          {
            type: "input",
            inputType: "text",
            label: "Street number",
            model: "streetNumber",
            required:true,
            styleClasses:'col-xs-3'
          },
          {
            type: "input",
            inputType: "text",
            label: "City",
            model: "city",
            required:true,
            styleClasses:'col-xs-6'
          },
          {
            type: "select",
            label: "Country",
            model: "country",
            required:true,
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
  @import url('https://fonts.googleapis.com/css2?family=Roboto&display=swap');
html {
    height: 100%;
    overflow:hidden;
}
body {
    border: 0; margin: 0; padding: 0;
    color: black;
    text-decoration: none;
    font-family: 'Roboto', sans-serif;
    font-size: 1.5rem;
    font-weight: bold;
    Display: block;
    padding-bottom: 0.5em;
    height: 100%;
    background: rgba(255,255,255,0.5);
    float: right;
    width: 60%
}
ul.sidebar-panel-nav {
    list-style-type: none;
}
ul.sidebar-panel-nav > li {
    color: rgba(8,8,8,0.5);
    text-decoration: none;
    font-family: 'Roboto', sans-serif;
    font-size: 1.5rem;
    font-weight: bold;
    Display: block;
    padding-bottom: 0.5em;
}
ul.sidebar-panel-subnav {
    list-style-type: none;
}
ul.sidebar-panel-subnav > li > a {
    color: rgba(86,86,86,0.5);
    text-decoration: none;
    font-family: 'Roboto', sans-serif;
    font-size: 1.5rem;
    display: block;
    padding-bottom: 0.5em;
}
button, input[type=button] {
    background: blue;
    color: white;
}

</style>
