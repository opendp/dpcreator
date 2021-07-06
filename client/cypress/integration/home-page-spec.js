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
        it('shows correct error message', () => {
            cy.visit('/')
            cy.get('div')
                .should('contain', 'To create a DP Release, please make a request from a registered Dataverse installation')
        })
    }),
        describe('The Home Page', () => {
            it('correctly renders locale text', () => {
                cy.visit('/')
                cy.get('p')
                    .should('contain', 'DP Creator allows researchers to easily')
            })
        })
}