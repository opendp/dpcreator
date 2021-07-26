{
    describe('My Data Page', () => {
        it('successfully loads', () => {
            cy.on('uncaught:exception', (e, runnable) => {
                console.log('error', e)
                console.log('runnable', runnable)

                return false
            })
            cy.clearData()
            cy.visit('/mock-dv');
            cy.get('[data-test="submit button"]').click();
            cy.url().should('contains', '/?id=');
            cy.scrollTo("bottom");
            cy.get('[data-test="termsOfServiceCheckbox"]').click({force: true});

            // This get (below) is more readable, but it causes a cypress error saying that the element
            // is detachached from the DOM.  Need to investigate further, but in the meantime, use the less
            // readable get string.
            //    cy.get('[data-test="loginButton"]').click({multiple:true});
            cy.get('#account-buttons--placeholder .v-btn--is-elevated > .v-btn__content').click()
            cy.url().should('contain', 'log-in')
            // The login command triggers the creation of a dataverse file from the mockdv form
            cy.get('[data-test="username"]').type('dev_admin');
            cy.get('[data-test="password"]').type('admin');
            cy.get('[data-test="Log in"]').click();

            // first we will be routed to the Terms of Conditions page for the user
            cy.get('[data-test="confirmTermsCheckbox"]').click({force: true});
            cy.get('[data-test="confirmTermsContinue"]').click();
            // This test is necessary to prevent cypress from canceling the
            // the POST to login to  the server (right now, login redirects to the welcome page)
            cy.url().should('contain', 'welcome')

            cy.visit('/my-data')

            cy.get('tr').should('contain',
                'Replication Data for: Eye-typing experiment')
        })
    })
}