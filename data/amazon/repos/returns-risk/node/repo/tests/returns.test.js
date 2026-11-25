// The integrated tests for the return/risk service. Run them with:  npm test
const { fresh, order, pastReturn, evaluate } = require('./helpers');

beforeEach(fresh);

describe('ReturnEvaluationTests', () => {
  test('accepts a return on the last day of the window', async () => {
    order('O-1', 'C5', { deliveredAt: '2026-10-16' });          // 30 days before 2026-11-15
    order('O-2', 'C5', { deliveredAt: '2026-10-15' });          // 31 days before
    const lastDay = await evaluate('O-1');
    expect(lastDay.status).toBe(200);
    expect(lastDay.body).toMatchObject({ decision: 'AUTO_APPROVE', riskScore: 0, reasons: [] });
    const late = await evaluate('O-2');
    expect(late.body).toMatchObject({ decision: 'REJECT', reasons: ['RETURN_WINDOW_EXPIRED'] });
  });

  test('matches categories whatever their case', async () => {
    order('O-1', 'C5', { category: 'Electronics' });
    order('O-2', 'C5', { category: 'HOME & KITCHEN' });
    order('O-3', 'C5', { category: 'Grocery' });
    expect((await evaluate('O-1')).body.decision).toBe('AUTO_APPROVE');
    expect((await evaluate('O-2')).body.decision).toBe('AUTO_APPROVE');
    expect((await evaluate('O-3')).body).toMatchObject({ decision: 'REJECT', reasons: ['NON_RETURNABLE_CATEGORY'] });
  });

  test('counts returns across every linked account', async () => {
    pastReturn('C3', { date: '2026-10-01' });                   // C3 is linked to C1 through C2
    pastReturn('C3', { date: '2026-11-02' });
    order('O-1', 'C1');
    const res = await evaluate('O-1');
    expect(res.body).toMatchObject({ decision: 'AUTO_APPROVE', riskScore: 20, reasons: ['RETURN_FREQUENCY'] });
  });

  test('only approved returns count toward the history', async () => {
    pastReturn('C5', { status: 'APPROVED' });
    pastReturn('C5', { status: 'REJECTED' });
    pastReturn('C5', { status: 'REJECTED' });
    pastReturn('C5', { status: 'PENDING_REVIEW' });
    order('O-1', 'C5');
    const res = await evaluate('O-1');
    expect(res.body).toMatchObject({ riskScore: 10, reasons: ['RETURN_FREQUENCY'] });
  });

  test('scores the value of the return as price times quantity', async () => {
    order('O-1', 'C5', { price: 120, quantity: 2 });            // 240
    order('O-2', 'C3', { price: 30, quantity: 2 });             // 60 (another customer: an approval goes into the history)
    expect((await evaluate('O-1')).body).toMatchObject({ riskScore: 15, reasons: ['ORDER_VALUE_ELEVATED'] });
    expect((await evaluate('O-2')).body).toMatchObject({ riskScore: 5, reasons: ['ORDER_VALUE_MODERATE'] });
  });

  test('decides at the score thresholds', async () => {
    pastReturn('C1', { amount: 1200 });                         // +10 history, +15 refunded over 1000
    order('O-1', 'C1', { price: 600 });                         // +25 value, +20 changed mind = 70
    const reject = await evaluate('O-1', 'CHANGED_MIND');
    expect(reject.body).toMatchObject({ decision: 'REJECT', riskScore: 70 });
    expect(reject.body.reasons).toEqual(['REASON_DISCRETIONARY', 'ORDER_VALUE_HIGH', 'RETURN_FREQUENCY', 'REFUND_TOTAL_HIGH', 'HIGH_RISK']);

    pastReturn('C5', { amount: 20 });                           // +10 history
    order('O-2', 'C5');                                         // +20 changed mind = 30
    expect((await evaluate('O-2', 'CHANGED_MIND')).body).toMatchObject({ decision: 'MANUAL_REVIEW', riskScore: 30 });

    order('O-3', 'C9', { price: 300 });                         // new account +10, +15 value = 25
    expect((await evaluate('O-3')).body).toMatchObject({ decision: 'AUTO_APPROVE', riskScore: 25 });
  });
});
