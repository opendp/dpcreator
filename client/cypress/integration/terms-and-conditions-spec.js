{
    describe('Terms and Conditions test', () => {
        it('Seeds the database', () => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)

                return false
            })
            cy.clearData()
        })
    })
}
