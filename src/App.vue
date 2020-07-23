<template>
  <div id="app">
    <img alt="Vue logo" src="./assets/logo.png">
    <example msg="Welcome to Example"/>
  </div>
</template>

<script>
import example from './components/example.vue'

export default {
  name: 'App',
  components: {
   example
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
