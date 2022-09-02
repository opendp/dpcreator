

{
    describe('Multiple Partial Updates', () => {
        it('saves the vuex state correctly', () => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })
            cy.clearData()
            cy.createMockDataset('EyeDemoMockDV.json')

            // without this wait, sometimes the api/dataset-info/<objectId> call
            // returns a 404.
            cy.wait(1000)
            // click on the start Process button on the welcome page,
            // to navigate to the Validate Dataset step of the Wizard.
            // This will setup Vuex state to contain the Dataset.
            cy.get('[data-test="Start Process"]').click();
            cy.url().should('contain', 'wizard')
            cy.request('/api/dataset-info/').then((data) => {
                // save the original copy of the object
                const datasetInfo = data.body.results[0]
                //   console.log('returned depositorSetupInfo' + JSON.stringify(datasetInfo.depositorSetupInfo))
                const depositorSetupId = datasetInfo.depositor_setup_info.object_id
                // update the user step
                // update something else - epsilon
                // check the state of the object in Vuex, it should have the correct userStep && epsilon
                const payload1 = {objectId: depositorSetupId, props: {userStep: 'step_500'}}
                const payload2 = {objectId: depositorSetupId, props: {epsilon: .75}}
                const payload3 = {objectId: depositorSetupId, props: {delta: .01}}
                const payload4 = {objectId: depositorSetupId, props: {defaultDelta: .002}}
                cy.vuex().invoke('dispatch', 'dataset/updateDepositorSetupInfo', payload1)
                cy.vuex().invoke('dispatch', 'dataset/updateDepositorSetupInfo', payload2)
                cy.vuex().invoke('dispatch', 'dataset/updateDepositorSetupInfo', payload3)
                cy.vuex().invoke('dispatch', 'dataset/updateDepositorSetupInfo', payload4)

                cy.vuex().its('state.dataset.datasetInfo.depositorSetupInfo.epsilon')
                    .should('not.be.null')
                cy.vuex().its('state.dataset.datasetInfo.depositorSetupInfo.userStep')
                    .should('equal', payload1.props.userStep)
                cy.vuex().its('state.dataset.datasetInfo.depositorSetupInfo.delta')
                    .should('equal', payload3.props.delta)
                cy.vuex().its('state.dataset.datasetInfo.depositorSetupInfo.defaultDelta')
                    .should('equal', payload4.props.defaultDelta)


            })
        })
    })
    /*
      Commenting out the API test, because need to add authorization
      headers to the direct api call, in order to run this
     *//*
        it('patch saves partial updates correctly', () => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })
            cy.clearData()
            cy.createMockDataset('EyeDemoMockDV.json')
            // click on the start Process button on the welcome page,
            // to navigate to the Validate Dataset step of the Wizard.
            // This will setup Vuex state to contain the Dataset.
            cy.get('[data-test="Start Process"]').click();
            cy.url().should('contain', 'wizard')
            cy.request('/api/dataset-info/').then((data) => {
                    // save the original copy of the object
                    const datasetInfo = camelcaseKeys(data.body.results[0], {deep: true});
                    //   console.log('returned depositorSetupInfo' + JSON.stringify(datasetInfo.depositorSetupInfo))
                    const depositorSetupId = datasetInfo.depositorSetupInfo.objectId
                    // update the user step
                    // update something else - epsilon
                    // check the state of the object in Vuex, it should have the correct userStep && epsilon

                    const payload1 = { objectId: depositorSetupId, props: {userStep: 'step_500'} }
                    const payload2 = { objectId: depositorSetupId, props: {epsilon: .75} }

                    cy.request('PATCH', '/api/deposit/'+ depositorSetupId+'/', payload1,  )
                    cy.request('PATCH', '/api/deposit/'+ depositorSetupId+'/', payload2 )
                    cy.wait(2000)
                    cy.request('/api/dataset-info/'+ datasetInfo.objectId +'/').then((data) => {
                        const datasetInfo = camelcaseKeys(data.body,{deep: true})
                        expect(datasetInfo.depositorSetupInfo.epsilon).to.not.be.null
                        expect(datasetInfo.depositorSetupInfo.userStep).to.equal(payload1.userStep)

                    })
             })
        }) */

}
