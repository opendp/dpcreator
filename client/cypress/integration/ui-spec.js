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

