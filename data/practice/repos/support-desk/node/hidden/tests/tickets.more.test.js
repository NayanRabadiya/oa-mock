const { fresh, create, assign, move, list, overdue, request, app } = require('./helpers');

describe('MoreTicketTests', () => {
  beforeEach(fresh);

  test('validates the request', async () => {
    expect((await request(app).post('/api/tickets').send({ title: 'x' })).body).toEqual({ message: 'title, customer and priority are required' });
    expect((await create('critical')).body).toEqual({ message: 'Invalid priority' });
    expect((await create('low', '15/11/2026')).status).toBe(400);
    expect((await assign('T9', 'A1')).body).toEqual({ message: 'Ticket not found' });
    await create('low');
    expect((await assign('T1', 'A9')).body).toEqual({ message: 'Agent not found' });
    expect((await move('T1', 'done')).body).toEqual({ message: 'Invalid status' });
  });

  test('filters by status, priority and assignee', async () => {
    await create('low');
    await create('high');
    await create('high');
    await assign('T2', 'A1');
    expect((await list('?priority=high')).body.map((t) => t.id)).toEqual(['T2', 'T3']);
    expect((await list('?status=open')).body.map((t) => t.id)).toEqual(['T3', 'T1']);
    expect((await list('?assigneeId=A1&status=in_progress')).body.map((t) => t.id)).toEqual(['T2']);
    expect((await list('?assigneeId=A2')).body).toEqual([]);
  });

  test('resolving records when, reopening clears it', async () => {
    await create('medium');
    await move('T1', 'in_progress');
    expect((await move('T1', 'resolved', '2026-11-15T13:00:00Z')).body.resolvedAt).toBe('2026-11-15T13:00:00Z');
    const reopened = await move('T1', 'in_progress');
    expect(reopened.body).toMatchObject({ status: 'in_progress', resolvedAt: null });
    await move('T1', 'resolved');
    await move('T1', 'closed');
    expect((await move('T1', 'in_progress')).status).toBe(409);
    expect((await assign('T1', 'A1')).body).toEqual({ message: 'Only open or in-progress tickets can be assigned' });
  });

  test('finished tickets are never overdue and do not count toward an agent limit', async () => {
    await create('urgent', '2026-11-10T00:00:00Z');
    await create('urgent', '2026-11-10T00:00:00Z');
    await create('urgent', '2026-11-10T00:00:00Z');
    await assign('T1', 'A1');
    await assign('T2', 'A1');
    await move('T1', 'resolved');
    expect((await overdue('2026-11-15T09:00:00Z')).body.map((t) => t.id)).toEqual(['T2', 'T3']);
    expect((await assign('T3', 'A1')).status).toBe(200);
  });
});
