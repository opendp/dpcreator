{
    describe('Create Statistics Wizard Step tests', () => {
        before(() => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })
            cy.clearData()
            cy.createAccount('oscar', 'oscar@sesame.com', 'oscar123!')
            cy.logout()

        })
        beforeEach(() => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })
            cy.clearDatasetsOnly()
            cy.login('oscar', 'oscar123!')
            let testfile = 'cypress/fixtures/Fatigue_data.csv'
            cy.uploadFile(testfile)


        })
        afterEach(() => {
            cy.logout()
        })
        it('Saves Histogram Options Correctly', () => {
            const demoDatafile = 'EyeDemoStatsTest.json'
            cy.fixture(demoDatafile).then((demoData) => {
                cy.goToConfirmVariables(demoData.variables)
                // select the variables we will use
                cy.selectVariable(demoData.variables)
                // Continue to Set Epsilon Step
                cy.epsilonStep()
                //go to Create Statistics Step
                cy.get('[data-test="wizardContinueButton"]').last().click({force: true});
                cy.get('h1').should('contain', 'Create Statistics').should('be.visible')

                // Add all a Histogram  statistic  and  test the options
                cy.get('[data-test="Add Statistic"]').click({force: true});
                cy.get('[data-test="AddStatisticDialog"]').should('be.visible')

                cy.get('[data-test="Histogram"]').click({force: true});
                const varDataTest = '[data-test="Trial"]'
                cy.get(varDataTest).click({force: true})
                cy.get('[data-test="Fixed value"]').type('5')
                cy.get('[data-test="onePerValue"]').click({force: true})
                cy.get('[data-test="Create Statistic Button"]').should('be.enabled')
                cy.get('[data-test="equalRanges"]').click({force: true})
                cy.get('[data-test="histogramNumberOfBins"]').type('11')
                cy.get('div').should('contain', 'Value must').should('be.visible')

                cy.get('[data-test="histogramNumberOfBins"]').clear().type('3')
                cy.get('div').should('contain', 'Equal range bins: [0, 4],[5, 10],uncategorized')
                cy.get('[data-test="Create Statistic Button"]').click({force: true})
                cy.get('tr').first().get('td').should('contain', "Histogram")

            })
        })
        it('Validates Correctly after epsilon changes', () => {
            const demoDatafile = 'EyeDemoStatsTest.json'

            cy.fixture(demoDatafile).then((demoData) => {
                cy.goToConfirmVariables(demoData.variables)
                // select the variables we will use
                cy.selectVariable(demoData.variables)

                // Continue to Set Epsilon Step
                cy.epsilonStep()
                const statsData = {
                    "datasetName": "Eye-typing experiment",
                    "statistics": [
                        {
                            "statistic": "Mean",
                            "variable": "Trial",
                            "fixedValue": "3",
                            "roundedAccuracy": "0.164"
                        }
                    ]
                }
                const newAccuracy = "1.64"
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


    })
}