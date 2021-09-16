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

            // Enter min and max for EyeHeight so we can validate
            cy.get('[data-test="EyeHeight:min"]').type('0')
            cy.get('[data-test="EyeHeight:max"]').type('100')

            // Continue to Set Epsilon Step
            cy.get('[data-test="wizardContinueButton"]').last().click();
            cy.get('[data-test="Larger Population - no"]').check({force: true})
            cy.get('[data-test="Public Observations - yes"]').check({force: true})

            // Continue to Create  Statistics Step
            cy.get('[data-test="wizardContinueButton"]').last().click();

            // Test Validating EyeHeight mean
            cy.get('[data-test="Add Statistic"]').click({force: true});
            cy.get('[data-test="Mean"]').click({force: true});
            cy.get('[data-test="EyeHeight"]').click({force: true})
            cy.get('[data-test="Insert fixed value"]').click({force: true})
            cy.get('[data-test="Fixed value"]').type('10')
            cy.get('[data-test="Create statistic"]').click({force: true})

            // The statistic should have been created
            // cy.get('[data-test="statistic"]').should('contain', 'Mean')
            cy.get('tr').first().get('td').should('contain', 'Mean')
            cy.get('table').contains('td', 'Mean').should('be.visible');

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