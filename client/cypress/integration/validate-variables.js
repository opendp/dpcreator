{
    describe('Confirm Variables Validation tests', () => {
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
            cy.login('oscar', 'oscar123!')
            cy.setupConfirmVariablesPage('datasetInfoStep400.json')

        })
        it('Uses fixtures on confirm Variables page', () => {

            cy.get('h1').should('contain', 'Confirm Variables')

        })
        /*
                it ('displays variables correctly',()=>{


                    cy.fixture('variables').then((varsFixture) => {

                        for (const key in varsFixture) {
                            cy.get('table').contains('td', varsFixture[key].name).should('be.visible')
                            cy.get('table').contains('tr', varsFixture[key].name).should('contain', varsFixture[key].type)
                        }
                    })
             })

         */
        it(' validates type integer', () => {

            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })
            const label = 'Trial'
            const minInput = label + ':min'
            const maxInput = label + ':max'
            //  selecting a numeric variable with min/max - test continue button
            cy.get('[data-test="wizardContinueButton"]').should('be.disabled')
            cy.contains('td', label).parent('tr').children().first().click()
            cy.get('[data-test="' + minInput + '"]').type('0');
            cy.get('[data-test="' + maxInput + '"]').type('100');
            cy.get('[data-test="' + maxInput + '"]').should('have.value', 100)
            cy.get('[data-test="' + maxInput + '"]').trigger('change')
            cy.get('[data-test="wizardContinueButton"]').should('not.be.disabled')


        })
        it(' validates type boolean', () => {

            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })
            const booleanLabel = 'Session'

            // Select boolean variable without additional information - continueButton should be disabled
            cy.contains('td', booleanLabel).parent('tr').children().first().click()
            cy.get('[data-test="wizardContinueButton"]').should('be.disabled')


        })


    })
}