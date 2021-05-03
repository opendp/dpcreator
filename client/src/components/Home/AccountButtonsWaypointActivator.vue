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
    onSeparatorAppear({going, direction}) {
      if (
          going === this.$waypointMap.GOING_IN &&
          direction === this.$waypointMap.DIRECTION_TOP
      ) {
        this.$root.$emit("buttonsShouldNotStick");
      }
      if (
          going === this.$waypointMap.GOING_OUT &&
          direction === this.$waypointMap.DIRECTION_BOTTOM
      ) {
        this.$root.$emit("buttonsShouldStick");
      }
    }
  }
};
</script>
