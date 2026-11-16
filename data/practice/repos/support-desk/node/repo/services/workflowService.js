// Where a ticket can go from each status. A resolved ticket can be reopened (back to in_progress) or closed;
// a closed ticket is final.
const NEXT = {
  open: ['in_progress'],
  in_progress: ['resolved', 'closed'],
  resolved: ['in_progress', 'closed'],
  closed: [],
};

const canMove = (from, to) => (NEXT[from] || []).includes(to);

module.exports = { canMove };
