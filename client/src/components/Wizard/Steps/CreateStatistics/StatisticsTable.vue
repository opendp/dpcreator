<template>
  <div>
    <v-data-table
        :headers="headers"
        :items="statistics"
        item-key="id"
        no-data-text="Create statistic"
        show-expand
        :single-expand="false"
        :expanded.sync="expanded"
        :items-per-page="-1"
        hide-default-footer
    >

      <template v-slot:[`item.num`]="{ index }">
        <span class="index-td">{{ index + 1 }}</span>
      </template>
      <template :data-test="'statistic'+index" v-slot:[`item.Statistic`]="{ item }">
        <div data-test="statistic">{{ item.statistic.label }}</div>
      </template>
      <template v-slot:[`item.missingValuesHandling`]="{ item }">
        <div v-if="item.missingValuesHandling === 'insert_fixed' ">
          Insert Fixed Value: {{ item.fixedValue }}
        </div>
      </template>
      <template v-slot:[`item.epsilon`]="{ item }">
        <v-text-field v-if="item.locked"
                      v-model="item.epsilon"
                      type="number"
                      :rules="[validateEpsilon(item)]"
                      v-on:click="currentItem=item"
                      v-on:keyup="$emit('editEpsilon', item)"
        >
        </v-text-field>
        <div v-else>
          {{ Number(item.epsilon).toFixed(3) }}
        </div>
      </template>
      <template v-slot:[`item.delta`]="{ item }">
        <div v-if="isDeltaStat(item)">
          <v-text-field
              v-model="item.delta"
              type="number"
              :rules="[validateDelta]"
              v-on:click="currentItem=item"
              :disabled="!(item.locked)"
              v-on:change="$emit('editDelta', item)"
          >
          </v-text-field>
        </div>
        <div v-if="!isDeltaStat(item)">
          NA
        </div>
      </template>
      <template v-slot:[`item.error`]="{ item }">


        <v-row v-if="item.accuracy">
         <span class="d-flex justify-center">
          {{ getAccuracy(item) }}
         <QuestionIconTooltip
             :text="errorHelpText(item)"
         />
           </span>
        </v-row>


      </template>
      <template v-slot:[`item.actions`]="{ item }">
        <div class="d-flex justify-space-between">
          <v-tooltip bottom max-width="220px">
            <template v-slot:activator="{ on, attrs }">
              <!-- TODO: Implement the logic of locking a statistic -->
              <v-icon
                  v-bind="attrs"
                  v-on="on"
                  class="mr-2"
                  @click="$emit('changeLockStatus', item)"
              >
                {{ item.locked ? "mdi-lock" : "mdi-lock-open" }}
              </v-icon>
            </template>
            <!-- TODO: Define the default status of the lock and adjust the label of the tooltip -->
            <span>Lock/Unlock</span>
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
      <template v-slot:item.data-table-expand="{ item, isExpanded, expand }">
        <v-icon
            large
            @click="expand(true)" v-if="item.canExpand && !isExpanded">
          >
          mdi-chevron-down
        </v-icon>
        <v-icon
            large
            @click="expand(false)" v-if="item.canExpand && isExpanded">
          >
          mdi-chevron-up
        </v-icon>

      </template>
      <template v-slot:expanded-item="{ headers, item }">
        <td :colspan="11">
          {{ getExpandedText(item) }}
        </td>
      </template>
    </v-data-table>
    <Button
        color="soft_primary primary--text"
        width="100%"
        depressed
        data-test="Add Statistic"
        :click="() => $emit('newStatisticButtonPressed')"
    >
      <v-icon left>mdi-plus-box</v-icon>
      Create New Statistic
    </Button>
  </div>
</template>

<style lang="scss">
.v-data-table__empty-wrapper {
  font-style: italic;
}

.v-data-table-header th {

  vertical-align: top;

}

</style>

<script>
import Button from "../../../DesignSystem/Button.vue";
import QuestionIconTooltip from "../../../DynamicHelpResources/QuestionIconTooltip.vue";
import Decimal from "decimal.js";
import createStatsUtils, {MAX_TOTAL_EPSILON, MIN_EPSILON} from "@/shared/createStatsUtils";

export default {
  components: {QuestionIconTooltip, Button},
  name: "StatisticsTable",
  props: ["statistics", "totalEpsilon", "totalDelta"],
  data: () => ({
    headers: [
      {value: "num"},
      {text: "Statistic", value: "label"},
      {text: "Variable", value: "variable"},
      {text: "Handle Missing Values", value: "missingValuesHandling"},
      {text: "Epsilon", value: "epsilon"},
      {text: "Delta", value: "delta"},
      {text: "Error", value: "error", width: "15%"},
      {text: "", value: "actions"},
      {text: "", value: 'data-table-expand'},
    ],
    currentItem: null,
    expanded: []
  }),
  computed:
      {
        deltaDisabled(item) {
          return !(item.locked && createStatsUtils.isDeltaStat(item.statistic))
        }
      },
  methods: {
    isDeltaStat(item) {
      return createStatsUtils.isDeltaStat(item.statistic)
    },
    errorHelpText(item) {
      return "We are " + (item.cl * 100) + "% confident that the magnitude of the noise will"
          + " be less than " + this.getAccuracy(item)
    },
    getExpandedText(item) {
      let text = ""
      if (item.statistic == 'histogram') {
        text = 'Histogram bin type: ' + item.histogramBinType
      }
      return text
    },
    getAccuracy(item) {
      return Number(item.accuracy.value).toPrecision(3)
    },
    validateEpsilon(item) {
      item.valid = true
      if (isNaN(item.epsilon)) {
        item.valid = false
      } else if (item.epsilon < MIN_EPSILON || item.epsilon > MAX_TOTAL_EPSILON) {
        item.valid = false
      } else {
        let lockedEpsilon = new Decimal('0.0');
        this.statistics.forEach(function (item) {
          if (item.locked) {
            lockedEpsilon = lockedEpsilon.plus(item.epsilon)
          }
        })
        if (Number(lockedEpsilon) > Number(this.totalEpsilon))
          item.valid = false
      }
      this.updateCompleteStatus()
      return item.valid

    },
    updateCompleteStatus() {
      let allValid = true
      this.statistics.forEach((item) => {
        if (item.valid == false) {
          allValid = false
        }
      })
      this.$emit("stepCompleted", 3, allValid);
    },
    validateDelta(value) {
      let lockedDelta = new Decimal('0.0');
      this.statistics.forEach(function (item) {
        if (item.locked && createStatsUtils.isDeltaStat(item.statistic)) {
          lockedDelta = lockedDelta.plus(item.delta)
        }
      })
      if (lockedDelta > this.totalDelta)
        item.valid = false
      else {
        item.valid = true
      }
      return item.valid
    }
  }


};
</script>
