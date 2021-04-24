{
  describe('My First Test', () => {
    it('Does not do much!', () => {
      expect(true).to.equal(true)
    })
  }),
      describe('The Home Page', () => {
        it('successfully loads', () => {
            cy.visit('/') // change URL to match your dev URL
        })
      }),
      describe('The Home Page Title', () => {
        it('successfully loads', () => {
            cy.visit('/') // change URL to match your dev URL
            cy.get('h2') // 9.
                .should('contain', 'Open')
        })
      })


}

