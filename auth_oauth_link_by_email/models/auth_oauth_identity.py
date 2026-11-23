# Copyright 2026 Avunu LLC (avu.nu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class AuthOAuthIdentity(models.Model):
    """One provider login profile of a user.

    Odoo stores a single (provider, provider user id) pair on res.users. A user
    can hold any number of these; the pair on res.users is the one that signed
    in last (see res.users._oauth_identity_activate).
    """

    _name = "auth.oauth.identity"
    _description = "OAuth Identity"
    _rec_name = "oauth_uid"
    _order = "user_id, provider_id, id"

    user_id = fields.Many2one(
        "res.users", string="User", required=True, index=True, ondelete="cascade"
    )
    provider_id = fields.Many2one(
        "auth.oauth.provider",
        string="OAuth Provider",
        required=True,
        ondelete="cascade",
    )
    oauth_uid = fields.Char(string="OAuth User ID", required=True)

    _sql_constraints = [
        (
            "uniq_provider_oauth_uid",
            "unique(provider_id, oauth_uid)",
            "A provider's user id can belong to only one user.",
        ),
    ]
