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

        it('Updated dpStatistics Correctly', () => {
            const demoDatafile = 'EyeDemoStatsTest.json'
            cy.fixture(demoDatafile).then((demoData) => {
                cy.goToConfirmVariables(demoData.variables)
                // select the variables we will use
                cy.selectVariable(demoData.variables)
                // Continue to Set Epsilon Step
                cy.epsilonStep()
                // Add all the statistics in the Create Statistics Step
                cy.createStatistics(demoData)
            })
        })
        it('Displays Fixed Value Input Correctly', () => {
            const demoDatafile = 'EyeDemoStatsTest.json'

            cy.fixture(demoDatafile).then((demoData) => {
                cy.goToConfirmVariables(demoData.variables)
                // select the variables we will use
                let variables = {
                    "Trial": {
                        "name": "Trial",
                        "label": "",
                        "type": "Integer",
                        "min": "0",
                        "max": "10"
                    },
                }
                cy.selectVariable(variables)

                // Continue to Set Epsilon Step
                cy.epsilonStep()

                cy.get('[data-test="wizardContinueButton"]').last().click({force: true});
                cy.get('[data-test="Add Statistic"]').click({force: true});
                cy.get('[data-test="AddStatisticDialog"]').should('be.visible')
                // The fixed input field should be visible after switching from Count to Mean
                cy.get('[data-test="Count"]').click({force: true});
                cy.get('[data-test="Trial"]').click({force: true})
                cy.get('[data-test="Fixed value"]').should('not.exist')
                cy.get('[data-test="Mean"]').click({force: true});
                cy.get('[data-test="Fixed value"]').should('exist')
                cy.get('[data-test="Count"]').click({force: true});
                cy.get('[data-test="Fixed value"]').should('not.exist')

                cy.get('[data-test="Create Statistic Button"]').click({force: true})
                // The statistic should have been created
                cy.get('tr').first().get('td').should('contain', "Count")

                cy.get('[data-test="Add Statistic"]').click({force: true});
                cy.get('[data-test="AddStatisticDialog"]').should('be.visible')
                cy.get('[data-test="Mean"]').click({force: true});
                cy.get('[data-test="Fixed value"]').should('be.visible')
                cy.get('[data-test="Trial"]').click({force: true})

                // The fixed input should be required to Create the  Statistic if it's visible
                cy.get('[data-test="Create Statistic Button"]').should('be.disabled')
                cy.get('[data-test="Fixed value"]').type('5')
                cy.get('[data-test="Create Statistic Button"]').should('be.enabled')
                cy.get('[data-test="Create Statistic Button"]').click({force: true})
                // The statistic should have been created
                cy.get('tr').first().get('td').should('contain', "Mean")


            })
        })


    })
}