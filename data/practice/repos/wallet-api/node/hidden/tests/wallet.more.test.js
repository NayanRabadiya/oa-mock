const { fresh, deposit, withdraw, send, wallet, history, request, app } = require('./helpers');

describe('MoreWalletTests', () => {
  beforeEach(fresh);

  test('validates amounts and wallets', async () => {
    expect((await deposit('W1', 0)).body).toEqual({ message: 'amount must be a positive whole number' });
    expect((await deposit('W1', 2.5)).status).toBe(400);
    expect((await deposit('W1', '10')).status).toBe(400);
    expect((await deposit('W9', 10)).body).toEqual({ message: 'Wallet not found' });
    expect((await wallet('W9')).status).toBe(404);
    expect((await request(app).post('/api/transfers').send({ from: 'W1' })).body).toEqual({ message: 'from, to and amount are required' });
    expect((await send('W1', 'W1', 10)).body).toEqual({ message: 'Cannot transfer to the same wallet' });
    expect((await history('W1', '?type=refund')).body).toEqual({ message: 'Invalid transaction type' });
    expect((await history('W1', '?limit=0')).status).toBe(400);
  });

  test('cannot spend more than the balance', async () => {
    expect((await withdraw('W2', 201)).body).toEqual({ message: 'Insufficient funds' });
    expect((await send('W2', 'W1', 201)).status).toBe(409);
    const all = await withdraw('W2', 200);
    expect(all.body.wallet.balance).toBe(0);
    expect(all.body.transaction).toMatchObject({ type: 'withdrawal', amount: 200, balanceAfter: 0 });
  });

  test('frozen wallets cannot send or receive', async () => {
    expect((await send('W3', 'W1', 10)).body).toEqual({ message: 'Wallet is frozen' });
    expect((await send('W1', 'W3', 10)).status).toBe(409);
    expect((await deposit('W3', 10)).status).toBe(409);
    expect((await wallet('W1')).body.balance).toBe(1000);
    expect((await wallet('W3')).body.balance).toBe(500);
  });

  test('limit caps the transaction list', async () => {
    for (let i = 1; i <= 25; i++) await deposit('W1', i, `2026-11-15T09:${String(i).padStart(2, '0')}:00Z`);
    expect((await history('W1')).body.length).toBe(20);
    expect((await history('W1', '?limit=2')).body.map((t) => t.amount)).toEqual([25, 24]);
    expect((await history('W1', '?type=deposit&limit=3')).body.map((t) => t.amount)).toEqual([25, 24, 23]);
  });
});
