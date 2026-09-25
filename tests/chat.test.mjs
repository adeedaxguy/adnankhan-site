import test from 'node:test';
import assert from 'node:assert/strict';

import chatHandler from '../api/chat.js';

const originalFetch = globalThis.fetch;
const originalKey = process.env.OPENROUTER_API_KEY;

test('public chat never shows free-model planning text', async () => {
  process.env.OPENROUTER_API_KEY = 'test-key';
  globalThis.fetch = async () => Response.json({ choices: [{ message: {
    content: 'We need to respond as Lofts Studio assistant and mention Shopify. The user is asking about migration. Must not include prices.\n\nWe need to ensure the final answer points to the form.',
  } }] });
  try {
    const request = new Request('https://lofts.studio/api/chat', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ messages: [{ role: 'user', content: 'Can you help migrate my Shopify store?' }] }),
    });
    const response = await chatHandler(request);
    const body = await response.json();
    assert.equal(response.status, 200);
    assert.match(body.reply, /tailored reply with a link to choose a call time/i);
    assert.doesNotMatch(body.reply, /we need to|the user is asking|must not/i);
  } finally {
    globalThis.fetch = originalFetch;
    if (originalKey === undefined) delete process.env.OPENROUTER_API_KEY;
    else process.env.OPENROUTER_API_KEY = originalKey;
  }
});
