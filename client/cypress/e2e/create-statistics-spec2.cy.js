{
    describe('Create Statistics Wizard Step tests', () => {
        before(() => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })
            cy.clearData()

        })
        beforeEach(() => {
         cy.loadTeacherSurveyDemo()
        })
        afterEach(() => {
            cy.logout()
        })
        it('Saves Histogram Options Correctly', () => {


            cy.get('h1').should('contain', 'Create Statistics').should('be.visible')

                // Add all a Histogram  statistic  and  test the options
                cy.get('[data-test="Add Statistic"]').click({force: true});
                cy.get('[data-test="AddStatisticDialog"]').should('be.visible')

                cy.get('[data-test="Histogram"]').click({force: true});
            const varDataTest = '[data-test="age"]'
            cy.get(varDataTest).click({force: true})
            cy.get('[data-test="Fixed value"]').type('35')
            cy.get('[data-test="onePerValue"]').click({force: true})
                cy.get('[data-test="Create Statistic Button"]').should('be.enabled')
            cy.get('[data-test="equalRanges"]').click({force: true})
            cy.get('[data-test="histogramNumberOfBins"]').type('110')
            cy.get('div').should('contain', 'Value must').should('be.visible')

            cy.get('[data-test="histogramNumberOfBins"]').clear().type('3')
            cy.get('div').should('contain', 'Equal range bins: [20, 47],[48, 75],uncategorized')
            cy.get('[data-test="Create Statistic Button"]').click({force: true})
                cy.get('tr').first().get('td').should('contain', "Histogram")


        })
        it('Validates Correctly after epsilon changes', () => {

                const statsData = {
                    "datasetName": "Teacher Survey",
                    "statistics": [
                        {
                            "statistic": "Mean",
                            "variable": "age",
                            "fixedValue": "35",
                            "roundedAccuracy": "0.0235"
                        }
                    ]
                }
            const newAccuracy = ".235"
                cy.createStatistics(statsData)
                cy.get('tr').first().get('td').should('contain', statsData.statistics[0].statistic)
                cy.get('table').contains('td', statsData.statistics[0].statistic).should('be.visible');

                const epsilonInput = '[data-test="editEpsilonInput"]'
                cy.get('[data-test=editConfidenceIcon]').click();
                cy.get('[data-test="confirmButton"] > .v-btn__content').click();
                cy.get('[data-test=editEpsilonInput]').click();
                cy.get('[data-test=editEpsilonInput]').clear()
                cy.get('[data-test=editEpsilonInput]').type('.1');
                cy.get('[data-test=editParamsSave]').click();
                cy.get('table').contains('td', newAccuracy).should('be.visible')
                cy.get('tr').first().get('td').should('contain', statsData.statistics[0].statistic)
                cy.get('table').contains('td', statsData.statistics[0].statistic).should('be.visible');

                cy.get('[data-test=editConfidenceIcon]').click();
                cy.get('[data-test="confirmButton"] > .v-btn__content').click();
                cy.get('[data-test=editEpsilonInput]').click();
                cy.get('[data-test=editEpsilonInput]').clear()
                cy.get('[data-test=editEpsilonInput]').type('1');
                cy.get('[data-test=editParamsSave]').click();
                cy.get('table').contains('td', statsData.statistics[0].roundedAccuracy).should('be.visible')


        })


    })
}