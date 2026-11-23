# OAuth Sign-in: Link Existing Users by Email

**This module trusts the OAuth providers you turn it on for.** A login from such a
provider whose verified email equals an existing user's login signs in as that user, the
first time and on every later sign-in, with no invitation and no manual linking. A user
can sign in with any number of providers and any number of accounts at each.

If you would not let a provider's account holders into the user with that email, do not
turn this on for it. Enabling an OAuth provider at all already means trusting its
sign-in; this module takes that trust to its conclusion.

## Why

Odoo's OAuth sign-in recognises a returning user by the pair _(provider, provider user
id)_ and nothing else, and stores one pair per user. A user created any other way (by
hand, imported, invited with a password) has no pair, so their first Google sign-in is
treated as a brand-new sign-up. That sign-up collides with their existing login, and the
sign-in page returns with "You do not have access to this database or your invitation
has expired." A user who has one pair cannot sign in with a second provider either.

## What it does

When a user signs in with a pair Odoo does not know yet:

1. If the pair belongs to one of a user's recorded identities, that user signs in.
2. Otherwise, if the provider has **Link Existing Users by Email** on, reports the email
   as verified (`email_verified` is true), and exactly one active user has that email as
   their login (compared without regard to case), the pair is recorded as a new identity
   of that user, whatever identities they already have, and they sign in.

Identities are kept in the user's **OAuth** tab (administrators only) and are never
replaced by one another. Odoo stores one pair on the user record: this module puts the
pair that is signing in there, so Odoo and `auth_oauth_multi_token` find the user the
way they always do. Nothing about the sign-in or the tokens changes.

It never links an inactive user, never takes a pair another user already holds, and
never creates a user. An identity, once recorded, signs in even if the provider's option
is later turned off; delete the identity to revoke it.

## Configuration

Turn on **Link Existing Users by Email** on each provider you trust (Settings → Users &
Companies → OAuth Providers). It is off by default.

## Security

Anyone who can obtain a verified address from a provider with this on can sign in as the
user with that login, including administrators. Turn it on only for providers that
verify email addresses (Google, Microsoft work accounts) and leave it off for the rest.
Apple may return a private-relay address that matches no login: those users still need
an identity added by hand or an invitation.

## With `auth_oauth_multi_token`

OCA's `auth_oauth_multi_token` keeps many simultaneous tokens per identity, and looks
the user up before this module would run. `auth_oauth_link_by_email_multi_token`
installs itself automatically when both are present and fixes the order, so the linking
and the lookup agree.

## Upgrading

Existing links keep working: each user's stored pair is recorded as an identity the next
time it signs in.

## Tests

```sh
python odoo/odoo-bin -c odoo.conf -d <testdb> -i auth_oauth_link_by_email \
  --test-enable --test-tags /auth_oauth_link_by_email --stop-after-init
```
