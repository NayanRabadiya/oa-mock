const { fresh, borrow, giveBack, request, app } = require('./helpers');

describe('MoreLoanTests', () => {
  beforeEach(fresh);

  test('validates the request', async () => {
    expect((await request(app).post('/api/loans').send({ memberId: 'M1' })).body).toEqual({ message: 'memberId and bookId are required' });
    expect((await borrow('M9', 'B1')).status).toBe(404);
    expect((await borrow('M1', 'B9')).body).toEqual({ message: 'Book not found' });
    expect((await borrow('M1', 'B1', '1/11/2026')).status).toBe(400);
    expect((await giveBack('L99', '2026-11-05')).body).toEqual({ message: 'Loan not found' });
  });

  test('a book with every copy out cannot be borrowed', async () => {
    expect((await borrow('M1', 'B2')).status).toBe(201);
    const none = await borrow('M2', 'B2');
    expect(none.status).toBe(409);
    expect(none.body).toEqual({ message: 'No copies available' });
  });

  test('the fee for one loan is at most 200', async () => {
    const loan = (await borrow('M1', 'B1', '2026-10-01')).body;
    expect((await giveBack(loan.id, '2026-11-15')).body).toMatchObject({ daysLate: 31, fee: 200 });
  });
});
