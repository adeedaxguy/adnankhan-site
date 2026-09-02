import test from 'node:test';
import assert from 'node:assert/strict';
import { zohoMessage } from '../api/integrations/growth-os-mail.js';

test('Growth OS HTML is handed to Zoho as HTML, not plain text', () => {
  assert.deepEqual(
    zohoMessage('buyer@example.com', 'Private review', '<strong>Designed review</strong>', 'html'),
    { toAddress: 'buyer@example.com', subject: 'Private review', htmlContent: '<strong>Designed review</strong>' },
  );
});
