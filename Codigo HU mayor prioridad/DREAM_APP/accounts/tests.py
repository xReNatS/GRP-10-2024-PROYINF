from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone

class TestAuthenticationEndpoint(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.auth_url = reverse('login')
        cls.valid_user = {'username': 'medico1', 'password': 'validpassword'}
        cls.invalid_user = {'username': 'medico1', 'password': 'wrongpassword'}
        User.objects.create_user(username=cls.valid_user['username'], password=cls.valid_user['password'])

    def test_failed_login(self):
        response = self.client.post(self.auth_url, {'username': 'invalid_user', 'password': 'wrong_password'})
        self.assertEqual(response.status_code, 401)  

    def test_successful_login(self):
        response = self.client.post(self.auth_url, self.valid_user)
        self.assertEqual(response.status_code, 302)  


class TestFailedLoginAttempts(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Configuración de los datos de prueba
        cls.client = Client()
        cls.auth_url = reverse('login')  # Ajusta 'login' al nombre de tu vista de login si es diferente
        cls.valid_user = {'username': 'medico1', 'password': 'validpassword'}
        cls.invalid_user = {'username': 'medico1', 'password': 'wrongpassword'}
        # Crea un usuario en la base de datos de pruebas
        User.objects.create_user(username=cls.valid_user['username'], password=cls.valid_user['password'])

    def test_failed_attempts_limit(self):
        # Caso de prueba 3: Intentos fallidos excedidos
        for _ in range(5):
            response = self.client.post(self.auth_url, self.invalid_user)
            self.assertEqual(response.status_code, 401)  # Verifica que el código de error sea 401 para intentos fallidos
        
        # En el sexto intento debe bloquearse el acceso
        response = self.client.post(self.auth_url, self.invalid_user)
        self.assertEqual(response.status_code, 403)  # Verifica que el usuario está bloqueado
        self.assertContains(response, "Wait 5 minutes")  # Verifica que el mensaje de bloqueo aparezca

    def test_successful_login_after_block(self):
        # Simulación del tiempo de espera (o usa mock para simular el paso del tiempo)
        # Después del bloqueo, el usuario debería poder autenticarse si espera 5 minutos
        response = self.client.post(self.auth_url, self.valid_user)
        self.assertEqual(response.status_code, 200)  # Verifica que después del bloqueo, el login sea exitoso
