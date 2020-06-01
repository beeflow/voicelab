# VoiceLab - rest server / client

Zadanie rekrutacyjne

## Założenia

### Serwer REST API przetwarzający audio
* serwer przyjmuje pliki wav
* przyjęte pliki są kolejkowane w kolejce do przetwarzania
* dla każdego pliku są obliczane dane potrzebne do wygenerowania tzw. waveform
* pliki oraz wszystkie obliczone dane (włącznie z metadanymi plików) powinny być archiwizowane w odpowiedni sposób
* API umożliwia pobieranie wyników, prostej listy statusów przetwarzania oraz generowanie obrazków przedstawiających waveform

### Wymagania
* serwer powinien być asynchroniczny, napisany w języku Python
* baza danych Postgresql, obsługa asynchroniczna (najlepiej z wykorzystaniem ORM’a)
* można wykorzystać dockery
* do serwera powinna być dołączona osobna prosta aplikacja kliencka (bez GUI) komunikująca się z serwerem
* prosta dokumentacja API

## Uruchomienie

Serwis pracuje na dockerach przy użyciu docker-compose, które należy zainstalować.

Uruchomienie dockerów:

```bash
$ docker-compose up
```

Jeżeli serwis nie chce się uruchomić, może okazać się, że docker-compose nie uruchamia serwisów w odpowiedniej kolejności. Wtedy należy uruchomić

```bash
$ docker-compose up postgres rabbit
```

a potem 

```bash
$ docker-compose up vl_server
```

```bash
$ docker-compose up -d
```

spowoduje uruchomienie wszystkich kontenerów w tle.

## Przetwarzanie plików

Aby można było przetwarzać pliki wave, należy wejść na system w dockerze
```bash
$ docker-compose exec vl_server /bin/bash
```
i uruchomić konsumera poprzez polecenie
```bash
./manage.py db_queue_consumer
```
## Klient

Skrypt klienta można uruchomić poprzez
```bash
./client.py
```
 Wyświetli się pomoc, która objaśni sposób używania skryptu.
 
## Enkdpointy API

### Upload pliku

Pozwala na dodanie nowego pliku na serwer do kolejki przetwarzania.

* **URL**

  /api/v1/upload

* **Method:**

  `POST`
  
*  **URL Params**
  
  None

* **Data Params**

   **Required:**
 
   `file` - plik
   
* **Success Response:**

  * **Code:** 201 <br />
    **Content:** `{ "id" : "91985bc2-2f8a-4a67-9fd1-9d2c396e6b30" }`

* **Error Response:**

  * **Code:** 400 BAD REQUEST <br />
    **Content:** ''<br />
    **Content-Type** `application/api-problem+json`
    
```bash
$ curl -X POST -F "file=@file_example_WAV_1MG.wav;type=audio/wave" /api/v1/upload
```

### Stronicowana lista zadań wraz ze statusami

* **URL**

  /api/v1/tasks/{:page}

* **Method:**

  `GET`
  
*  **URL Params**
  
   page = 1
   
* **Success Response:**

  * **Code:** 200 <br />
    **Content:** 
```json
{
    "data": [
        {
            "job": {
                "@uri": "/api/v1/tasks/2181643b-5651-47c1-b2b8-0c0cef57b61e",
                "id": "2181643b-5651-47c1-b2b8-0c0cef57b61e",
                "name": "file_example_WAV_1MG.wav",
                "job-status": "SUCCESS"
            }
        },
...
    ],
    "links": {
        "self": "/api/v1/tasks/1",
        "next": "/api/v1/tasks/2",
        "meta": {
            "count": 33
        }
    }
}
```

* **Error Response:**

  * **Code:** 404 NOT FOUND <br />
    **Content:** ''<br />
    **Content-Type** `application/api-problem+json`
    
```bash
$ curl -X GET /api/v1/taks
$ curl -X GET /api/v1/taks/1
```

### Informacje o wybranym zadaniu

* **URL**

  /api/v1/tasks/{:uuid}

* **Method:**

  `GET`
  
*  **URL Params**
  
   uuid = 2181643b-5651-47c1-b2b8-0c0cef57b61e
   
* **Success Response:**

  * **Code:** 200 <br />
    **Content:** 
```json
{
    "job": {
        "@uri": "/api/v1/tasks/2181643b-5651-47c1-b2b8-0c0cef57b61e",
        "id": "2181643b-5651-47c1-b2b8-0c0cef57b61e",
        "name": "file_example_WAV_1MG.wav",
        "job-status": "SUCCESS"
    }
}
```

* **Error Response:**

  * **Code:** 404 NOT FOUND <br />
    **Content:** ''<br />
    **Content-Type** `application/api-problem+json`
    
```bash
$ curl -X GET /api/v1/taks/2181643b-5651-47c1-b2b8-0c0cef57b61e
```


### Pobranie audiogramu

* **URL**

  /api/v1/waveform/{:uuid}

* **Method:**

  `GET`
  
*  **URL Params**
  
   uuid = 2181643b-5651-47c1-b2b8-0c0cef57b61e
   
* **Success Response:**

  * **Code:** 200 <br />
    **Content:** 
```json
{
    "@file": "staticfiles/2181643b-5651-47c1-b2b8-0c0cef57b61e.png"
}
```

* **Error Response:**

  * **Code:** 404 NOT FOUND <br />
    **Content:** ''<br />
    **Content-Type** `application/api-problem+json`
    
```bash
$ curl -X GET /api/v1/waveform/2181643b-5651-47c1-b2b8-0c0cef57b61e
```
