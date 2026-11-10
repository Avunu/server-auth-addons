# Copyright 2026 Avunu LLC (avu.nu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def _auth_oauth_signin(self, provider, validation, params):
        # auth_oauth_multi_token looks the user up by (provider, uid) before it
        # calls super(), and refuses the sign-in when that lookup is empty. This
        # module depends on it, so it loads after it and runs outside it: the
        # link is stored before that lookup. (auth_oauth_link_by_email alone
        # loads before it on the module name, which is too late.)
        self._auth_oauth_link_existing_user(provider, validation)
        return super()._auth_oauth_signin(provider, validation, params)
