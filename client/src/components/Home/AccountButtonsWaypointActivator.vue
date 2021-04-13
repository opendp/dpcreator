<template>
  <div
      class="separator"
      v-waypoint="{
      active: true,
      callback: onSeparatorAppear
    }"
      style="minHeight: 60px"
  ></div>
</template>

<script>
export default {
  name: "AccountButtonsWaypointActivator",
  methods: {
    onSeparatorAppear({going}) {
      if (going === this.$waypointMap.GOING_IN) {
        this.$root.$emit("buttonsShouldNotStick");
      }
      if (going === this.$waypointMap.GOING_OUT) {
        this.$root.$emit("buttonsShouldStick");
      }
    }
  }
};
</script>
