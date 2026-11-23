# Copyright 2026 Avunu LLC (avu.nu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class AuthOAuthProvider(models.Model):
    _inherit = "auth.oauth.provider"

    link_existing_users_by_email = fields.Boolean(
        string="Link Existing Users by Email",
        help="Trust this provider: any login it vouches for (a verified email "
        "equal to an existing user's login) signs in as that user, the first time "
        "and for as long as the provider is enabled, even if the user already "
        "signs in with another provider or another account of this one. Every "
        "profile is kept on the user (OAuth tab) and none replaces another. Turn "
        "this on only for a provider whose email verification you trust as much "
        "as you trust your own users' passwords: anyone who can obtain a verified "
        "address from it can sign in as the matching user.",
    )
