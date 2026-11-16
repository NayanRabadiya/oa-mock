// More integrated tests (hidden in the test: they run when you submit).
const { fresh, order, pastReturn, evaluate, request, app } = require('./helpers');

beforeEach(fresh);

describe('MoreReturnEvaluationTests', () => {
  test('validates the request', async () => {
    order('O-1', 'C5');
    const missing = await request(app).post('/api/returns/evaluate').send({ orderId: 'O-1' });
    expect([missing.status, missing.body]).toEqual([400, { message: 'orderId, itemId and reason are required' }]);
    expect((await evaluate('O-1', 'BORED')).body).toEqual({ message: 'Invalid return reason' });
    expect((await evaluate('O-1', 'DAMAGED', { requestedAt: '15/11/2026' })).status).toBe(400);
    const noOrder = await evaluate('O-404');
    expect([noOrder.status, noOrder.body]).toEqual([404, { message: 'Order not found' }]);
    const noItem = await evaluate('O-1', 'DAMAGED', { itemId: 'I-9' });
    expect([noItem.status, noItem.body]).toEqual([404, { message: 'Item not found in order' }]);
  });

  test('rejects orders that have not been delivered', async () => {
    order('O-1', 'C5', { status: 'SHIPPED', deliveredAt: null });
    expect((await evaluate('O-1')).body).toMatchObject({ decision: 'REJECT', riskScore: 0, reasons: ['NOT_DELIVERED'] });
  });

  test('an item can have only one open return', async () => {
    order('O-1', 'C5');
    expect((await evaluate('O-1')).body.decision).toBe('AUTO_APPROVE');
    expect((await evaluate('O-1')).body).toMatchObject({ decision: 'REJECT', reasons: ['ALREADY_RETURNED'] });
    order('O-2', 'C5');
    pastReturn('C5', { orderId: 'O-2', status: 'REJECTED' });  // a rejected return doesn't block a new one
    expect((await evaluate('O-2')).body.reasons).not.toContain('ALREADY_RETURNED');
  });

  test('caps the score at 100', async () => {
    for (let i = 0; i < 5; i++) pastReturn('C9', { amount: 300, date: '2026-11-0' + (i + 2) });
    order('O-1', 'C9', { price: 800 });
    const res = await evaluate('O-1', 'NO_LONGER_NEEDED');
    expect(res.body).toMatchObject({ decision: 'REJECT', riskScore: 100 });
    expect(res.body.reasons).toEqual(['REASON_DISCRETIONARY', 'ORDER_VALUE_HIGH', 'RETURN_FREQUENCY', 'REFUND_TOTAL_HIGH', 'NEW_ACCOUNT', 'HIGH_RISK']);
  });

  test('history covers the 90 days before the request', async () => {
    pastReturn('C5', { date: '2026-08-17' });                  // 90 days before: counts
    pastReturn('C5', { date: '2026-08-16' });                  // 91 days before: doesn't
    pastReturn('C5', { date: '2026-11-20' });                  // after the request: doesn't
    order('O-1', 'C5');
    expect((await evaluate('O-1')).body).toMatchObject({ riskScore: 10, reasons: ['RETURN_FREQUENCY'] });
  });

  test('the refund total must be more than 1000', async () => {
    pastReturn('C5', { amount: 500 });
    pastReturn('C5', { amount: 500 });
    order('O-1', 'C5');
    expect((await evaluate('O-1')).body.reasons).toEqual(['RETURN_FREQUENCY']);
    pastReturn('C5', { amount: 0.01 });
    expect((await evaluate('O-1')).body.reasons).toEqual(['RETURN_FREQUENCY', 'REFUND_TOTAL_HIGH']);
  });

  test('every reason comes with its message', async () => {
    order('O-1', 'C9', { price: 75 });
    const res = await evaluate('O-1', 'NOT_AS_DESCRIBED');
    expect(res.body).toMatchObject({ decision: 'AUTO_APPROVE', riskScore: 25 });
    expect(res.body.reasons).toEqual(['REASON_NOT_AS_DESCRIBED', 'ORDER_VALUE_MODERATE', 'NEW_ACCOUNT']);
    expect(res.body.messages).toEqual(['The customer says the item is not as described', 'The return is worth 50 or more', 'The account is less than 30 days old']);
  });

  test('evaluations are recorded in the history', async () => {
    order('O-1', 'C5', { price: 45, quantity: 2 });
    order('O-2', 'C5');
    const first = await evaluate('O-1');
    expect(first.body.decision).toBe('AUTO_APPROVE');
    const list = await request(app).get('/api/returns/customer/C5');
    expect(list.body).toEqual([expect.objectContaining({ id: first.body.returnId, orderId: 'O-1', status: 'APPROVED', amount: 90, date: '2026-11-15' })]);
    expect((await evaluate('O-2')).body).toMatchObject({ riskScore: 10, reasons: ['RETURN_FREQUENCY'] });
    expect((await request(app).get('/api/returns/customer/C404')).status).toBe(404);
  });
});
