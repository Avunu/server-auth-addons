# Copyright 2026 Avunu LLC (avu.nu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class AuthOAuthProvider(models.Model):
    _inherit = "auth.oauth.provider"

    link_existing_users_by_email = fields.Boolean(
        string="Link Existing Users by Email",
        help="On a user's first sign-in with this provider, link the existing "
        "Odoo user whose login equals the email the provider returns, when the "
        "provider says that email is verified. Turn this on only for a provider "
        "that verifies email addresses (Google does): anyone who can obtain a "
        "verified address from it can sign in as the matching user.",
    )
