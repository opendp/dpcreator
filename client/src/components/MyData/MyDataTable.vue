<template>
  <div>
    <v-data-table
        :headers="headers"
        :items="datasets"
        :items-per-page="computedItemsPerPage"
        :search="searchTerm ? searchTerm : search"
        :hide-default-footer="true"
        class="my-data-table"
        :page.sync="page"
        @page-count="pageCount = $event"
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
        <span class="index-td">{{ index + 1 }}</span>
      </template>
      <template v-slot:[`item.status`]="{ item }">
        <v-chip :color="statusInformation[item.status].color" label>
          <v-icon left small>
            {{ statusInformation[item.status].icon }}
          </v-icon>
          {{ statusInformation[item.status].label }}
        </v-chip>
      </template>
      <template v-slot:[`item.options`]="{ item }">
        <v-btn
            v-for="action in statusInformation[item.status].availableActions"
            :key="action"
            color="primary"
            :class="`mr-3 ${action}`"
            @click="handleButtonClick(action, item)"
        >
          {{ actionsInformation[action] }}
        </v-btn>
      </template>
      <template v-slot:footer="{ props }">
        <div
            v-if="paginationVisible"
            class="d-flex justify-space-between mt-10 itemsPerPage"
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
}
</style>

<script>
import statusInformation from "../../data/statusInformation";
import actionsInformation from "../../data/actionsInformation";

export default {
  name: "MyDataTable",

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
      default: 3
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
        {text: "Dataset", value: "dataset"},
        {text: "Status", value: "status"},
        {text: "Options", value: "options", align: "end"}
      ],
      statusInformation,
      actionsInformation
    };
  },
  methods: {
    handleButtonClick(action, item) {
      this[action](item);
    },
    viewDetails(item) {
      this.$router.push(`/my-data/${item.datasetId}`);
    },
    continueWorkflow(item) {
      alert("continue workflow " + item.dataset);
    },
    cancelExecution(item) {
      alert("cancel execution " + item.dataset);
    }
  }
};
</script>
