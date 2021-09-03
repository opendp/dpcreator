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
                    .should('contain', 'Open')
            })
        })

        describe('The Home Page', () => {
            it('correctly renders locale text', () => {
                cy.visit('/')
                cy.get('p')
                    .should('contain', 'DP Creator is a tool for use with')
            })
        })
}