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
    describe('The Home Page', () => {
        it('correctly renders hamburger menu', () => {
            cy.clearData()
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)

                return false
            })
            const username = 'oscar'
            const email = 'oscar@thegrouch.com'
            const password = 'oscar123!'
            cy.createAccount(username, email, password)
            cy.viewport('ipad-mini')

            cy.visit('/')
            cy.get('[data-test="menuIcon"]').should('be.visible')
            cy.get('[data-test="menuIcon"]').click({force: true})
            cy.get('[data-test="mobileMenu"]').should('be.visible')
            cy.get('[data-test="mobileMenu"]').should('include.text', 'My Analysis Plans')

               })
    })
}