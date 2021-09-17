{
    describe('Confirm Variables Page', () => {

        beforeEach(() => {
            cy.on("window:before:load", (win) => {
                cy.spy(win.console, "log");
                cy.spy(win.console, "error")
            })
        })

        it('displays the variables correctly', () => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })

            cy.clearData()
            cy.createMockDataset('mockDV.json')
            // click on the start Process button on the welcome page,
            // to navigate to the Validate Dataset step of the Wizard
            cy.get('[data-test="Start Process"]').click();
            cy.url().should('contain', 'wizard')
            cy.get('[data-test="radioPrivateInformationYes"]').check({force: true})
            cy.get('[data-test="notHarmButConfidential"]').check({force: true})
            cy.get('[data-test="radioOnlyOneIndividualPerRowYes"]').check({force: true})

            // click on continue to go to trigger the profiler and go to the Confirm Variables Page
            cy.get('[data-test="wizardContinueButton"]').last().click();
            cy.get('h1').should('contain', 'Confirm Variables')

            const numericVar = {"name": "EyeHeight", min: "0", max: "100", fixedValue: "10"}
            cy.testMean(numericVar)


            // Try to create the same statistic again, it should display a duplicates validation error
            cy.get('[data-test="Add Statistic"]').click({force: true});
            cy.get('[data-test="Mean"]').click({force: true});
            cy.get('[data-test="EyeHeight"]').click({force: true})
            cy.get('[data-test="Insert fixed value"]').click({force: true})
            cy.get('[data-test="Fixed value"]').type('10')
            cy.get('[data-test="Create statistic"]').click({force: true})
            cy.get('[data-test="validation alertbox"]').should('be.visible')
            cy.get('[data-test="validation alertbox"]')
                .should('contain', 'Statistic already exists on the statistics table.')
            cy.get('[data-test="Close Dialog"]').click({force: true})

            // Try to create a Histogram, it should fail validation:
            cy.get('[data-test="Add Statistic"]').click({force: true});
            cy.get('[data-test="Histogram"]').click({force: true});
            cy.get('[data-test="EyeHeight"]').click({force: true})
            cy.get('[data-test="Insert fixed value"]').click({force: true})
            cy.get('[data-test="Fixed value"]').type('10')
            cy.get('[data-test="Create statistic"]').click({force: true})
            cy.get('[data-test="validation alertbox"]').should('be.visible')
            cy.get('[data-test="validation alertbox"]')
                .should('contain', 'histogram')

        })

    })
}