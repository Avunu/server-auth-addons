# OAuth Sign-in: Link Existing Users by Email

Odoo's OAuth sign-in recognises a returning user by the pair _(provider, provider user
id)_ and nothing else. A user who was created any other way (by hand, imported, invited
with a password) has neither, so their first Google sign-in is treated as a brand-new
sign-up. That sign-up collides with their existing login, and the sign-in page returns
with "You do not have access to this database or your invitation has expired."

This module fixes that for providers you choose. On a first sign-in it looks for the one
active user whose **login equals the email the provider returns**, stores the provider
and user id on that user, and signs them in. Every later sign-in takes Odoo's normal
path.

## Configuration

Turn on **Link Existing Users by Email** on the provider (Settings → Users & Companies →
OAuth Providers). It is off by default.

## What it links, and what it never does

A user is linked only when all of these hold:

- the provider has the option on;
- the provider reports the email as verified (`email_verified` is true);
- exactly one active user has that login (compared without regard to case);
- that user has no OAuth identity yet, for any provider;
- no user already holds the provider's user id.

It never replaces an existing link, never links an inactive user, and never creates a
user.

## Security

Linking by email trusts the provider's claim that the address belongs to the person
signing in. Anyone who can obtain a verified address from the provider can sign in as
the user with that login. Turn the option on only for providers that verify email
addresses (Google does) and leave it off for the rest. Apple may return a private-relay
address that matches no login: those users still need to be linked by hand or by an
invitation.

## With `auth_oauth_multi_token`

OCA's `auth_oauth_multi_token` looks the user up before this module runs, so the link
would come too late. `auth_oauth_link_by_email_multi_token` installs itself
automatically when both are present and fixes the order.

## Tests

```sh
python odoo/odoo-bin -c odoo.conf -d <testdb> -i auth_oauth_link_by_email \
  --test-enable --test-tags /auth_oauth_link_by_email --stop-after-init
```
