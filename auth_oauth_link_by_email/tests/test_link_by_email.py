# Copyright 2026 Avunu LLC (avu.nu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.exceptions import AccessDenied
from odoo.tests import TransactionCase, tagged

GOOGLE_UID = "118000000000000000001"


@tagged("post_install", "-at_install")
class TestLinkByEmail(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.provider = cls.env["auth.oauth.provider"].create(
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
        cls.user = cls.env["res.users"].create(
            {"name": "Josh", "login": "josh@example.com", "email": "josh@example.com"}
        )

    def _validation(self, **overrides):
        validation = {
            "user_id": GOOGLE_UID,
            "email": "josh@example.com",
            "email_verified": True,
        }
        validation.update(overrides)
        return validation

    def _signin(self, validation=None, provider=None):
        """Return the login, or None when the sign-in is refused.

        no_user_creation makes Odoo return None for a user it cannot match
        instead of attempting a sign-up. auth_oauth_multi_token, when it is
        installed, raises AccessDenied for the same case: both are a refusal.
        """
        Users = self.env["res.users"].with_context(no_user_creation=True)
        try:
            return Users._auth_oauth_signin(
                (provider or self.provider).id,
                validation or self._validation(),
                {"access_token": "token", "state": "{}"},
            )
        except AccessDenied:
            return None

    def test_first_signin_links_the_user(self):
        self.assertEqual(self._signin(), "josh@example.com")
        self.assertEqual(self.user.oauth_provider_id, self.provider)
        self.assertEqual(self.user.oauth_uid, GOOGLE_UID)

    def test_second_signin_uses_the_link(self):
        self._signin()
        self.assertEqual(self._signin(), "josh@example.com")

    def test_email_match_ignores_case(self):
        self.assertEqual(
            self._signin(self._validation(email="Josh@Example.COM")),
            "josh@example.com",
        )
        self.assertEqual(self.user.oauth_uid, GOOGLE_UID)

    def test_verified_flag_as_string(self):
        self.assertEqual(
            self._signin(self._validation(email_verified="true")),
            "josh@example.com",
        )

    def test_provider_off_does_not_link(self):
        self.provider.link_existing_users_by_email = False
        self.assertFalse(self._signin())
        self.assertFalse(self.user.oauth_uid)

    def test_unverified_email_does_not_link(self):
        for flag in (False, "false", None):
            validation = self._validation(email_verified=flag)
            if flag is None:
                del validation["email_verified"]
            self.assertFalse(self._signin(validation), flag)
        self.assertFalse(self.user.oauth_uid)

    def test_no_email_does_not_link(self):
        validation = self._validation()
        del validation["email"]
        self.assertFalse(self._signin(validation))
        self.assertFalse(self.user.oauth_uid)

    def test_user_with_another_identity_is_not_relinked(self):
        self.user.write({"oauth_provider_id": self.provider.id, "oauth_uid": "other"})
        self.assertFalse(self._signin())
        self.assertEqual(self.user.oauth_uid, "other")

    def test_user_linked_to_another_provider_is_not_relinked(self):
        other = self.provider.copy({"name": "Other provider"})
        self.user.write({"oauth_provider_id": other.id, "oauth_uid": "other"})
        self.assertFalse(self._signin())
        self.assertEqual(self.user.oauth_provider_id, other)

    def test_inactive_user_is_not_linked(self):
        self.user.active = False
        self.assertFalse(self._signin())
        self.assertFalse(self.user.oauth_uid)

    def test_identity_held_by_another_user_is_left_alone(self):
        holder = self.env["res.users"].create(
            {"name": "Holder", "login": "holder@example.com"}
        )
        holder.write({"oauth_provider_id": self.provider.id, "oauth_uid": GOOGLE_UID})
        self.assertEqual(self._signin(), "holder@example.com")
        self.assertFalse(self.user.oauth_uid)

    def test_underscore_is_not_a_wildcard(self):
        self.user.login = "a_b@example.com"
        self.assertFalse(self._signin(self._validation(email="axb@example.com")))
        self.assertFalse(self.user.oauth_uid)
