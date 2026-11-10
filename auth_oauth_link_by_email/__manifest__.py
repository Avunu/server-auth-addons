# Copyright 2026 Avunu LLC (avu.nu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "OAuth Sign-in: Link Existing Users by Email",
    "summary": "On a first OAuth sign-in, link the Odoo user whose login is the "
    "provider's verified email, instead of failing the sign-up.",
    "version": "18.0.1.0.0",
    "category": "Technical",
    "author": "Avunu LLC",
    "website": "https://github.com/Avunu/server-auth-addons",
    "license": "AGPL-3",
    "depends": [
        "auth_oauth",  # res.users sign-in and the auth.oauth.provider model extended
    ],
    "data": [
        "views/auth_oauth_provider_views.xml",
    ],
    "installable": True,
}
