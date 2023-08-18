<template>
  <div>

    <v-data-table v-if="tableItems"
        data-test="my-plans-table"
        :headers="headers"
        :items="tableItems"
         :custom-filter="filterOnlyCapsText"
        :items-per-page="computedItemsPerPage"
        :search="search"
        :hide-default-footer="true"
        class="my-data-table"
        :page.sync="page"
        @page-count="pageCount = $event"
        :disable-sort="$vuetify.breakpoint.xsOnly"
    >
      <template v-slot:top v-if="inlineSearchEnabled">
      <v-container>
      <v-row  align="start"
              no-gutters>
        <v-col cols="6" class="align-left">
          <b>Filter By:</b>
          <v-select
              v-model="selectedFilter"
              :items="filterOptions"
              label="Select Filter"
          ></v-select>
          <v-btn text small @click="clearFilter">Clear Filter</v-btn>
        </v-col>
      </v-row>
      </v-container>
      </template>
      <template v-slot:[`header.options`]="{ header }">
        <span class="font-weight-bold text-start d-inline">
          {{ header.text }}</span
        >
      </template>
      <template v-slot:[`item.num`]="{ index }">
        <span class="index-td hidden-xs-only grey--text">{{ index + 1 }}</span>
      </template>
      <template v-slot:[`item.epsilon`]="{ item }">
        {{item.epsilon}}&epsilon;
      </template>
        <template v-slot:[`item.status`]="{ item }">
            <StatusTag data-test="table status tag" :status="getWorkflowStatus(item)"/>
        </template>
        <template v-slot:[`item.expirationDate`]="{ item }">
            <div v-if="!isCompleted(item)">
           <span v-if="isExpired(item)" class='error_status__color--text'>
             Time has expired
           </span>
                <span v-else>
             {{ formatDate(item.expirationDate) }}
           </span>
            </div>
            <div v-else-if="item.releaseInfo">
                Release Generated on {{ new Date(item.releaseInfo.created).toDateString() }}
            </div>
            <div v-else>
                Release Completed
            </div>
        </template>
Z        <template v-slot:[`item.actions`]="{ item,index }">
            <div  class="d-flex justify-space-between">

                <v-tooltip

                        v-for="(action,  actionIndex) in statusInformation[stepInformation[item.userStep].workflowStatus]
            .availableActions"
                        bottom max-width="220px">
                    <template v-slot:activator="{ on, attrs }">
                        <v-icon
                                :data-test="action+index"
                                v-bind="attrs"
                                v-on="on"
                                class="mr-2"
                                @click="handleButtonClick(action, item)"
                        >
                            {{ actionsInformation.icons[action] }}

                        </v-icon>
                    </template>
                    <span>{{ actionsInformation[action] }}</span>
                </v-tooltip>

            </div>
        </template>


      <template v-slot:footer="{ props }">
        <div
            v-if="paginationVisible"
            class="d-flex justify-space-between mt-10 itemsPerPage"
            :class="{
            'flex-column align-center': $vuetify.breakpoint.xsOnly
          }"
        >
          <div v-if="props.pagination.itemsLength > 5" class="d-inline">
            Showing
            <v-select
                v-model="computedItemsPerPage"
                :items="[5, 10, 30, 50, 100]"
                outlined
                hide-selected
                class="d-inline-block select"
                dense
            ></v-select>
            <span>of {{ props.pagination.itemsLength }}</span>
          </div>
          <div v-if="pageCount > 1" class="d-inline">
            <v-pagination
                v-model="page"
                :length="pageCount"
                class="d-inline-block"
                circle
            ></v-pagination>
          </div>
        </div>
      </template>


    </v-data-table>
    <DeleteAnalysisPlanDialog
        v-if="selectedItem"
        :dialogDelete="dialogDelete"
        :analysisPlan="selectedItem"
        v-on:cancel="closeDelete"
        v-on:close="closeDelete"
    />
  </div>

</template>

<style lang="scss">
.my-data-table {
  th {
    span {
      color: #000000;
    }

    color: inherit !important;
    border-bottom-color: black !important;
  }
  .index-td {
    color: rgba(0, 0, 0, 0.6);
    font-weight: 600;
    font-size: 0.75rem;
  }
  .select {
    max-width: 90px;
    text-align: center;
    margin: 0 10px !important;
  }
  .v-select__selections input {
    display: none;
  }

  .v-pagination__navigation,
  .v-pagination__item--active,
  .v-pagination__item {
    box-shadow: none;

    &:focus {
      outline: none;
    }
  }

  th:last-child {
    text-align: start !important;
  }

  &.v-data-table > .v-data-table__wrapper > table > thead > tr > th {
    font-size: 0.875rem;
  }

  .itemsPerPage {
    font-size: 0.875rem;

    span {
      color: rgba(0, 0, 0, 0.6);
    }
  }

  .cancelExecution,
  .continueWorkflow {
    min-width: 160px !important;
  }

  .viewDetails {
    min-width: unset !important;
  }

  .delete {
    min-width: unset !important;
  }

  .v-data-table-header-mobile {
    display: none;
  }

  .v-data-table__mobile-table-row {
    .v-data-table__mobile-row:first-child {
      display: none;
    }

    .v-data-table__mobile-row {
      align-items: unset;
    }
  }
}
</style>

<script>

import statusInformation from "../../data/statusInformation";
import actionsInformation from "../../data/actionsInformation";
import stepInformation from "@/data/stepInformation";
import StatusTag from "../DesignSystem/StatusTag.vue";
import Button from "../DesignSystem/Button.vue";
import NETWORK_CONSTANTS from "../../router/NETWORK_CONSTANTS";
import DeleteDatasetDialog from "@/components/MyData/DeleteDatasetDialog";
import DeleteAnalysisPlanDialog from "@/components/MyAnalysisPlans/DeleteAnalysisPlanDialog.vue";
import {mapGetters, mapState} from "vuex";

const {
  VIEW_DETAILS,
  CONTINUE_WORKFLOW,
  CANCEL_EXECUTION
} = actionsInformation.actions;

// plan filter options
const MY_PLANS = 'My Plans';
const CREATED_FROM_MY_DATASETS = 'Plans Created From My Datasets';
const RELEASED_PLANS = 'Released Plans';


export default {
  name: "MyPlansTable",
  components: {DeleteAnalysisPlanDialog, StatusTag, Button, DeleteDatasetDialog},
  props: {
    plans: {
      type: Array
    },
    inlineSearchEnabled: {
      type: Boolean,
      default: true
    },
    searchTerm: {
      type: String
    },
    itemsPerPage: {
      type: Number,
      default: 4
    },
    paginationVisible: {
      type: Boolean,
      default: true
    }
  },
  computed: {
    tableItems(){
      let items = []
      if (this.selectedFilter === RELEASED_PLANS) {
        items = this.plans.filter(plan => plan.status === "step_1200")
      }
      else if (this.selectedFilter === MY_PLANS) {
        items = this.plans.filter(plan =>   plan.analystName == this.user.username)
      }
      else if (this.selectedFilter === CREATED_FROM_MY_DATASETS) {
        items = this.plans.filter(plan =>  plan.datasetOwnerId == this.user.objectId)
      } else {
        items = [...this.plans]; // Create a shallow copy of the plans array
      }
      return items
    },
    ...mapState('auth', ['user']),
  },
    data: function () {
    return {
      computedItemsPerPage: this.itemsPerPage,
      page: 1,
      pageCount: 0,
      search: "",

      dialogDelete: false,
      selectedItem: null,
      headers: [
        {value: "num"},
        {text: "Dataset Name", value: "datasetName"},
        {text: "Plan Name", value: "name"},
        {text: "Analyst", value: "analystName"},
        {text: "Budget", value: "epsilon"},
        {text: "Expiration Date", value: "expirationDate"},
        {text: "Status", value: "status"},
        {text: "Options", value: "actions", align: "end"}

      ],
      selectedFilter: '', // Initialize selected filter
      filterOptions: [MY_PLANS, CREATED_FROM_MY_DATASETS, RELEASED_PLANS],
      statusInformation,
      actionsInformation,
      stepInformation,
      VIEW_DETAILS,
      CONTINUE_WORKFLOW,
      CANCEL_EXECUTION
    };
  },
  methods: {
    handleButtonClick(action, item) {
      this[action](item)
    },

    clearFilter() {
      this.selectedFilter = ''; // Clear the selected filter
    },
    filterOnlyCapsText (value, query, item) {
      return value != null && query != null && typeof value === 'string' && value.toString().toLocaleUpperCase().indexOf(query) !== -1
    },
    deleteItem(item) {
      this.selectedItem = Object.assign({}, item);
      this.dialogDelete = true;
    },
    closeDelete() {
      this.dialogDelete = false
      this.selectedItem = null
    },
    isExpired(item) {
        return item.isExpired
    },
    isCompleted(item) {
        return item.isCompleted
    },
    delete(item) {
      this.deleteItem(item)
    },

    formatDate(dateString) {
      const dateObj = new Date(dateString);
      // The dateString returned from the v-date-picker is in UTC, so we have to display that
      // in the same UTC timezone
      const options = { timeZone: 'UTC', year: 'numeric', month: 'long', day: 'numeric' };
      const formattedDate = dateObj.toLocaleString('en-US', options);
      return formattedDate
     },
    viewDetails(item) {
      this.goToPage(item, `${NETWORK_CONSTANTS.MY_DATA_DETAILS.PATH}`)
    // TODO: create MY_PLAN_DETAILS
    },
    continueWorkflow(item) {
      this.goToPage(item, `${NETWORK_CONSTANTS.ANALYST_WIZARD.PATH}`)
    },
    getWorkflowStatus(item) {
        const workflowStatus= stepInformation[item.userStep].workflowStatus
        return workflowStatus
    },
    goToPage(item, path) {
      this.$store.dispatch('dataset/setAnalysisPlan', item.objectId)
          .then(() => {
                 this.$router.push(path)
          })
    },
    cancelExecution(item) {
      //TODO: Implement Cancel Execution handler
      alert("cancel execution " + item.dataset);
    }
  }
};
</script>
