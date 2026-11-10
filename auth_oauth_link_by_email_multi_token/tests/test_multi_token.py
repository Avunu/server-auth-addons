# Copyright 2026 Avunu LLC (avu.nu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.tests import TransactionCase, tagged

GOOGLE_UID = "118000000000000000001"


@tagged("post_install", "-at_install")
class TestLinkByEmailMultiToken(TransactionCase):
    def test_first_signin_links_and_records_a_token(self):
        provider = self.env["auth.oauth.provider"].create(
            {
                "name": "Test provider",
                "body": "Sign in with Test",
                "client_id": "test-client",
                "auth_endpoint": "https://idp.example/auth",
                "validation_endpoint": "https://idp.example/tokeninfo",
                "enabled": True,
                "link_existing_users_by_email": True,
            }
        )
        user = self.env["res.users"].create(
            {"name": "Josh", "login": "josh@example.com", "email": "josh@example.com"}
        )
        validation = {
            "user_id": GOOGLE_UID,
            "email": "josh@example.com",
            "email_verified": True,
        }
        login = self.env["res.users"]._auth_oauth_signin(
            provider.id, validation, {"access_token": "token-1", "state": "{}"}
        )
        self.assertEqual(login, "josh@example.com")
        self.assertEqual(user.oauth_uid, GOOGLE_UID)
        self.assertEqual(
            user.oauth_access_token_ids.mapped("oauth_access_token"), ["token-1"]
        )
