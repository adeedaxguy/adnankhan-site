import test from 'node:test';
import assert from 'node:assert/strict';
import { DAILY_NEW_LIMIT, zohoMessage } from '../api/integrations/growth-os-mail.js';
import { zohoPostRequest } from '../api/_lib/zoho.js';

test('Growth OS bridge matches the five 20-recipient Lofts lanes', () => {
  assert.equal(DAILY_NEW_LIMIT, 100);
});

test('Growth OS HTML is handed to Zoho as HTML, not plain text', () => {
  assert.deepEqual(
    zohoMessage('buyer@example.com', 'Private review', '<strong>Designed review</strong>', 'html'),
    { toAddress: 'buyer@example.com', subject: 'Private review', htmlContent: '<strong>Designed review</strong>' },
  );
});

test('Growth OS follow-up is sent as a reply to the original Zoho message', () => {
  const message = zohoMessage('buyer@example.com', 'Re: Private review', '<strong>Follow-up</strong>', 'html', 'provider-root-123');
  const request = zohoPostRequest({ accountId: 'account-1', fromEmail: 'hi@lofts.studio', dataCenter: 'us' }, { ...message, content: message.htmlContent, mailFormat: 'html' });
  assert.equal(request.url, 'https://mail.zoho.com/api/accounts/account-1/messages/provider-root-123');
  assert.equal(request.body.action, 'reply');
});
