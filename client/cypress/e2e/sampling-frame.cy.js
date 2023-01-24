{
    describe('Test Sampling Frame step', () => {

        beforeEach(() => {
            cy.on("window:before:load", (win) => {
                cy.spy(win.console, "log");
                cy.spy(win.console, "error")
            })
        })

        it('Displays Sampling Page ', () => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })

            const mockDVfile = 'EyeDemoMockDV.json'
            const demoDatafile = 'EyeDemoHistogram.json'
            cy.clearData()
            cy.createMockDataset(mockDVfile)
            cy.fixture(demoDatafile).then((demoData) => {
                cy.url().should('contain', 'welcome')
                cy.get('.soft_primary.rounded-lg.mt-10.pa-16').should('contain',
                    demoData['datasetName'])
                cy.goToConfirmVariables(demoData.variables)

                // select the variables we will use
                cy.selectVariable(demoData.variables)

                // Continue to Sampling Step
                cy.epsilonStep()
                cy.get('[data-test="Larger Population - yes"]').click({force: true})

                cy.get('[data-test="populationSizeInput"]').type('45')
                cy.get('div').should('contain', 'Population size must greater than sample size')
                cy.get('[data-test="populationSizeInput"]').clear()
                cy.get('[data-test="populationSizeInput"]').type('200')
                cy.get('div').should('not.contain', 'Population size must greater than sample size')

            })
        })
    })
}