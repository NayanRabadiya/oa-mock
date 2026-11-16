const { fresh, borrow, giveBack, available } = require('./helpers');

describe('LoanTests', () => {
  beforeEach(fresh);

  test('borrowing and returning a book changes the copies on the shelf', async () => {
    expect(await available('B1')).toBe(2);
    const res = await borrow('M1', 'B1');
    expect(res.status).toBe(201);
    expect(res.body).toMatchObject({ memberId: 'M1', bookId: 'B1', borrowedAt: '2026-11-01', returnedAt: null });
    expect(await available('B1')).toBe(1);
    expect((await giveBack(res.body.id, '2026-11-10')).status).toBe(200);
    expect(await available('B1')).toBe(2);
  });

  test('a member can have at most 3 books out', async () => {
    for (const book of ['B1', 'B2', 'B3']) {
      expect((await borrow('M1', book)).status).toBe(201);
    }
    const fourth = await borrow('M1', 'B3');
    expect(fourth.status).toBe(409);
    expect(fourth.body).toEqual({ message: 'Loan limit reached' });
    expect((await borrow('M2', 'B3')).status).toBe(201);
  });

  test('late fees start after the 14-day loan period', async () => {
    const onTime = (await borrow('M1', 'B1', '2026-11-01')).body;
    expect((await giveBack(onTime.id, '2026-11-15')).body).toMatchObject({ daysLate: 0, fee: 0 });   // day 14: on time
    const late = (await borrow('M1', 'B1', '2026-11-01')).body;
    expect((await giveBack(late.id, '2026-11-18')).body).toMatchObject({ daysLate: 3, fee: 30 });
  });

  test('a loan can be returned only once', async () => {
    const loan = (await borrow('M1', 'B1')).body;
    expect((await giveBack(loan.id, '2026-11-05')).status).toBe(200);
    const again = await giveBack(loan.id, '2026-11-06');
    expect(again.status).toBe(409);
    expect(again.body).toEqual({ message: 'Loan already returned' });
  });
});
