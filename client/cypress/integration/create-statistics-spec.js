{
    describe('Create Statistics Wizard Step tests', () => {

        beforeEach(() => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })
            cy.clearData()

        })
        it('Displays Fixed Value Input Correctly', () => {
            const mockDVfile = 'EyeDemoMockDV.json'
            const demoDatafile = 'EyeDemoStatsTest.json'

            cy.createMockDataset(mockDVfile)
            cy.fixture(demoDatafile).then((demoData) => {
                cy.url().should('contain', 'welcome')
                cy.get('.soft_primary.rounded-lg.mt-10.pa-16').should('contain',
                    demoData['datasetName'])
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
                const varDataTest = '[data-test="Trial"]'
                cy.get(varDataTest).click({force: true})
                cy.get('[data-test="Fixed value"]').should('not.exist')
                cy.get('[data-test="Mean"]').click({force: true});
                cy.get('[data-test="Fixed value"]').should('be.visible')
                // The fixed input should be required to Create the  Statistic if it's visible
                cy.get('[data-test="Create Statistic Button"]').should('be.disabled')
                cy.get('[data-test="Fixed value"]').type('5')
                cy.get('[data-test="Create Statistic Button"]').should('be.enabled')
                cy.get('[data-test="Create Statistic Button"]').click({force: true})
                // The statistic should have been created
                cy.get('tr').first().get('td').should('contain', "Mean")


            })
        })

        it('Validates fixed value max-min', () => {
            const mockDVfile = 'EyeDemoMockDV.json'
            const demoDatafile = 'EyeDemoStatsTest.json'

            cy.createMockDataset(mockDVfile)
            cy.fixture(demoDatafile).then((demoData) => {
                cy.url().should('contain', 'welcome')
                cy.get('.soft_primary.rounded-lg.mt-10.pa-16').should('contain',
                    demoData['datasetName'])
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

                // cy.createStatistics(statsData)
                cy.get('[data-test="wizardContinueButton"]').last().click({force: true});
                cy.get('[data-test="Add Statistic"]').click({force: true});
                cy.get('[data-test="AddStatisticDialog"]').should('be.visible')

                cy.get('[data-test="Histogram"]').click({force: true});
                const varDataTest = '[data-test="Trial"]'
                cy.get(varDataTest).click({force: true})
                cy.get('[data-test="Fixed value"]').type((Number(variables.Trial.max) + 1))
                cy.get('div').should('contain', 'Value must be between')
                cy.get('[data-test="Fixed value"]').clear()
                cy.get('[data-test="Fixed value"]').type((Number(variables.Trial.max) - 1))
                cy.get('div').should('not.contain', 'Value must be between')


            })
        })

        it('Validates Correctly after epsilon changes', () => {
            const mockDVfile = 'EyeDemoMockDV.json'
            const demoDatafile = 'EyeDemoStatsTest.json'

            cy.createMockDataset(mockDVfile)
            cy.fixture(demoDatafile).then((demoData) => {
                cy.url().should('contain', 'welcome')
                cy.get('.soft_primary.rounded-lg.mt-10.pa-16').should('contain',
                    demoData['datasetName'])
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
                cy.wait(1000)
                cy.get('[data-test=editParamsSave]').click();
                cy.get('table').contains('td', newAccuracy).should('be.visible')
                cy.get('tr').first().get('td').should('contain', statsData.statistics[0].statistic)
                cy.get('table').contains('td', statsData.statistics[0].statistic).should('be.visible');

                cy.get('[data-test=editConfidenceIcon]').click();
                cy.get('[data-test="confirmButton"] > .v-btn__content').click();
                cy.get('[data-test=editEpsilonInput]').click();
                cy.get('[data-test=editEpsilonInput]').clear()
                cy.get('[data-test=editEpsilonInput]').type('1');
                cy.wait(1000)
                cy.get('[data-test=editParamsSave]').click();
                cy.get('table').contains('td', statsData.statistics[0].roundedAccuracy).should('be.visible')

            })
        })
        it('Updated dpStatistics Correctly', () => {
            const mockDVfile = 'EyeDemoMockDV.json'
            const demoDatafile = 'EyeDemoStatsTest.json'
            cy.createMockDataset(mockDVfile)
            cy.fixture(demoDatafile).then((demoData) => {
                cy.url().should('contain', 'welcome')
                cy.get('.soft_primary.rounded-lg.mt-10.pa-16').should('contain',
                    demoData['datasetName'])
                cy.goToConfirmVariables(demoData.variables)
                // select the variables we will use
                cy.selectVariable(demoData.variables)
                // Continue to Set Epsilon Step
                cy.epsilonStep()
                // Add all the statistics in the Create Statistics Step
                cy.createStatistics(demoData)
            })
        })

        it('Displays correct precision', () => {
            const mockDVfile = 'EyeDemoMockDV.json'
            const demoDatafile = 'EyeDemoData.json'

            cy.createMockDataset(mockDVfile)
            cy.fixture(demoDatafile).then((demoData) => {
                cy.url().should('contain', 'welcome')
                cy.get('.soft_primary.rounded-lg.mt-10.pa-16').should('contain',
                    demoData['datasetName'])
                cy.goToConfirmVariables(demoData.variables)
                // select the variables we will use
                cy.selectVariable(demoData.variables)

                // Continue to Set Epsilon Step
                cy.epsilonStep()
                // Add all the statistics in the Create Statistics Step
                cy.createStatistics(demoData)
            })
        })
        it('Goes back to the Confirm Variables Page', () => {
            const mockDVfile = 'EyeDemoMockDV.json'
            const demoDatafile = 'EyeDemoData.json'

            cy.createMockDataset(mockDVfile)
            cy.fixture(demoDatafile).then((demoData) => {
                cy.url().should('contain', 'welcome')
                cy.get('.soft_primary.rounded-lg.mt-10.pa-16').should('contain',
                    demoData['datasetName'])
                cy.goToConfirmVariables(demoData.variables)
                // select the variables we will use
                cy.selectVariable(demoData.variables)

                // Continue to Set Epsilon Step
                cy.epsilonStep()
                // Add all the statistics in the Create Statistics Step
                cy.createStatistics(demoData)
                cy.get('[data-test="Add Statistic"]').should('be.visible')
                cy.get('[data-test="Add Statistic"]').click({force: true});
                cy.get('[data-test="confirmVariablesLink"]').click({force: true});
                cy.get('h1').should('contain', 'Confirm Variables').should('be.visible')
                cy.contains('td', demoData.variables[demoData.statistics[0].variable].name).parent('tr').children()
                    .first().children().get(":has(.v-simple-checkbox--disabled)").should('be.visible')


            })
        })
        it('Populates Edit Noise Param Dialog', () => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })
            cy.login('dev_admin', 'admin')
            cy.setupStatisticsPage('datasetInfoStep600.json', 'analysisPlanStep700.json')
            cy.get('h1').should('contain', 'Create Statistics')
            cy.get('[data-test="editConfidenceIcon"]').click({force: true});
            cy.get('h2').should('contain', 'Are you sure you want to proceed?').should('be.visible')
            cy.get('[data-test="confirmButton"]').click({force: true});

            cy.get('[data-test="editEpsilonInput"]').should('have.value', 1)
            cy.get('[data-test="editParamsCancel"]').click({force: true});

        })


        it('Goes to the correct wizard step', () => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })
            cy.login('dev_admin', 'admin')
            cy.setupStatisticsPage('datasetInfoStep600.json', 'analysisPlanStep700.json')
            cy.get('h1').should('contain', 'Create Statistics')
        })


        it('Contains correct variables in the Add Statistics dialog ', () => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })
            cy.login('dev_admin', 'admin')
            cy.setupStatisticsPage('datasetInfoStep600.json', 'analysisPlanStep700.json')
            cy.fixture('analysisPlanStep700').then((analysisFixture) => {
                // Create your statistic
                cy.get('[data-test="Add Statistic"]').click({force: true});
                for (const key in analysisFixture.variableInfo) {
                    if (analysisFixture.variableInfo[key].selected) {
                        cy.get('label').should('contain', analysisFixture.variableInfo[key].name)
                    } else {
                        cy.get('label').should('not.contain', analysisFixture.variableInfo[key].name)
                    }
                }
                cy.get('[data-test="Mean"]').click({force: true});
                for (const key in analysisFixture.variableInfo) {
                    if (!analysisFixture.variableInfo[key].selected ||
                        (analysisFixture.variableInfo[key].type !== 'Integer' &&
                            analysisFixture.variableInfo[key].type !== 'Float')) {
                        cy.get('label').should('not.contain', analysisFixture.variableInfo[key].name)
                    }
                }
                cy.get('[data-test="Add Statistic Close"]').click({force: true})
            })

        })

    })
}