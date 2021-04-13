<template>
  <div>
    <v-data-table
        :headers="headers"
        :items="statistics"
        no-data-text="Create your first statistic"
        hide-default-footer
    >
      <template v-slot:[`header.error`]="{ header }">
        <span>
          {{ header.text }}
          <QuestionIconTooltip
              text="Calculated error to be added to your statistic."
          />
        </span>
      </template>
      <template v-slot:[`item.num`]="{ index }">
        <span class="index-td">{{ index + 1 }}</span>
      </template>
      <template v-slot:[`item.actions`]="{ item }">
        <div class="d-flex justify-space-between">
          <v-tooltip bottom max-width="220px">
            <template v-slot:activator="{ on, attrs }">
              <v-icon
                  v-bind="attrs"
                  v-on="on"
                  class="mr-2"
                  @click="$emit('editStatistic', item)"
              >
                mdi-lock
              </v-icon>
            </template>
            <span>Lock</span>
          </v-tooltip>
          <v-tooltip bottom max-width="220px">
            <template v-slot:activator="{ on, attrs }">
              <v-icon
                  v-bind="attrs"
                  v-on="on"
                  class="mr-2"
                  @click="$emit('editStatistic', item)"
              >
                mdi-pencil
              </v-icon>
            </template>
            <span>Edit</span>
          </v-tooltip>
          <v-tooltip bottom max-width="220px">
            <template v-slot:activator="{ on, attrs }">
              <v-icon
                  v-bind="attrs"
                  v-on="on"
                  @click="$emit('deleteStatistic', item)"
              >
                mdi-delete
              </v-icon>
            </template>
            <span>Delete</span>
          </v-tooltip>
        </div>
      </template>
    </v-data-table>
    <v-btn
        color="blue lighten-4 primary--text"
        width="100%"
        depressed
        @click="$emit('newStatisticButtonPressed')"
    >
      <v-icon left>mdi-plus-box</v-icon>
      Create new statistic
    </v-btn>
  </div>
</template>

<script>
import QuestionIconTooltip from "../../../DynamicHelpResources/QuestionIconTooltip.vue";

export default {
  components: {QuestionIconTooltip},
  name: "StatisticsTable",
  props: ["statistics"],
  data: () => ({
    headers: [
      {value: "num"},
      {text: "Statistic", value: "statistic"},
      {text: "Variable", value: "variable"},
      {text: "Epsilon", value: "epsilon"},
      {text: "Error", value: "error"},
      {text: "", value: "actions"}
    ]
  })
};
</script>
