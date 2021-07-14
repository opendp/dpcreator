{
  describe('My First Test', () => {
      it('Does not do much!', () => {
          expect(true).to.equal(true)
      })
  }),
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
        }),
        describe('Mock DV Request', () => {
            it('correctly redirects to homepage', () => {
                cy.on('uncaught:exception', (e, runnable) => {
                    console.log('error', e)
                    console.log('runnable', runnable)

                    return false
                })
                cy.login('dev_admin', 'admin')
                cy.clearData()
                cy.visit('/mock-dv')
                cy.get('#postOpenDP > .v-btn__content').click();
                cy.url().should('include', '/?id=');

            })
        })

}

