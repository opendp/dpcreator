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
            cy.spy(win.console, "log");
            cy.spy(win.console, "error")
            cy.clearDatasetsOnly()
            cy.login('oscar', 'oscar123!')
            let testfile = 'cypress/fixtures/Fatigue_data.csv'
            cy.uploadFile(testfile)


        })
        afterEach(() => {
            cy.logout()
        })

        it('Validates fixed value max-min', () => {
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
        it('Displays correct precision', () => {
            const demoDatafile = 'EyeDemoData.json'

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
        it('Goes back to the Confirm Variables Page', () => {
            const demoDatafile = 'EyeDemoData.json'

            cy.fixture(demoDatafile).then((demoData) => {
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
            cy.logout()
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
            cy.logout()
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
            cy.logout()
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