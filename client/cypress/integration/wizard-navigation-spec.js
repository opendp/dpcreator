{
    describe('Wizard Navigation tests', () => {

        beforeEach(() => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })
            cy.logout()
            cy.clearData()
            cy.login('dev_admin', 'admin')
            cy.setupStatisticsPage('datasetInfoStep600.json', 'analysisPlanStep700.json')
        })

        it('Goes to the correct wizard step', () => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })
            cy.get('h1').should('contain', 'Create the statistics')
        })

        it('Allows re-do of Wizard Steps ', () => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })
            // Go to earlier wizard step, click continue, go to my data page, continue workflow -
            // we should go back to create statistics page

            // go to Validate Dataset page
            cy.get('[data-test="step0"]').click({force: true})
            cy.get('h1').should('contain', 'Validate Dataset').should('be.visible')
            // Click continue, this will go to next step in the wizard, but will not update user step
            cy.get('[data-test="wizardContinueButton"]').last().click();
            cy.get('h1').should('contain', 'Confirm Variables').should('be.visible')

            // Go back to my data page
            cy.get('[data-test="My Data"]').click({force: true})
            // Click Continue Workflow
            cy.get('[data-test="continueWorkflow"]').click({force: true})
            // We should go back to Create Statistics step
            cy.get('h1').should('contain', 'Create the statistics').should('be.visible')
        })

    })
}