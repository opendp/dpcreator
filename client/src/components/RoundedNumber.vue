<template>
  <div
      class="white rounded-circle d-inline-block px-4 py-1 font-weight-bold mb-5 grid-item__title"
  >
    {{ number }}
  </div>
</template>

<script>
export default {
  name: "RoundedNumber",
  props: ["number"]
};
</script>
