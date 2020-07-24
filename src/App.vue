<template>
  <div id="app">
    <nav class="main-nav">
      <div class="logo">my.company</div>
      <Burger></Burger>
    </nav>
    <Sidebar><ul class="sidebar-panel-nav">
        <li><a href="#intro">Introduction</a></li>
        <ul class="sidebar-panel-subnav">
        <li><a href="#background">Background</a></li>
        </ul>
        <li><a href="#import-data">Import Data</a></li>
        <ul class="sidebar-panel-subnav">
          <li><a href="#upload-dataset">Upload dataset</a></li>
          <li><a href="#confirm-dataset">Confirm dataset</a></li>
          <li><a href="#select-dataset-type">Select dataset type</a></li>
          <li><a href="#confirm-dataset-contents">Confirm contents of dataset</a></li>
          <li><a href="#specify-dataset-info">Specify dataset information</a></li>                </ul>
        <li><a href="#specify-metadata">Specify Metadata</a></li>
        <ul class="sidebar-panel-subnav">
          <li><a href="#create-custom-vars">Create custom variables</a></li>
          <li><a href="#confirm-var-types">Confirm variable types</a></li>
          <li><a href="#set-var-ranges">Set variable ranges</a></li>
          <li><a href="#confirm-vars-of-interest">Confirm variables of interest</a></li>
        </ul>
        <li><a href="#set-params">Set Parameters</a></li>
        <ul class="sidebar-panel-subnav">
          <li><a href="#set-priv-loss-params">Set privacy loss parameters</a></li>
        </ul>
        <li><a href="#create-stats">Create Statistics</a></li>
        <ul class="sidebar-panel-subnav">
          <li><a href="#create-stats0">Create statistics</a></li>
        </ul>
        <li><a href="#generate-report">Generate Report</a></li>
        <ul class="sidebar-panel-subnav">
          <li><a href="#confirm-err-and-submit">Confirm error and submit</a></li>
          <li><a href="#view-report">View report</a></li>
        </ul>
      </ul>
    </Sidebar>
  </div>
</template>
<script>
  import Burger from './components/Menu/Burger.vue';
  import Sidebar from './components/Menu/Sidebar.vue';

  export default {
  name: 'app',
  components: {
  Burger, Sidebar
  }
  }
</script>

<style>
html {
   height: 100%;
   overflow:hidden;
 }

 body {
   border: 0; margin: 0; padding: 0;
   font-family: 'Lato';
   height: 100%;
   background: rgb(101,31,87);
   background: linear-gradient(45deg, rgba(101,31,87,1) 0%, rgba(225,113,87,1) 48%, rgba(249,248,113,1) 100%);
 }

 .logo {
   align-self: center;
   color: #fff;
   font-weight: bold;
   font-family: 'Lato'
 }

 .main-nav {
   display: flex;
   justify-content: space-between;
   padding: 0.5rem 0.8rem;
 }

 ul.sidebar-panel-nav {
   list-style-type: none;
 }

 ul.sidebar-panel-nav > li > a {
   color: #fff;
   text-decoration: none;
   font-size: 1.5rem;
   display: block;
   padding-bottom: 0.5em;
}

 ul.sidebar-panel-subnav {
   list-style-type: none;
 }

 ul.sidebar-panel-subnav > li > a {
   color: #fff;
   text-decoration: none;
   font-size: 1.5rem;
   display: block;
   padding-bottom: 0.5em;
 }
</style>
