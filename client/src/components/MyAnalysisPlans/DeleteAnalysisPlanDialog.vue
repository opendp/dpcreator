<template>
    <v-dialog v-model="dialogDelete" max-width="500px">
        <v-card elevation="2" class="px-10 py-12">
            <v-icon
                    style="position: absolute; right: 40px"
                    @click="() => $emit('cancel')"
            >mdi-close
            </v-icon
            >
            <v-card-title>
                <h2 data-test="deleteAnalysisDialogTitle" class="title-size-2 mb-5 font-weight-bold">
                    Are you sure?
                </h2>
            </v-card-title>
            <v-card-text class="text--primary">
                This will delete Analysis Plan "{{ analysisPlanName() }}".
            </v-card-text>
            <v-card-actions>
                <Button
                        data-test="deleteAnalysisConfirm"
                        color="primary"
                        :click="() => deleteConfirm()"
                        label="OK"
                />
                <Button
                        outlined
                        data-test="deleteAnalysisCancel"
                        color="primary"
                        :click="() => $emit('cancel')"
                        label="Cancel"
                />
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>

<script>
import Button from "@/components/DesignSystem/Button.vue";

export default {
    components: {Button},
    name: "DeleteAnalysisPlanDialog",
    props: ["dialogDelete", "analysisPlan"],
    methods: {
        deleteConfirm() {
            const payload = {
                datasetId: this.analysisPlan.datasetId,
                analysisPlanId: this.analysisPlan.objectId
            }
            this.$store.dispatch('dataset/deleteAnalysisPlan', payload)
            this.closeDelete();
        },
        closeDelete() {
            this.$emit("close")
        },
        analysisPlanName() {
            let name = ""
            if (this.analysisPlan !== null) {
                name = this.analysisPlan.name
            }
            return name
        }
    }
};
</script>
