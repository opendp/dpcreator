{
    describe('Dataverse Handoff mock-dv test', () => {
        it('Displays correct file on Welcome Page', () => {
            cy.visit('http://localhost:8000/mock-dv');
            cy.get('#postOpenDP > .v-btn__content').click();
            cy.url().should('contains', 'http://localhost:8000/');
            cy.get('.v-input--selection-controls__ripple').click();
            cy.get('#account-buttons--placeholder .v-btn--is-elevated > .v-btn__content').click();
            cy.url().should('contain', 'log-in')
            cy.get('#input-65').click();
            cy.get('#input-65').type('dev_admin');
            cy.get('#input-68').click();
            cy.get('#input-68').type('admin');
            cy.get('.v-btn--is-elevated > .v-btn__content').click();
            cy.get('.soft_primary.rounded-lg.mt-10.pa-16').should('contain',
                ' doi:10.7910/DVN/PUXVDH | Replication Data for: Eye-typing experiment | Fatigue_data.tab ')
        })
    })
}