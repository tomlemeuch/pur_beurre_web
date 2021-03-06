"""
Functional tests.
"""
from django.contrib.sessions.models import Session
from selenium.webdriver.common.keys import Keys

from substitute_finder.models import CustomUser
from substitute_finder.tests.test_helpers import CustomStaticLiveServerTestCase


class UserInterfaceTestCase(CustomStaticLiveServerTestCase):
    """
    Live tests for comment user interface.
    """
    fixtures = ['test_users.json', 'test_categories.json', 'test_products.json']

    def test_header_form(self):
        """
        Test a search using header form.
        """
        self.browser.get(self.live_server_url)

        self.wait.until(lambda driver: self.get_element("header form").is_displayed())
        search_field = self.get_element("header form #id_product")
        submit_button = self.get_element("header form button")
        search_field.send_keys("coca")
        submit_button.click()
        self.wait.until(lambda driver: self.get_element("#relevant_products").is_displayed())
        self.assertEqual(self.browser.current_url, "%s/search" % self.live_server_url)
        self.assertTrue(self.get_element(".product-card"))

    def test_navbar_form(self):
        """
        Test a search using navbar form.
        """
        self.browser.get(self.live_server_url)
        self.wait.until(lambda driver: self.get_element(".navbar-form").is_displayed())
        search_field = self.get_element(".navbar-form #id_product")
        search_field.send_keys("coca")
        search_field.send_keys(Keys.ENTER)
        self.wait.until(lambda driver: self.get_element("#relevant_products").is_displayed())
        self.assertEqual(self.browser.current_url, "%s/search" % self.live_server_url)
        self.assertTrue(self.get_element(".product-card"))

    def test_login_form(self):
        """
        Test user login.
        """
        self.browser.get("%s/login" % self.live_server_url)
        self.wait.until(lambda driver: self.get_element("#id_email").is_displayed())
        email_field = self.get_element("#id_email")
        password_field = self.get_element("#id_password")
        submit_button = self.get_element("form button")
        email_field.send_keys("user@test.fr")
        password_field.send_keys("test")
        submit_button.click()
        self.wait.until(lambda driver: self.get_element("header form #id_product").is_displayed())

        session_id = self.browser.get_cookie("sessionid")['value']

        session = Session.objects.get(pk=session_id)
        user = CustomUser.objects.get(email='user@test.fr')

        self.assertEqual(session.get_decoded()['_auth_user_id'], str(user.pk))
        self.assertEqual(self.browser.current_url, "%s/" % self.live_server_url)
        self.assertTrue(self.get_element("header form #id_product"))

    def test_login_form_wrong_password(self):
        """
        Test user login.
        """
        self.browser.get("%s/login" % self.live_server_url)
        self.wait.until(lambda driver: self.get_element("#id_email").is_displayed())
        email_field = self.get_element("#id_email")
        password_field = self.get_element("#id_password")
        submit_button = self.get_element("form button")
        email_field.send_keys("user@test.fr")
        password_field.send_keys("wrong_password")
        submit_button.click()

        self.assertEqual(self.browser.current_url, "%s/login" % self.live_server_url)
        self.assertTrue(self.get_element(".alert"))

    def test_create_account_form(self):
        """
        Test account creation.
        """

        old_nb_users = CustomUser.objects.count()

        self.browser.get("%s/create-account" % self.live_server_url)
        self.wait.until(lambda driver: self.get_element("#id_email").is_displayed())
        email_field = self.get_element("#id_email")
        username_field = self.get_element("#id_username")
        password_field = self.get_element("#id_password")
        submit_button = self.get_element("form button")

        email_field.send_keys("new_user@test.fr")
        username_field.send_keys("new_user")
        password_field.send_keys("test")
        submit_button.click()

        new_nb_users = CustomUser.objects.count()

        self.wait.until(lambda driver: self.get_element("#id_product").is_displayed())
        self.assertEqual(self.browser.current_url, "%s/" % self.live_server_url)
        self.assertEqual(new_nb_users, old_nb_users + 1)

    def test_create_account_form_no_password(self):
        """
        Test account creation.
        """
        self.browser.get("%s/create-account" % self.live_server_url)
        self.wait.until(lambda driver: self.get_element("#id_email").is_displayed())
        email_field = self.get_element("#id_email")
        username_field = self.get_element("#id_username")
        password_field = self.get_element("#id_password")
        submit_button = self.get_element("form button")

        email_field.send_keys("new_user@test.fr")
        username_field.send_keys("test")
        password_field.send_keys("")
        submit_button.click()

        self.assertEqual(self.browser.current_url, "%s/create-account/" % self.live_server_url)
        self.assertTrue(password_field == self.browser.switch_to.active_element)

    def test_create_account_form_user_exists(self):
        """
        Test account creation.
        """
        existing_user = CustomUser.objects.first()
        self.browser.get("%s/create-account" % self.live_server_url)
        self.wait.until(lambda driver: self.get_element("#id_email").is_displayed())
        email_field = self.get_element("#id_email")
        username_field = self.get_element("#id_username")
        password_field = self.get_element("#id_password")
        submit_button = self.get_element("form button")
        email_field.send_keys(existing_user.email)
        username_field.send_keys(existing_user.username)
        password_field.send_keys("test")
        submit_button.click()

        self.assertEqual(self.browser.current_url, "%s/create-account/" % self.live_server_url)
        self.assertTrue(self.get_element(".alert"))

    def test_logout_form(self):
        """
        Test user logout.
        """
        self.browser.get("%s/login" % self.live_server_url)

        self.wait.until(lambda driver: self.get_element("#id_email").is_displayed())
        email_field = self.get_element("#id_email")
        password_field = self.get_element("#id_password")
        submit_button = self.get_element("form button")
        email_field.send_keys("user@test.fr")
        password_field.send_keys("test")
        submit_button.click()
        self.wait.until(lambda driver: self.get_element("header form #id_product").is_displayed())

        session_id = self.browser.get_cookie("sessionid")['value']

        session = Session.objects.get(pk=session_id)
        user = CustomUser.objects.get(email='user@test.fr')
        self.assertEqual(user.id, int(session.get_decoded()['_auth_user_id']))

        logout_link = self.get_element('.navbar-nav li:nth-child(3) a')

        logout_link.click()

        self.assertIsNone(self.browser.get_cookie("sessionid"))

        self.assertEqual(self.browser.current_url, "%s/" % self.live_server_url)
        self.assertTrue(self.get_element("header form #id_product"))

    def test_visit_product_page(self):
        """
        Test product page.
        """
        self.browser.get(self.live_server_url)

        self.wait.until(lambda driver: self.get_element("header form").is_displayed())
        search_field = self.get_element("header form #id_product")
        submit_button = self.get_element("header form button")
        search_field.send_keys("coca")
        submit_button.click()
        self.wait.until(lambda driver: self.get_element("#relevant_products").is_displayed())

        card_link = self.get_element(".product-card a.card-body")
        card_link.click()

        product_header = self.get_element(".producthead")
        self.assertTrue(product_header)

        product_id = self.get_element(".producthead .container .row .col").get_attribute("id")

        cards = self.browser.find_elements_by_css_selector(".product-card")
        cards_id = [card.get_attribute("id") for card in cards]

        self.assertNotIn(product_id, cards_id)

    def test_add_to_favorites(self):
        """
        Test addition of product to favorites and visit favorites page.
        """
        self.browser.get("%s/login" % self.live_server_url)

        self.wait.until(lambda driver: self.get_element("#id_email").is_displayed())
        email_field = self.get_element("#id_email")
        password_field = self.get_element("#id_password")
        submit_button = self.get_element("form button")
        email_field.send_keys("user@test.fr")
        password_field.send_keys("test")
        submit_button.click()

        self.wait.until(lambda driver: self.get_element("header form").is_displayed())
        search_field = self.get_element("header form #id_product")
        submit_button = self.get_element("header form button")
        search_field.send_keys("coca")
        submit_button.click()
        self.wait.until(lambda driver: self.get_element("#relevant_products").is_displayed())

        product_card = self.get_element(".product-card")
        product_card_id = product_card.get_attribute("id")
        card_add_to_favorites_link = self.get_element(".product-card .card-footer a")
        card_add_to_favorites_link.click()

        carrot = self.get_element(".header-logo").find_element_by_xpath('../..')
        carrot.click()
        self.assertIn("/favorites", self.browser.current_url)
        cards = self.browser.find_elements_by_css_selector(".product-card")
        cards_id = [card.get_attribute("id") for card in cards]
        self.assertIn(product_card_id, cards_id)
