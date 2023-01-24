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

            cy.setupStatisticsPageFixtures('datasetInfoStep600.json', 'analysisPlanStep700.json')

        })


        it('Enables Create Statistics Button', () => {
            cy.get('h1').should('contain', 'Create Statistics')
            cy.get('[data-test="Add Statistic"]').click({force: true});
            cy.get('[data-test="AddStatisticDialog"]').should('be.visible')

            // The Create Statistics Button should be enabled after entering histogram edges
            cy.get('[data-test="Histogram"]').click({force: true});
            cy.get('[data-test="Trial"]').click({force: true})
            cy.get('[data-test="Fixed value"]').type('22')
            cy.get('[data-test="binEdges"]').click({force: true})
            cy.get('[data-test="histogramBinEdges"]').type("2,6,", {force: true})
            cy.get('[data-test="Create Statistic Button"]').should('be.enabled')
            cy.get('[data-test="Create Statistic Button"]').click({force: true})
            cy.get('[data-test="Create Statistics Title').should('be.visible')
            cy.get('[data-test="Add Statistic"]').should('be.visible')

            cy.get('[data-test="Add Statistic"]').click({force: true});
            cy.get('[data-test="AddStatisticDialog"]').should('be.visible')

            // The second time through, the Create Statistics button should still be enabled
            cy.get('[data-test="Histogram"]').click({force: true});
            cy.get('[data-test="Trial"]').click({force: true})
            cy.get('[data-test="Fixed value"]').type('33')
            cy.get('[data-test="binEdges"]').click({force: true})
            cy.get('[data-test="histogramBinEdges"]').type("4,8,", {force: true})
            cy.get('[data-test="Create Statistic Button"]').should('be.enabled')
            cy.get('[data-test="Create Statistic Button"]').click({force: true})


        })
        it('Displays correct Variable list', () => {
            cy.get('h1').should('contain', 'Create Statistics')
            cy.get('[data-test="Add Statistic"]').click({force: true});
            cy.get('[data-test="AddStatisticDialog"]').should('be.visible')
            cy.get('[data-test="Subject"]').should('be.enabled')
            cy.get('[data-test="Language"]').should('be.enabled')

            // After clicking Mean, the non-numeric variables should not be visible
            cy.get('[data-test="Mean"]').click({force: true})
            cy.get('[data-test="Subject"]').should('not.exist')
            cy.get('[data-test="Language"]').should('not.exist')
            cy.get('[data-test="Trial"]').click({force: true})

            cy.get('[data-test="Fixed value"]').type('22')
            cy.get('[data-test="Create Statistic Button"]').click({force: true})
            cy.get('[data-test="Create Statistics Title').should('be.visible')
            cy.get('[data-test="Add Statistic"]').should('be.visible')

            cy.get('[data-test="Add Statistic"]').click({force: true});
            cy.get('[data-test="AddStatisticDialog"]').should('be.visible')
            // The non-numeric fields should be visible when re-opening the Dialog
            cy.get('[data-test="Subject"]').should('be.enabled')
            cy.get('[data-test="Language"]').should('be.enabled')


        })
    })
}