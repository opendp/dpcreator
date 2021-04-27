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
                .should('contain', 'To create a DP Release, please make a request from an registered Dataverse installation')
        })
    })

}

