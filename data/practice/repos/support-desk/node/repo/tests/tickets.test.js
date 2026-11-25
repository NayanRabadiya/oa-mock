const { fresh, create, assign, move, list, overdue } = require('./helpers');

describe('TicketTests', () => {
  beforeEach(fresh);

  test('creating a ticket opens it', async () => {
    const res = await create('high');
    expect(res.status).toBe(201);
    expect(res.body).toEqual({ id: 'T1', title: 'Help', customer: 'acme', priority: 'high', status: 'open',
      assigneeId: null, createdAt: '2026-11-15T09:00:00Z', resolvedAt: null });
  });

  test('tickets are listed by priority, oldest first', async () => {
    await create('low', '2026-11-15T08:00:00Z');
    await create('high', '2026-11-15T10:00:00Z');
    await create('urgent', '2026-11-15T11:00:00Z');
    await create('high', '2026-11-15T09:00:00Z');
    const res = await list();
    expect(res.body.map((t) => t.id)).toEqual(['T3', 'T4', 'T2', 'T1']);
  });

  test('an agent cannot take more tickets than their limit', async () => {
    for (let i = 0; i < 3; i++) await create('medium');
    expect((await assign('T1', 'A1')).body.status).toBe('in_progress');
    expect((await assign('T2', 'A1')).status).toBe(200);
    const third = await assign('T3', 'A1');
    expect(third.status).toBe(409);
    expect(third.body).toEqual({ message: 'Agent has too many open tickets' });
    expect((await assign('T3', 'A2')).status).toBe(200);
  });

  test('tickets move through the workflow in order', async () => {
    await create('low');
    expect((await move('T1', 'resolved')).status).toBe(409);
    expect((await move('T1', 'in_progress')).status).toBe(200);
    const closeEarly = await move('T1', 'closed');
    expect(closeEarly.status).toBe(409);
    expect(closeEarly.body).toEqual({ message: 'Cannot move a ticket from in_progress to closed' });
    expect((await move('T1', 'resolved')).status).toBe(200);
    expect((await move('T1', 'closed')).body.status).toBe('closed');
  });

  test('a ticket is overdue only after its SLA', async () => {
    await create('high', '2026-11-14T10:00:00Z');   // 23 hours before the check
    await create('high', '2026-11-14T08:00:00Z');   // 25 hours before
    await create('urgent', '2026-11-15T05:30:00Z'); // 3.5 hours before
    const res = await overdue('2026-11-15T09:00:00Z');
    expect(res.status).toBe(200);
    expect(res.body.map((t) => t.id)).toEqual(['T2']);
  });
});
