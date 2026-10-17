import json
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

# ==============================
# PRUEBAS DE LA API DE RESERVAS
# ==============================
# Ejecutar con:  python manage.py test cuentas.api.tests
# (crea una base de prueba temporal y la borra al terminar)

URL = '/api/reservas/'


def reserva_valida(**cambios):
    datos = {
        'nombre': 'Ana Duarte',
        'correo': 'ana@ejemplo.com',
        'telefono': '0981 123456',
        'fecha': (date.today() + timedelta(days=7)).isoformat(),
        'hora': '20:00',
        'personas': 2,
        'motivo': 'cena',
        'notas': '',
    }
    datos.update(cambios)
    return datos


class ApiReservasTests(TestCase):

    def setUp(self):
        usuario = get_user_model().objects.create_user(
            email='prueba@ejemplo.com', password='clave-de-prueba',
            first_name='Prueba', last_name='Api')
        self.client.force_login(usuario)

    def post(self, datos):
        return self.client.post(URL, json.dumps(datos), content_type='application/json')

    # ----- GET -----
    def test_get_listado_200(self):
        r = self.client.get(URL)
        self.assertEqual(r.status_code, 200)
        self.assertIsInstance(r.json()['reservas'], list)

    def test_get_por_id_200(self):
        r = self.client.get(URL + '1/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()['reserva']['id'], 1)

    def test_get_por_id_inexistente_404(self):
        r = self.client.get(URL + '99999/')
        self.assertEqual(r.status_code, 404)

    # ----- POST -----
    def test_post_valido_201_y_aparece_en_el_get(self):
        r = self.post(reserva_valida())
        self.assertEqual(r.status_code, 201)
        nueva = r.json()['reserva']
        self.assertEqual(nueva['estado'], 'pendiente')

        ids = [x['id'] for x in self.client.get(URL).json()['reservas']]
        self.assertIn(nueva['id'], ids)

    def test_post_sin_datos_obligatorios_400(self):
        r = self.post({})
        self.assertEqual(r.status_code, 400)
        errores = r.json()['errores']
        for campo in ('nombre', 'correo', 'telefono', 'fecha', 'hora', 'personas'):
            self.assertIn(campo, errores)

    def test_post_datos_invalidos_400(self):
        r = self.post(reserva_valida(correo='sin-arroba', personas=0, fecha='2020-01-01'))
        self.assertEqual(r.status_code, 400)
        self.assertEqual(set(r.json()['errores']), {'correo', 'personas', 'fecha'})

    def test_post_json_mal_formado_400(self):
        r = self.client.post(URL, '{nombre: ', content_type='application/json')
        self.assertEqual(r.status_code, 400)

    # ----- Otros casos -----
    def test_metodo_no_permitido_405(self):
        self.assertEqual(self.client.delete(URL).status_code, 405)

    def test_sin_sesion_401(self):
        self.client.logout()
        self.assertEqual(self.client.get(URL).status_code, 401)

    def test_post_sin_token_csrf_403(self):
        cliente = Client(enforce_csrf_checks=True)
        cliente.force_login(get_user_model().objects.get(email='prueba@ejemplo.com'))
        r = cliente.post(URL, json.dumps(reserva_valida()), content_type='application/json')
        self.assertEqual(r.status_code, 403)
