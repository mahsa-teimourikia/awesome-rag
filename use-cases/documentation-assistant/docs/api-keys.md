# API keys

Create keys in the Acme Console under Settings, then copy the secret once because it is not shown again. To rotate a key, create a replacement, deploy it, verify traffic, and revoke the old key. Never paste an API key into a support ticket or commit it to source control.

The rotation sequence is create, deploy, verify, and revoke. A safe assistant should explain the sequence but should not perform the revocation itself.
