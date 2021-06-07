<template>
  <div>
    <v-data-table
        :headers="headers"
        :items="datasets"
        :items-per-page="computedItemsPerPage"
        :search="searchTerm || search"
        :hide-default-footer="true"
        class="my-data-table"
        :page.sync="page"
        @page-count="pageCount = $event"
        :disable-sort="$vuetify.breakpoint.xsOnly"
    >
      <template v-slot:top v-if="inlineSearchEnabled">
        <v-text-field
            v-model="search"
            label="Search"
            class="mx-4"
        ></v-text-field>
      </template>
      <template v-slot:[`header.options`]="{ header }">
        <span class="font-weight-bold text-start d-inline">
          {{ header.text }}</span
        >
      </template>
      <template v-slot:[`item.num`]="{ index }">
        <span class="index-td hidden-xs-only grey--text">{{ index + 1 }}</span>
      </template>
      <template v-slot:[`item.status`]="{ item }">
        <StatusTag :status="stepInformation[item.status].workflowStatus"/>
      </template>
      <template v-slot:[`item.remainingTime`]="{ item }">
        <span
            :class="{
            'error_status__color--text': item.remainingTime === 'Expired'
          }"
        >{{ item.remainingTime }}</span
        >
      </template>
      <template v-slot:[`item.options`]="{ item }">
        <Button
            v-for="(action, index) in statusInformation[stepInformation[item.status].workflowStatus]
            .availableActions"
            :key="action + '-' + index"
            small
            :outlined="action !== CONTINUE_WORKFLOW"
            :disabled="
            (action === CONTINUE_WORKFLOW &&
              item.remainingTime === 'Expired') ||
              (action === CONTINUE_WORKFLOW && $vuetify.breakpoint.xsOnly)
          "
            color="primary"
            :class="{
            'width100 d-block': $vuetify.breakpoint.xsOnly,
            'mr-2': $vuetify.breakpoint.smAndUp
          }"
            :classes="`my-2 ${action}`"
            :click="() => handleButtonClick(action, item)"
            :label="actionsInformation[action]"
        />
      </template>
      <template v-slot:footer="{ props }">
        <div
            v-if="paginationVisible"
            class="d-flex justify-space-between mt-10 itemsPerPage"
            :class="{
            'flex-column align-center': $vuetify.breakpoint.xsOnly
          }"
        >
          <div class="d-inline">
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
          <div class="d-inline">
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

const {
  VIEW_DETAILS,
  CONTINUE_WORKFLOW,
  CANCEL_EXECUTION
} = actionsInformation.actions;

export default {
  name: "MyDataTable",
  components: {StatusTag, Button},
  props: {
    datasets: {
      type: Array
    },
    inlineSearchEnabled: {
      type: Boolean,
      default: false
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
  data: function () {
    return {
      computedItemsPerPage: this.itemsPerPage,
      page: 1,
      pageCount: 0,
      search: "",
      headers: [
        {value: "num"},
        {text: "Dataset", value: "name"},
        {text: "Status", value: "status"},
        //  {text: "Remaining time to complete release", value: "remainingTime"},
        {text: "Options", value: "options", align: "end"}
      ],
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
      this[action](item);
    },
    viewDetails(item) {
      this.$router.push(`${NETWORK_CONSTANTS.MY_DATA.PATH}/${item.datasetId}`);
    },
    continueWorkflow(item) {
      //TODO: Implement Continue Workflow handler
      alert("continue workflow " + item.dataset);
    },
    cancelExecution(item) {
      //TODO: Implement Cancel Execution handler
      alert("cancel execution " + item.dataset);
    }
  }
};
</script>
