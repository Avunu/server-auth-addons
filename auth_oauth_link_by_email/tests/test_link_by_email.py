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

    def test_second_account_of_one_provider_is_linked_too(self):
        self.assertEqual(self._signin(), "josh@example.com")
        self.assertEqual(
            self._signin(self._validation(user_id="second")), "josh@example.com"
        )
        self.assertEqual(self.user.oauth_uid, "second")
        self.assertEqual(
            sorted(self.user.oauth_identity_ids.mapped("oauth_uid")),
            sorted([GOOGLE_UID, "second"]),
        )

    def test_a_second_provider_is_linked_and_the_first_still_signs_in(self):
        other = self.provider.copy({"name": "Other provider"})
        self.assertEqual(self._signin(), "josh@example.com")
        self.assertEqual(
            self._signin(self._validation(user_id="ms-1"), other), "josh@example.com"
        )
        self.assertEqual(self.user.oauth_provider_id, other)
        # The first provider's profile was kept, and signs in again.
        self.assertEqual(self._signin(), "josh@example.com")
        self.assertEqual(self.user.oauth_provider_id, self.provider)
        self.assertEqual(self.user.oauth_uid, GOOGLE_UID)
        self.assertEqual(len(self.user.oauth_identity_ids), 2)

    def test_identity_stored_by_hand_is_kept_when_another_is_linked(self):
        self.user.write({"oauth_provider_id": self.provider.id, "oauth_uid": "other"})
        self.assertEqual(self._signin(), "josh@example.com")
        self.assertEqual(self.user.oauth_uid, GOOGLE_UID)
        self.assertEqual(
            sorted(self.user.oauth_identity_ids.mapped("oauth_uid")),
            sorted(["other", GOOGLE_UID]),
        )
        self.assertEqual(
            self._signin(self._validation(user_id="other")), "josh@example.com"
        )
        self.assertEqual(self.user.oauth_uid, "other")

    def test_known_identity_signs_in_even_when_the_provider_is_off(self):
        self.assertEqual(self._signin(), "josh@example.com")
        self.provider.link_existing_users_by_email = False
        self.user.write({"oauth_uid": "other"})
        self.assertEqual(self._signin(), "josh@example.com")
        self.assertEqual(self.user.oauth_uid, GOOGLE_UID)
        self.assertFalse(self._signin(self._validation(user_id="new")))

    def test_identity_follows_its_user_not_the_email(self):
        self.assertEqual(self._signin(), "josh@example.com")
        self.user.login = "josh@new.example.com"
        self.assertEqual(self._signin(), "josh@new.example.com")

    def test_two_users_each_link_by_their_own_email(self):
        anna = self.env["res.users"].create(
            {"name": "Anna", "login": "anna@example.com"}
        )
        self.assertEqual(self._signin(), "josh@example.com")
        self.assertEqual(
            self._signin(self._validation(user_id="anna-1", email="anna@example.com")),
            "anna@example.com",
        )
        self.assertEqual(anna.oauth_uid, "anna-1")
        self.assertEqual(self.user.oauth_uid, GOOGLE_UID)

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
        self.assertEqual(holder.oauth_identity_ids.oauth_uid, GOOGLE_UID)

    def test_underscore_is_not_a_wildcard(self):
        self.user.login = "a_b@example.com"
        self.assertFalse(self._signin(self._validation(email="axb@example.com")))
        self.assertFalse(self.user.oauth_uid)
