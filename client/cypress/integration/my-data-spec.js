{
    describe('My Data Page', () => {
        it('successfully loads', () => {

            cy.login('dev_admin', 'admin')

            cy.visit('/my-data')
        })
    })
}