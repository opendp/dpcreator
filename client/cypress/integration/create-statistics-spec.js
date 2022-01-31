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