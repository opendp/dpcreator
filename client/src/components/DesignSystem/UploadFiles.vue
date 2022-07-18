<template>
  <div>
    <Button v-if="!uploadClicked"
            :click="onUploadClick"
            data-test="myDataUploadButton"
            color="primary"
            label="Upload a File"

            :class="{
                  'width80 mx-auto d-block mb-2': $vuetify.breakpoint.xsOnly,
                  'mr-2 mb-2': $vuetify.breakpoint.smAndUp
                }"
    />
    <div v-if="currentFile && uploadProgress < 100">
      <div>
        <v-progress-linear
            v-model="progress"
            color="light-blue"
            height="25"
            reactive
        >
          <strong>{{ uploadProgress }} %</strong>
        </v-progress-linear>
      </div>
    </div>
    <div v-if="uploadClicked">
      <v-row no-gutters justify="center" align="center">
        <v-col>
          <div data-test="dragArea" @dragover.prevent @drop.prevent @drop="dragFile">
            <v-file-input
                data-test="fileInput"
                accept=".csv,.tsv"
                show-size
                label="Click to select a file, or drag file here (.csv, .tab, .tsv)"
                @change="selectFile"
            ></v-file-input>

          </div>
          <v-alert type="error" dismissible v-if="message" color="blue-grey" dark>
            {{ message }}
          </v-alert>
        </v-col>
      </v-row>
    </div>


  </div>
</template>

<script>
import Button from "@/components/DesignSystem/Button";
import {mapState} from "vuex";

export default {
  name: "upload-files",
  components: {Button},
  data() {
    return {
      fileTypeError: false,
      currentFile: undefined,
      message: "",
      uploadClicked: false
    };
  },
  computed: {
    ...mapState('auth', ['user']),
    ...mapState('dataset', ["uploadProgress"])
  },
  methods: {
    onUploadClick() {
      this.uploadClicked = true
    },
    selectFile(file) {
      this.progress = 0;
      this.currentFile = file;
      this.uploadDataset(file)
    },
    dragFile(e) {
      this.currentFile = e.dataTransfer.files[0]
      const extension = this.currentFile.name.split(".").pop();
      const isSupported = ["csv"].includes(extension);
      if (isSupported) {
        this.uploadDataset(this.currentFile)
      } else {
        this.message = 'file type ' + extension + "is not supported."
      }
    },
    uploadDataset(file) {
      const payload = {file: file, creatorId: this.user.objectId}
      this.$store.dispatch('dataset/uploadDataset', payload)
    },

  },
  watch: {
    uploadProgress: function (val, oldVal) {
      if (val == 100) {
        this.currentFile = null
        this.uploadClicked = false
      }
    }
  },
};
</script>
