# OAuth Sign-in: Link by Email with Multiple Tokens

Glue between [`auth_oauth_link_by_email`](../auth_oauth_link_by_email/README.md) and
OCA's `auth_oauth_multi_token`. It installs itself when both are installed and changes
nothing you configure.

`auth_oauth_multi_token` overrides the OAuth sign-in to look the user up by provider and
user id **before** it calls the rest of the chain, and refuses the sign-in when that
lookup is empty. Odoo loads modules by dependency depth and then by name, so
`auth_oauth_link_by_email` would run inside that override, after the lookup. This module
depends on both, loads after them, and runs the link first.

## Tests

```sh
python odoo/odoo-bin -c odoo.conf -d <testdb> -i auth_oauth_link_by_email_multi_token \
  --test-enable --test-tags /auth_oauth_link_by_email_multi_token --stop-after-init
```
