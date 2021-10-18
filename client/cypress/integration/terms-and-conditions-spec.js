{
    describe('Terms and Conditions test', () => {
        it('goes to My Data page after accepting terms', () => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })
            cy.clearData()
            cy.login('dev_admin', 'admin')
            cy.url().should('contain', 'terms-and-conditions')
            cy.get('[data-test="confirmTermsCheckbox"]').click({force: true});
            cy.get('[data-test="confirmTermsContinue"]').click();
            cy.url().should('contain', 'my-data')
            cy.logout()
        }),
            it('goes directly to My Data page when terms are already accepted', () => {
                cy.on('uncaught:exception', (e, runnable) => {
                    console.log('error', e)
                    console.log('runnable', runnable)
                    return false
                })
                cy.login('dev_admin', 'admin')
                cy.url().should('contain', 'my-data')

            })
    })
}
