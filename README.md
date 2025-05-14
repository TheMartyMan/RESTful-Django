# RESTful Django

**Lokális futtatás**

Előfeltételek:
- Python
- pipenv (virtuális környezet) telepítve, shellben fut


1. Projekt mappához navigélás
    ```
	cd <project_mappa>
	```
	
2. Függőségek telepítése
        ```
   		pip install --upgrade pip
		```
		```
   		pip install -r requirements.txt
        ```


3. Adatbázis beállítása
	• Az adatbázis beállítások a settings.py részben módosítható
```
DATABASES = {
	'default': {
	'ENGINE': 'django.db.backends.postgresql',
	'NAME': 'dbname',
	'USER': 'username',
	'PASSWORD': 'password',
	'HOST': 'host',
	'PORT': 'port',
	}
}
```

4. Áttelepítéseket
    ```
	python manage.py makemigrations && python manage.py migrate
    ```

	
5. Szerver futtatása
    ```
	python manage.py runserver <port>
    ```
	



**Az alkalmazás futtatása a Dockerrel**

Előfeltételek:
- A Docker és a Docker Compose telepítve van


1. Projekt mappához navigélás
    ```
	cd <project_folder>
    ```
	
2. Konténer buildelése és futtatása
    ```
	docker-compose up --build
    ```
