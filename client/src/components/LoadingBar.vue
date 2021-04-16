<template>
  <div class="v-card__progress">
    <div
        role="progressbar"
        aria-valuemin="0"
        aria-valuemax="100"
        class="v-progress-linear theme--light"
    >
      <div
          class="v-progress-linear__background grey lighten-1"
          style="opacity: 0.3; left: 0%; width: 100%;"
      ></div>
      <div class="v-progress-linear__buffer"></div>
      <div
          class="v-progress-linear__indeterminate v-progress-linear__indeterminate--active"
      >
        <div class="v-progress-linear__indeterminate long grey lighten-1"></div>
        <div
            class="v-progress-linear__indeterminate short grey lighten-1"
        ></div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.v-card__progress {
  padding: 15px 0;
}
.v-card__progress:first-child {
  padding-top: 30px;
}
.v-card__progress:last-child {
  padding-bottom: 30px;
}

.v-progress-linear {
  border-radius: 50px;
  height: 20px;
}
</style>

<script>
export default {
  name: "LoadingBar"
};
</script>
