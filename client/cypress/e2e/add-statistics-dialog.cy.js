{
    describe('Create Statistics Wizard Step tests', () => {
        before(() => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })
            cy.clearData()
            //
        })
        beforeEach(() => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })
            cy.login('dev_admin', 'admin')
            cy.request('/cypress-tests/clear-test-data/').then((resp) => {
                console.log('CLEAR RESP: ' + JSON.stringify(resp))
            })
            cy.request('/cypress-tests/setup-demo-data/').then(() => {
                cy.logout()
                cy.login('dp_analyst', 'Test-for-2022')
                cy.visit('/my-data')
                cy.get('[data-test="continueWorkflow"]').click({force: true})


            })
        })


        it('Enables Create Statistics Button', () => {
            cy.get('h1').should('contain', 'Create Statistics')
            cy.get('[data-test="Add Statistic"]').click({force: true});
            cy.get('[data-test="AddStatisticDialog"]').should('be.visible')

            // The Create Statistics Button should be enabled after entering histogram edges
            cy.get('[data-test="Histogram"]').click({force: true});
            cy.get('[data-test="selfesteem"]').click({force: true})
            cy.get('[data-test="Fixed value"]').type('22')
            cy.get('[data-test="binEdges"]').click({force: true})
            cy.get('[data-test="histogramBinEdges"]').type("12,16,", {force: true})
            cy.get('[data-test="Create Statistic Button"]').should('be.enabled')
            cy.get('[data-test="Create Statistic Button"]').click({force: true})
            cy.get('[data-test="Create Statistics Title').should('be.visible')

            // wait until the vuex store is updated before adding the next statistic
            cy.vuex().its('state.dataset.analysisPlan.dpStatistics.length').should('be.equal', 1)
            cy.get('[data-test="Add Statistic"]').should('be.visible')
            cy.get('[data-test="Add Statistic"]').click({force: true});
            cy.get('[data-test="AddStatisticDialog"]').should('be.visible')

            // The second time through, the Create Statistics button should still be enabled
            cy.get('[data-test="Histogram"]').click({force: true});
            cy.get('[data-test="age"]').click({force: true})
            cy.get('[data-test="Fixed value"]').type('33')
            cy.get('[data-test="binEdges"]').click({force: true})
            cy.get('[data-test="histogramBinEdges"]').type("20,40,", {force: true})
            cy.get('[data-test="Create Statistic Button"]').should('be.enabled')
            cy.get('[data-test="Create Statistic Button"]').click({force: true})


        })
        it('Displays correct Variable list', () => {
            cy.get('h1').should('contain', 'Create Statistics')
            cy.get('[data-test="Add Statistic"]').click({force: true});
            cy.get('[data-test="AddStatisticDialog"]').should('be.visible')
            cy.get('[data-test="sex"]').should('be.enabled')
            cy.get('[data-test="maritalstatus"]').should('be.enabled')

            // After clicking Mean, the non-numeric variables should not be visible
            cy.get('[data-test="Mean"]').click({force: true})
            cy.get('[data-test="sex"]').should('not.exist')
            cy.get('[data-test="maritalstatus"]').should('not.exist')
            cy.get('[data-test="age"]').click({force: true})

            cy.get('[data-test="Fixed value"]').type('22')
            cy.get('[data-test="Create Statistic Button"]').click({force: true})
            cy.get('[data-test="Create Statistics Title').should('be.visible')
            cy.vuex().its('state.dataset.analysisPlan.dpStatistics.length').should('be.equal', 1)
            cy.get('[data-test="Add Statistic"]').should('be.visible')

            cy.get('[data-test="Add Statistic"]').click({force: true});
            cy.get('[data-test="AddStatisticDialog"]').should('be.visible')
            // The non-numeric fields should be visible when re-opening the Dialog
            cy.get('[data-test="sex"]').should('be.enabled')
            cy.get('[data-test="maritalstatus"]').should('be.enabled')


        })
    })
}