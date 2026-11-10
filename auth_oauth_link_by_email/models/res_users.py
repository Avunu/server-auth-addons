# Copyright 2026 Avunu LLC (avu.nu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging

from odoo import api, models

_logger = logging.getLogger(__name__)

_TRUE_VALUES = (True, 1, "true", "True", "TRUE", "1")


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def _auth_oauth_link_existing_user(self, provider, validation):
        """Link the user whose login is the provider's verified email.

        Odoo matches a returning user on (provider, provider user id) only. A
        user created any other way (by hand, imported, invited by password) has
        neither, so the sign-in falls through to a sign-up that collides with
        that user's login. When the provider is configured for it, store the
        pair on the one active, unlinked user whose login is the verified email.

        Idempotent: it does nothing once a user holds the pair.
        """
        oauth_provider = self.env["auth.oauth.provider"].sudo().browse(provider)
        if not oauth_provider.link_existing_users_by_email:
            return False
        oauth_uid = validation.get("user_id")
        email = (validation.get("email") or "").strip().lower()
        if not oauth_uid or not email:
            return False
        if validation.get("email_verified") not in _TRUE_VALUES:
            _logger.info(
                "OAuth provider %s: not linking by email, the email is not "
                "reported as verified",
                provider,
            )
            return False
        users = self.sudo()
        if users.search_count(
            [("oauth_uid", "=", oauth_uid), ("oauth_provider_id", "=", provider)]
        ):
            return False
        # `=ilike` treats `_` and `%` as wildcards: it narrows the search, the
        # exact comparison below decides.
        candidates = users.search([("login", "=ilike", email)]).filtered(
            lambda user: user.login.strip().lower() == email
            and not user.oauth_uid
            and not user.oauth_provider_id
        )
        if len(candidates) != 1:
            return False
        candidates.write({"oauth_provider_id": provider, "oauth_uid": oauth_uid})
        _logger.info(
            "OAuth provider %s: linked user id %s by verified email",
            provider,
            candidates.id,
        )
        return True

    @api.model
    def _auth_oauth_signin(self, provider, validation, params):
        self._auth_oauth_link_existing_user(provider, validation)
        return super()._auth_oauth_signin(provider, validation, params)
