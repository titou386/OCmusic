from django.test import TestCase
from selenium import webdriver
from account.models import User
import time


class RegisterPageTestCase(TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()

    def test_01_register_firefox(self):
        self.driver.get("http://localhost:8000/account/sign-up/")
        self.driver.find_element_by_id("id_username").send_keys("Test")
        self.driver.find_element_by_id("id_email").send_keys("test@test.fr")
        self.driver.find_element_by_id("id_password1").send_keys("1234")
        self.driver.find_element_by_id("id_password2").send_keys("1234")
        self.driver.find_element_by_id("submit").click()
        time.sleep(1)
        self.assertIn("http://localhost:8000/account/", self.driver.current_url)

    def test_02_login_firefox(self):
        self.driver.get("http://localhost:8000/account/sign-in")
        self.driver.find_element_by_id("id_username").send_keys("Test")
        self.driver.find_element_by_id("id_password").send_keys("1234")
        self.driver.find_element_by_id("submit").click()
        time.sleep(1)
        self.assertEquals("http://localhost:8000/account/", self.driver.current_url)

    def tearDown(self):
        self.driver.quit()


class LoginViewTestCase(TestCase):
    def setUp(self):
        u = User.objects.create(username="Michelle", email="michelle@free.fr")
        u.set_password("1234")
        u.save()

    def test_login_success(self):
        response = self.client.login(username="Michelle", password="1234")
        self.assertTrue(response)


class RegisterViewTestCase(TestCase):
    def setUp(self):
        u = User.objects.create(username="Michelle", email="michelle@free.fr")
        u.set_password("1234")
        u.save()

    def test_signup_success(self):
        response = self.client.post(
            "/account/sign-up/",
            {
                "username": "Jacques",
                "email": "jacques@free.fr",
                "password1": "1234",
                "password2": "1234",
            },
        )

        self.assertEquals(response.status_code, 302)

    def test_register_username_fail(self):
        response = self.client.post(
            "/account/sign-up/",
            {
                "username": "Michelle",
                "email": "michelle@yahoo.fr",
                "password1": "2345",
                "password2": "2345",
            },
        )
        self.assertEquals(response.status_code, 200)

    def test_register_email_fail(self):
        response = self.client.post(
            "/account/sign-up/",
            {
                "username": "michelle",
                "email": "michelle@free.fr",
                "password1": "2345",
                "password2": "2345",
            },
        )
        self.assertEquals(response.status_code, 200)

    def test_register_mismatch_password(self):
        response = self.client.post(
            "/account/sign-up/",
            {
                "username": "Vincent",
                "email": "vincent@free.fr",
                "password1": "1234",
                "password2": "2345",
            },
        )
        self.assertEquals(response.status_code, 200)

    def test_if_logged_no_register_page(self):
        self.client.post(
            "/account/sign-in/", {"username": "Michelle", "password": "1234"}
        )
        response = self.client.get("/account/sign-up/")
        self.assertEquals(response.status_code, 302)

    def test_if_logged_no_login_page(self):
        self.client.post(
            "/account/sign-in/", {"username": "Michelle", "password": "1234"}
        )
        response = self.client.get("/account/sign-in/")
        self.assertEquals(response.status_code, 302)

    def test_no_account_page_on_visitor(self):
        response = self.client.get("/account/")
        self.assertEquals(response.status_code, 302)
