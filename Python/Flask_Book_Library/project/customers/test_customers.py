import unittest
from sqlalchemy.exc import IntegrityError
from project import db, app
from project.customers.models import Customer


class TestCustomerModel(unittest.TestCase):

    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_valid_customer_creation(self):
        customer = Customer(name='Pierwszy Agent', city='Warsaw', age=30, pesel='12345678901', street='Zielona', appNo='A123')
        db.session.add(customer)
        db.session.commit()
        self.assertIsNotNone(customer.id)

    def test_invalid_age(self):
        customer = Customer(name='Drugi Agent', city='Krakow', age=-5, pesel='98765432101', street='Niebieska', appNo='B123')
        db.session.add(customer)
        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_sql_injection(self):
        customer = Customer(name="Trzeci Agent'); DROP TABLE customers;--", city='Lodz', age=25, pesel='11111111111',
                            street='Czerwona', appNo='C123')
        db.session.add(customer)
        db.session.commit()
        self.assertNotIn("DROP TABLE", customer.name)

    def test_javascript_injection(self):
        customer = Customer(name='<script>alert("XSS")</script>', city='Poznan', age=21, pesel='22222222222',
                            street='Czarna', appNo='D123')
        db.session.add(customer)
        db.session.commit()
        self.assertNotIn('<script>', customer.name)
        self.assertNotIn('</script>', customer.name)

    def test_extreme_string_length(self):
        long_name = 'A' * 300
        customer = Customer(name=long_name, city='Gdansk', age=40, pesel='33333333333', street='Pomaranczowa',
                            appNo='E123')
        db.session.add(customer)
        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_empty_fields(self):
        test_cases = [
            {'name': '', 'city': '', 'age': 0, 'pesel': '', 'street': '', 'appNo': ''},
            {'name': None, 'city': None, 'age': None, 'pesel': None, 'street': None, 'appNo': None}
        ]

        for case in test_cases:
            with self.subTest(case=case):
                customer = Customer(
                    name=case['name'],
                    city=case['city'],
                    age=case['age'],
                    pesel=case['pesel'],
                    street=case['street'],
                    appNo=case['appNo']
                )
                db.session.add(customer)
                with self.assertRaises(IntegrityError):
                    db.session.commit()

    def test_unique_pesel(self):
        customer1 = Customer(name='Czlowiek 1', city='Wars', age=28, pesel='11111111111', street='Kolorawa',
                             appNo='A001')
        customer2 = Customer(name='Czlowiek 2', city='Sawa', age=35, pesel='11111111111', street='Kolorowa',
                             appNo='A002')
        db.session.add(customer1)
        db.session.commit()
        db.session.add(customer2)
        with self.assertRaises(IntegrityError):
            db.session.commit()


if __name__ == '__main__':
    unittest.main()