import test from 'node:test';
import assert from 'node:assert/strict';

import { draftLeadReply } from '../api/_lib/lead-reply.js';

const originalFetch = globalThis.fetch;
const originalKey = process.env.OPENROUTER_API_KEY;
const originalModel = process.env.LEAD_REPLY_MODEL;

test('free AI draft uses enquiry context and rejects off-topic output', async () => {
  process.env.OPENROUTER_API_KEY = 'test-key';
  delete process.env.LEAD_REPLY_MODEL;
  let requestedModel = '';
  globalThis.fetch = async (_url, options) => {
    const request = JSON.parse(options.body);
    requestedModel = request.model;
    assert.match(request.messages[1].content, /shopify/i);
    return Response.json({ choices: [{ message: { content: JSON.stringify({
      subject: 'Your Shopify store enquiry',
      body: 'Hi Sam,\n\nThanks for telling us about your Shopify checkout. Your note about mobile shoppers leaving before payment is useful context, and we can look at that journey together.\n\nWhich part of checkout seems to lose the most people? Reply here or choose a time below for a conversation.',
    }) } }] });
  };
  try {
    const lead = { name: 'Sam Rivera', message: 'Our Shopify checkout loses mobile shoppers before payment.' };
    const drafted = await draftLeadReply(lead);
    assert.equal(requestedModel, 'openrouter/free');
    assert.equal(drafted.subject, 'Your Shopify project | Lofts Studio');
    assert.match(drafted.body, /Shopify checkout/);

    globalThis.fetch = async () => Response.json({ choices: [{ message: { content: JSON.stringify({
      subject: 'Generic update about your project',
      body: 'Hi Sam,\n\nThanks for the enquiry. We would love to help and can talk more about your plans soon.\n\nPlease choose a time and we can discuss your goals, timeline, and the next steps together.',
    }) } }] });
    const fallback = await draftLeadReply(lead);
    assert.equal(fallback.subject, 'Your Shopify project | Lofts Studio');
    assert.match(fallback.body, /Shopify checkout loses mobile shoppers/);

    globalThis.fetch = async () => Response.json({ choices: [{ message: { content: JSON.stringify({
      subject: 'Your Shopify checkout enquiry',
      body: 'We need to respond as the studio and mention Shopify. The user is asking about checkout, so the reply should sound helpful.\n\nHere is the email we should write for Sam and the booking prompt.',
    }) } }] });
    const reasoningFallback = await draftLeadReply(lead);
    assert.equal(reasoningFallback.subject, 'Your Shopify project | Lofts Studio');
    assert.match(reasoningFallback.body, /^Hi Sam,/);
  } finally {
    globalThis.fetch = originalFetch;
    if (originalKey === undefined) delete process.env.OPENROUTER_API_KEY;
    else process.env.OPENROUTER_API_KEY = originalKey;
    if (originalModel === undefined) delete process.env.LEAD_REPLY_MODEL;
    else process.env.LEAD_REPLY_MODEL = originalModel;
  }
});
