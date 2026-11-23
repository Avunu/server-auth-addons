# Copyright 2026 Avunu LLC (avu.nu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "OAuth Sign-in: Link Existing Users by Email",
    "summary": "Any OAuth login whose verified email is an existing user's login "
    "signs in as that user: any number of profiles, from any provider "
    "that has this turned on.",
    "version": "18.0.1.0.0",
    "category": "Technical",
    "author": "Avunu LLC",
    "website": "https://github.com/Avunu/server-auth-addons",
    "license": "AGPL-3",
    "depends": [
        "auth_oauth",  # res.users sign-in and the auth.oauth.provider model extended
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/auth_oauth_provider_views.xml",
        "views/res_users_views.xml",
    ],
    "installable": True,
}
