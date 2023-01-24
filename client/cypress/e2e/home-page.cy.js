{
    describe('The Home Page', () => {
        it('successfully loads', () => {
            cy.visit('/')
        })
    }),

        describe('The Home Page Title', () => {
            it('successfully loads', () => {
                cy.visit('/')
                cy.get('h2')
                    .should('contain', 'Tips for Use')
            })
        })

    describe('The Home Page', () => {
        it('correctly renders locale text', () => {
            cy.visit('/')
            cy.get('p')
                .should('contain', 'A differentially private (DP) Release includes the statistic or statistics that you have requested. ')
        })
    })
}