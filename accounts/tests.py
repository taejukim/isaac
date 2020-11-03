from django.test import SimpleTestCase, Client

# Create your tests here.
class AccountsTestClass(SimpleTestCase):

    def check_login(self):
        c = Client()
        resp = c.post('/login/', {'emp_no':'to10523', 'pw':'!qweqweqwe1'})
        self.assertEqual(resp.status_code, 200)
        