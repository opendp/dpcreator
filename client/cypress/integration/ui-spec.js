{
  describe('My First Test', () => {
      it('Does not do much!', () => {
          expect(true).to.equal(true)
      })
  }),

        describe('Mock DV Request', () => {
            it('correctly redirects to homepage', () => {
                cy.visit('/mock-dv')
                cy.get('#postOpenDP > .v-btn__content').click();
                cy.url().should('include', '/?id=');

            })
        })

}

