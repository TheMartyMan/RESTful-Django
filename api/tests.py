from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import Company, Employee
import uuid






# -------------------------------------- COMPANY --------------------------------------


class CompanyAPITestCase(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name="Teszt Cég 1",
            address="1234 Teszt utca 56",
            phone="+36301234567",
            description=""
        )
        self.valid_payload = {
            "name": "Teszt Cég 2",
            "address": "1102 Budapest Valami utca 22",
            "phone": "06301234567",
            "description": "Teszt cég leírás"
        }
        self.invalid_payload = {
            "name": "",
            "address": "",
            "phone": "",
        }


    def test_company_GET(self):
        url = reverse('companies')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
        print(f"\nCompany GET ✔ ({response.status_code})")

    def test_company_POST_valid(self):
        url = reverse('companies')
        response = self.client.post(url, data=self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], self.valid_payload['name'])
        print(f"\nCompany valid POST ✔ ({response.status_code})")

    def test_company_POST_invalid(self):
        url = reverse('companies')
        response = self.client.post(url, data=self.invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        print(f"\nCmopany invalid POST ✔ ({response.status_code})")

    def test_company_PATCH(self):
        url = reverse('company_detail', args=[self.company.id])
        updated_data = {
            "name": "Új Cégnév",
            "address": "7890 Új utca 11"
        }

        response = self.client.patch(url, data=updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data['name'], self.valid_payload['name'])
        print(f"\nCompany PATCH ✔ ({response.status_code})")


    def test_company_PUT(self):
        url = reverse('company_detail', args=[self.company.id])
        updated_data = {
            "name": "Új Cégnév",
            "address": "7890 Új utca 11",
            "phone": "06301234567",
            "description": "Hozzáadva desc"
        }

        response = self.client.put(url, data=updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        print(f"\nCompany PUT ✔ ({response.status_code})")

    def test_company_DELETE(self):
        url = reverse('company_detail', args=[self.company.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Company.objects.filter(id=self.company.id).exists())
        print(f"\nCompany DELETE ✔ ({response.status_code})")




# -------------------------------------- EMPLOYEE --------------------------------------




class EmployeeAPITestCase(APITestCase):
    def setUp(self):

        self.company = Company.objects.create(
            name="Teszt Company",
            address="1234 Teszt utca 12",
            phone="+36301234567",
            description="Teszt leírás"
        )

        self.employee = Employee.objects.create(
            name="Aladár",
            email="email@email.email",
            job_title="tester",
            age=23,
            company=self.company
        )



        self.employee2 = Employee.objects.create(
            name="Teszt Employee 2",
            email="employee2@example.com",
            job_title="developer",
            age=30,
            company=self.company
        )

        self.employee3 = Employee.objects.create(
            name="Teszt Employee 3",
            email="employee3@example.com",
            job_title="designer",
            age=28,
            company=self.company
        )


        self.valid_payload = {
            "name": "Aladár",
            "email": "email@ema2il.email",
            "job_title": "tester",
            "age":23,
            "company": str(self.company.id)
        }
        self.invalid_payload = {
            "name": "Nemjó",
            "email": "nemjo",
        }


    def test_employee_GET(self):
        url = reverse('employees')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
        print(f"\nEmployee GET ✔ ({response.status_code})")

    def test_employee_POST_valid(self):
        url = reverse('employees')
        response = self.client.post(url, data=self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], self.valid_payload['name'])
        print(f"\nEmployee valid POST ✔ ({response.status_code})")

    def test_employee_POST_invalid(self):
        url = reverse('employees')
        response = self.client.post(url, data=self.invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        print(f"\nEmployee invalid POST ✔ ({response.status_code})")

    def test_employee_PATCH(self):
        url = reverse('employee_detail', args=[self.employee.id])
        updated_data = {
            "name": "Újnév",
            "address": "7890 Új utca 11"
        }

        response = self.client.patch(url, data=updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data['name'], self.valid_payload['name'])
        print(f"\nEmployee PATCH ✔ ({response.status_code})")


    def test_employee_PUT(self):
        url = reverse('employee_detail', args=[self.employee.id])
        updated_data = {
            "name": "Put Teszt",
            "email": "valamiteszt@teszt.hu",
            "job_title": "tester",
            "age": 22,
            "company": str(self.company.id)
        }

        response = self.client.put(url, data=updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(f"\nEmployee PUT ✔ ({response.status_code})")

    def test_employee_DELETE(self):
        url = reverse('employee_detail', args=[self.employee.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Employee.objects.filter(id=self.employee.id).exists())
        print(f"\nEmployee DELETE ✔ ({response.status_code})")




# -------------------------------------- BULK EMPLOYEE --------------------------------------


    def test_bulk_employee_post_create_valid(self):
        url = reverse('bulk_employee')
        valid_data = {
            "action": "CREATE",
            "employees": [
                {
                    "name": "József",
                    "email": "jozsef@example.com",
                    "job_title": "developer",
                    "age": 30,
                    "company": str(self.company.id)
                },
                {
                    "name": "Mária",
                    "email": "maria@example.com",
                    "job_title": "tester",
                    "age": 25,
                    "company": str(self.company.id)
                },
                {
                    "name": "Zoltán",
                    "email": "zoltan@example.com",
                    "job_title": "manager",
                    "age": 28,
                    "company": str(self.company.id)
                }
            ]
        }
        response = self.client.post(url, data=valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Employee.objects.count(), 6)
        print(f"\nBulk Employee valid POST [CREATE] ✔ ({response.status_code})")

    def test_bulk_employee_post_create_invalid(self):
        url = reverse('bulk_employee')
        invalid_data = {
            "action": "CREATE",
            "employees": [
                {
                    "name": "Hibás Név",
                    "email": "hibás-email",
                    "job_title": "",
                    "age": 10,
                    "company": "invalid-uuid"
                },
                {
                    "name": "Hibás Név2",
                    "email": "hibás-email2",
                    "job_title": "",
                    "age": 10,
                    "company": "invalid-uuid2"
                },
                {
                    "name": "Hibás Név3",
                    "email": "hibás-email3",
                    "job_title": "",
                    "age": 10,
                    "company": "invalid-uuid3"
                }
            ]
        }
        response = self.client.post(url, data=invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        print(f"\nBulk Employee invalid POST [CREATE] ✔ ({response.status_code})")



    def test_bulk_employee_put_valid(self):
        url = reverse('bulk_employee')
        valid_data = [
            {
                "id": str(self.employee.id),
                "name": "Updated Employee 1",
                "email": "employee1@example.com",
                "job_title": "manager",
                "age": 40,
                "company": str(self.company.id)
            },
            {
                "id": str(self.employee2.id),
                "name": "Updated Employee 2",
                "email": "employee2@example.com",
                "job_title": "developer",
                "age": 30,
                "company": str(self.company.id)
            },
            {
                "id": str(self.employee3.id),
                "name": "Updated Employee 3",
                "email": "employee3@example.com",
                "job_title": "designer",
                "age": 28,
                "company": str(self.company.id)
            }
        ]

        response = self.client.put(url, data=valid_data, format='json')


        self.assertEqual(response.status_code, status.HTTP_200_OK)


        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], f'{len(valid_data)} employees updated.')


        self.employee.refresh_from_db()
        self.assertEqual(self.employee.name, "Updated Employee 1")
        self.assertEqual(self.employee.job_title, "manager")
        self.assertEqual(self.employee.age, 40)

        print(f"\nBulk Employee valid PUT ✔ ({response.status_code})")


    def test_bulk_employee_put_invalid(self):
        url = reverse('bulk_employee')
        invalid_data = [
            {
                "id": str(self.employee.id),
                "name": "",
                "job_title": "invalid_job_title",
                "age": 10,
                "company": str(self.company.id)
            },
            {
                "id": str(self.employee2.id),
                "name": "",
                "email": "invalid-email-format",
                "job_title": "developer",
                "age": 20,
                "company": str(self.company.id)
            },
            {
                "id": str(self.employee3.id),
                "name": "Invalid Employee",
                "email": "employee3@example.com",
                "job_title": "manager",
                "age": 15,
                "company": str(self.company.id)
            }
        ]

        response = self.client.put(url, data=invalid_data, format='json')


        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


        self.assertIn('errors', response.data)
        self.assertTrue(len(response.data['errors']) > 0)


        first_error = response.data['errors'][0]
        self.assertIn('name', first_error)
        self.assertIn('job_title', first_error)
        self.assertIn('age', first_error)

        print(f"\nBulk Employee invalid PUT ✔ ({response.status_code})")



    def test_bulk_employee_patch_valid(self):
        url = reverse('bulk_employee')
        valid_data = [
            {
                "id": str(self.employee.id),
                "name": "Updated Employee 1",
                "job_title": "manager"
            },
            {
                "id": str(self.employee.id),
                "name": "Updated Employee 2",
                "job_title": "developer"
            },
            {
                "id": str(self.employee.id),
                "name": "Updated Employee 3",
                "job_title": "designer"
            }
        ]

        response = self.client.patch(url, data=valid_data, format='json')


        self.assertEqual(response.status_code, status.HTTP_200_OK)


        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], f'{len(valid_data)} employees updated.')


        self.employee.refresh_from_db()
        self.assertEqual(self.employee.name, "Updated Employee 1")
        self.assertEqual(self.employee.job_title, "manager")

        print(f"\nBulk Employee valid PATCH ✔ ({response.status_code})")



    def test_bulk_employee_patch_invalid(self):
        url = reverse('bulk_employee')
        invalid_data = [
            {
                "id": str(self.employee.id),
                "name": "",
                "job_title": "invalid_job_title"
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Invalid Employee 2",
                "job_title": "developer",
                "email": "invalid-email-format"
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Invalid Employee 3",
                "job_title": "manager",
                "age": 10
            }
        ]

        response = self.client.patch(url, data=invalid_data, format='json')


        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

 
        self.assertIn('errors', response.data)
        self.assertTrue(len(response.data['errors']) > 0)


        first_error = response.data['errors'][0]
        self.assertIn('name', first_error)
        self.assertIn('job_title', first_error)

        print(f"\nBulk Employee invalid PATCH ✔ ({response.status_code})")

    def test_bulk_employee_delete_valid(self):
        url = reverse('bulk_employee')
        valid_data = {
            "action": "DELETE",
            "employees": [
                {"id": str(self.employee.id)},
                {"id": str(self.employee2.id)},
                {"id": str(self.employee3.id)}
            ]
        }
        response = self.client.post(url, data=valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Employee.objects.count(), 0)
        print(f"\nBulk Employee valid POST [DELETE] ✔ ({response.status_code})")



    def test_bulk_employee_delete_invalid(self):
        url = reverse('bulk_employee')
        non_existing_id = str(uuid.uuid4())
        invalid_data = {
            "action": "DELETE",
            "employees": [
                {"id": non_existing_id},
                {"id": non_existing_id},
                {"id": non_existing_id}
            ]
        }
        response = self.client.post(url, data=invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        print(f"\nBulk Employee invalid POST [DELETE] ✔ ({response.status_code})")