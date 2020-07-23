<template>
  <div class="example">
    <h1>{{ msg }}</h1>
  </div>
</template>

<script>
export default {
  name: 'example',
  props: {
    msg: String
  }
}
</script>
