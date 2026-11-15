// A Jest reporter that writes a JUnit XML report to $OA_JUNIT_OUT, so the OA Mock app can show a result per
// test (like HackerRank's JUnit-based scoring). Test ids are "<describe titles> . <test title>".
const fs = require('fs');
const path = require('path');

const esc = (s) => String(s).replace(/[<>&"']/g, (c) => ({ '<': '&lt;', '>': '&gt;', '&': '&amp;', '"': '&quot;', "'": '&apos;' }[c]))
  // characters XML 1.0 can't hold (Jest colours its messages)
  .replace(/\u001b\[[0-9;]*m/g, '').replace(/[\u0000-\u0008\u000b\u000c\u000e-\u001f]/g, '');

class JUnitReporter {
  constructor(globalConfig, options) { this.out = (options && options.out) || process.env.OA_JUNIT_OUT; }

  onRunComplete(contexts, results) {
    if (!this.out) return;
    const cases = [];
    for (const file of results.testResults) {
      const rel = path.relative(process.cwd(), file.testFilePath).split(path.sep).join('/');
      if (file.testExecError || (file.failureMessage && !file.testResults.length)) {
        cases.push({ cls: rel, name: '(file did not run)', status: 'error', time: 0,
          msg: (file.testExecError && (file.testExecError.stack || file.testExecError.message)) || file.failureMessage });
      }
      for (const t of file.testResults) {
        cases.push({ cls: t.ancestorTitles.join(' › ') || rel, name: t.title, time: (t.duration || 0) / 1000,
          status: t.status === 'passed' ? 'passed' : t.status === 'pending' || t.status === 'skipped' || t.status === 'todo' ? 'skipped' : 'failed',
          msg: (t.failureMessages || []).join('\n') });
      }
    }
    const xml = ['<?xml version="1.0" encoding="UTF-8"?>',
      `<testsuite name="jest" tests="${cases.length}" failures="${cases.filter((c) => c.status === 'failed').length}" errors="${cases.filter((c) => c.status === 'error').length}">`];
    for (const c of cases) {
      xml.push(`  <testcase classname="${esc(c.cls)}" name="${esc(c.name)}" time="${c.time.toFixed(3)}">`);
      if (c.status !== 'passed') {
        const tag = { failed: 'failure', error: 'error', skipped: 'skipped' }[c.status];
        const first = esc((c.msg || '').split('\n').find((l) => l.trim()) || '');
        xml.push(`    <${tag} message="${first.slice(0, 500)}">${esc(c.msg || '')}</${tag}>`);
      }
      xml.push('  </testcase>');
    }
    xml.push('</testsuite>');
    fs.mkdirSync(path.dirname(this.out), { recursive: true });
    fs.writeFileSync(this.out, xml.join('\n') + '\n');
  }
}

module.exports = JUnitReporter;
