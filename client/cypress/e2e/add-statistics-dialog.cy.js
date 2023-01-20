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
            cy.pause()
            cy.get('h1').should('contain', 'Create Statistics')
            cy.get('[data-test="Add Statistic"]').click({force: true});
            cy.get('[data-test="AddStatisticDialog"]').should('be.visible')
            // The fixed input field should be visible after switching from Count to Mean
            cy.get('[data-test="Histogram"]').click({force: true});
            cy.get('[data-test="Trial"]').click({force: true})
            cy.get('[data-test="Fixed value"]').type('22')
            cy.pause()
            cy.get('[data-test="binEdges"]').click({force: true})
            cy.get('[data-test="histogramBinEdges"]').type("2,6,", {force: true})
            cy.get('[data-test="Create Statistic Button"]').click({force: true})
            cy.get('[data-test="Create Statistics Title').should('be.visible')
            cy.get('[data-test="Add Statistic"]').should('be.visible')

            cy.get('[data-test="Add Statistic"]').click({force: true});
            cy.get('[data-test="AddStatisticDialog"]').should('be.visible')
            // The fixed input field should be visible after switching from Count to Mean
            cy.get('[data-test="Histogram"]').click({force: true});
            cy.get('[data-test="Trial"]').click({force: true})
            cy.get('[data-test="Fixed value"]').type('33')
            cy.get('[data-test="binEdges"]').click({force: true})
            cy.pause()
            cy.get('[data-test="histogramBinEdges"]').type("4,8,", {force: true})
            cy.get('[data-test="Create Statistic Button"]').click({force: true})


        })
    })
}