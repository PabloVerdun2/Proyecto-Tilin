import json
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from cuentas.models import Reserva

# Pruebas de la API de reservas sobre la BD.
# Ejecutar con: python manage.py test cuentas.api.tests

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
        self.usuario = get_user_model().objects.create_user(
            email='prueba@ejemplo.com', password='clave-de-prueba',
            first_name='Prueba', last_name='Api')
        self.client.force_login(self.usuario)

    def post(self, datos):
        return self.client.post(URL, json.dumps(datos), content_type='application/json')

    def _crear_en_bd(self, **cambios):
        d = reserva_valida(**cambios)
        return Reserva.objects.create(
            cliente=self.usuario, nombre_contacto=d['nombre'], correo=d['correo'],
            telefono=d['telefono'], fecha=d['fecha'], hora=d['hora'],
            cantidad_personas=d['personas'], motivo=d['motivo'], notas_adicionales=d['notas'])

    # ----- GET -----
    def test_get_listado_200(self):
        r = self.client.get(URL)
        self.assertEqual(r.status_code, 200)
        self.assertIsInstance(r.json()['reservas'], list)

    def test_get_por_id_200(self):
        reserva = self._crear_en_bd()
        r = self.client.get(URL + str(reserva.id) + '/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()['reserva']['id'], reserva.id)

    def test_get_por_id_inexistente_404(self):
        r = self.client.get(URL + '99999/')
        self.assertEqual(r.status_code, 404)

    # ----- POST -----
    def test_post_valido_201_y_persiste_en_bd(self):
        r = self.post(reserva_valida())
        self.assertEqual(r.status_code, 201)
        nueva = r.json()['reserva']
        self.assertEqual(nueva['estado'], 'pendiente')
        # La fila quedo realmente en la base de datos.
        self.assertTrue(Reserva.objects.filter(id=nueva['id']).exists())

    def test_post_aparece_en_el_get(self):
        nueva = self.post(reserva_valida()).json()['reserva']
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
        cliente.force_login(self.usuario)
        r = cliente.post(URL, json.dumps(reserva_valida()), content_type='application/json')
        self.assertEqual(r.status_code, 403)
