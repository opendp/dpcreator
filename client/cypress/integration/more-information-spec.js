{
    describe('Validate More Information Page', () => {
        it('successfully displays Text sections', () => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)
                return false
            })
            cy.visit('more-information')
            cy.get('h2').should('contain', 'DP Creator Concepts')
            cy.get('h2').should('contain', 'What is a registered Dataverse?')
            cy.get('h2').should('contain', 'What is epsilon')
            cy.get('h2').should('contain', 'What is delta')

        })
    })
}