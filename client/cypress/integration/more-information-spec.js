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
            cy.get('h2').should('contain', 'More Information on Epsilon')
            cy.get('h2').should('contain', 'More Information on Delta')
            cy.get('h2').should('contain', 'More Information on Confidence Level')

        })
    })
}