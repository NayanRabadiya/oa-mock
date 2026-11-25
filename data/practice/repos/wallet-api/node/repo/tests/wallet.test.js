const { fresh, deposit, send, wallet, history } = require('./helpers');

describe('WalletTests', () => {
  beforeEach(fresh);

  test('a deposit adds to the balance', async () => {
    const res = await deposit('W1', 250);
    expect(res.status).toBe(200);
    expect(res.body.wallet).toEqual({ id: 'W1', owner: 'Asha', balance: 1250, status: 'active' });
    expect(res.body.transaction).toEqual({ id: 'TX1', walletId: 'W1', type: 'deposit', amount: 250, balanceAfter: 1250,
      counterparty: null, at: '2026-11-15T09:00:00Z' });
  });

  test('a transfer moves money between wallets', async () => {
    const res = await send('W1', 'W2', 300);
    expect(res.status).toBe(201);
    expect(res.body).toMatchObject({ amount: 300, from: { id: 'W1', balance: 700 }, to: { id: 'W2', balance: 500 } });
    expect((await wallet('W2')).body.balance).toBe(500);
  });

  test('a failed transfer changes nothing', async () => {
    const res = await send('W1', 'W404', 300);
    expect(res.status).toBe(404);
    expect(res.body).toEqual({ message: 'Wallet not found' });
    expect((await wallet('W1')).body.balance).toBe(1000);
    expect((await history('W1')).body).toEqual([]);
  });

  test('lists a wallet\'s transactions, newest first', async () => {
    await deposit('W1', 100, '2026-11-15T08:00:00Z');
    await deposit('W1', 50, '2026-11-15T11:00:00Z');
    await deposit('W2', 70, '2026-11-15T09:00:00Z');
    const res = await history('W1');
    expect(res.status).toBe(200);
    expect(res.body.map((t) => [t.id, t.amount, t.balanceAfter])).toEqual([['TX2', 50, 1150], ['TX1', 100, 1100]]);
  });

  test('filters transactions by type', async () => {
    await deposit('W2', 100, '2026-11-15T08:00:00Z');
    await send('W2', 'W1', 50, '2026-11-15T09:00:00Z');
    await send('W1', 'W2', 20, '2026-11-15T10:00:00Z');
    const res = await history('W2', '?type=transfer_out');
    expect(res.status).toBe(200);
    expect(res.body.map((t) => [t.type, t.amount, t.counterparty])).toEqual([['transfer_out', 50, 'W1']]);
    expect((await history('W2', '?type=transfer_in')).body.map((t) => t.amount)).toEqual([20]);
  });
});
