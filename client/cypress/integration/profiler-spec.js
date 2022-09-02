{
    describe('Profiler', () => {
        it('successfully stores variableInfo', () => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })
            cy.clearData()
            cy.createMockDataset('EyeDemoMockDV.json')

            cy.request('/api/dataset-info/').then((data) => {
                // Update Vuex store with the dataset to be profiled
                cy.vuex().invoke('dispatch', 'dataset/setDatasetInfo', data.body.results[0].object_id)
                    .then(() => {
                        cy.vuex().its('state.dataset.datasetInfo.objectId').should('exist')
                        // Get the current user id, for running the profiler
                        cy.request('rest-auth/user/').then((data) => {
                                const payload = {userId: data.body.object_id}
                                // Invoke vuex action for running the profiler and updating variableInfo
                                cy.vuex().invoke('dispatch', 'dataset/runProfiler', payload)
                                // Test that vuex store has been updated with variableInfo
                                cy.vuex().its('state.dataset.datasetInfo.depositorSetupInfo.variableInfo').should('exist')
                            cy.fixture('profiler').then((varsFixture) => {
                                cy.vuex().its('state.dataset.datasetInfo.depositorSetupInfo.variableInfo')
                                    .should('deep.equal', varsFixture)
                            })


                            }
                        )
                    })

            })


        })


    })
}