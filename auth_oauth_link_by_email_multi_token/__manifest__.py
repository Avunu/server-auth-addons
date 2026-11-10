# Copyright 2026 Avunu LLC (avu.nu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "OAuth Sign-in: Link by Email with Multiple Tokens",
    "summary": "Makes link-by-email work when auth_oauth_multi_token is installed.",
    "version": "18.0.1.0.0",
    "category": "Technical",
    "author": "Avunu LLC",
    "website": "https://github.com/Avunu/server-auth-addons",
    "license": "AGPL-3",
    "depends": [
        "auth_oauth_link_by_email",  # the link this module runs earlier
        "auth_oauth_multi_token",  # OCA/server-auth: looks the user up before super()
    ],
    "auto_install": True,
    "installable": True,
}
