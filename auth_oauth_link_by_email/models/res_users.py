# Copyright 2026 Avunu LLC (avu.nu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

_TRUE_VALUES = (True, 1, "true", "True", "TRUE", "1")


class ResUsers(models.Model):
    _inherit = "res.users"

    oauth_identity_ids = fields.One2many(
        "auth.oauth.identity",
        "user_id",
        string="OAuth Identities",
        copy=False,
        groups="base.group_system",
    )

    @api.model
    def _oauth_identity_ensure(self, user, provider, oauth_uid):
        """Record (provider, oauth_uid) as one of the user's identities."""
        identities = self.env["auth.oauth.identity"].sudo()
        if not identities.search_count(
            [("provider_id", "=", provider), ("oauth_uid", "=", oauth_uid)]
        ):
            identities.create(
                {"user_id": user.id, "provider_id": provider, "oauth_uid": oauth_uid}
            )

    @api.model
    def _oauth_identity_activate(self, user, provider, oauth_uid):
        """Make (provider, oauth_uid) the pair stored on the user.

        Odoo, and auth_oauth_multi_token after it, find the user by the single
        pair on res.users. A user with several identities has the one that is
        signing in put there first; the others stay in auth.oauth.identity. The
        write takes the user's row lock, so two sign-ins of one user in
        parallel are serialised and each finds its own pair.

        Returns whether the pair on the user changed.
        """
        user = user.sudo()
        if not user.active:
            return False
        current = (user.oauth_provider_id.id, user.oauth_uid)
        if current == (provider, oauth_uid):
            self._oauth_identity_ensure(user, provider, oauth_uid)
            return False
        if self.sudo().search_count(
            [("oauth_uid", "=", oauth_uid), ("oauth_provider_id", "=", provider)]
        ):
            return False  # another user holds this pair on their record
        if all(current):
            self._oauth_identity_ensure(user, *current)
        self._oauth_identity_ensure(user, provider, oauth_uid)
        user.write({"oauth_provider_id": provider, "oauth_uid": oauth_uid})
        return True

    @api.model
    def _auth_oauth_link_existing_user(self, provider, validation):
        """Find the user an OAuth sign-in belongs to and make it findable.

        Odoo matches a returning user on (provider, provider user id) held on
        res.users, one pair per user. This keeps every pair a user signs in
        with, and finds the user of a pair it has not seen:

        1. the pair is one of a user's identities: that user;
        2. the pair is already stored on a user: record it, nothing else;
        3. the provider has "Link Existing Users by Email" on, reports the
           email as verified, and exactly one active user has it as their
           login: that user, whatever identities they already have.

        Idempotent. Returns whether it changed the pair stored on a user.
        """
        oauth_uid = validation.get("user_id")
        if not oauth_uid:
            return False
        identity = (
            self.env["auth.oauth.identity"]
            .sudo()
            .search([("provider_id", "=", provider), ("oauth_uid", "=", oauth_uid)])
        )
        if identity:
            return self._oauth_identity_activate(identity.user_id, provider, oauth_uid)
        users = self.sudo()
        holder = users.search(
            [("oauth_uid", "=", oauth_uid), ("oauth_provider_id", "=", provider)]
        )
        if holder:
            self._oauth_identity_ensure(holder, provider, oauth_uid)
            return False
        oauth_provider = self.env["auth.oauth.provider"].sudo().browse(provider)
        if not oauth_provider.link_existing_users_by_email:
            return False
        email = (validation.get("email") or "").strip().lower()
        if not email:
            return False
        if validation.get("email_verified") not in _TRUE_VALUES:
            _logger.info(
                "OAuth provider %s: not linking by email, the email is not "
                "reported as verified",
                provider,
            )
            return False
        # `=ilike` treats `_` and `%` as wildcards: it narrows the search, the
        # exact comparison below decides.
        candidates = users.search([("login", "=ilike", email)]).filtered(
            lambda user: user.login.strip().lower() == email
        )
        if len(candidates) != 1:
            return False
        linked = self._oauth_identity_activate(candidates, provider, oauth_uid)
        _logger.info(
            "OAuth provider %s: linked an identity to user id %s by verified email",
            provider,
            candidates.id,
        )
        return linked

    @api.model
    def _auth_oauth_signin(self, provider, validation, params):
        self._auth_oauth_link_existing_user(provider, validation)
        return super()._auth_oauth_signin(provider, validation, params)
