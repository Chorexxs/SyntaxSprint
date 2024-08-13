from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
import requests
import random
from django.http import JsonResponse
from .models import TypingTestResult
from django.db.models import Avg
# Create your views here.


def get_python_function(request):
    functions = [
        {
            "name": "Imprimir un Mensaje",
            "code": "print(\"Hello, World!\")"
        },
        {
            "name": "Suma de Dos Números",
            "code": "def add(a, b):\n    return a + b"
        },
        {
            "name": "Verificar Paridad",
            "code": "def is_even(num):\n    return num % 2 == 0"
        },
        {
            "name": "Calcular Factorial",
            "code": "import math\n\ndef factorial(n):\n    return math.factorial(n)"
        },
        {
            "name": "Leer Archivo de Texto",
            "code": "with open('file.txt', 'r') as file:\n    content = file.read()\n    print(content)"
        },
        {
            "name": "Escribir en un Archivo",
            "code": "with open('file.txt', 'w') as file:\n    file.write(\"Hello, File!\")"
        },
        {
            "name": "Ordenar una Lista",
            "code": "numbers = [3, 1, 4, 1, 5, 9]\nsorted_numbers = sorted(numbers)"
        },
        {
            "name": "Filtrar Lista por Condición",
            "code": "numbers = [1, 2, 3, 4, 5]\neven_numbers = list(filter(lambda x: x % 2 == 0, numbers))"
        },
        {
            "name": "Mapear Lista a Nuevos Valores",
            "code": "numbers = [1, 2, 3, 4]\nsquared_numbers = list(map(lambda x: x**2, numbers))"
        },
        {
            "name": "Generar una Secuencia de Números",
            "code": "sequence = range(10)"
        },
        {
            "name": "Calcular Promedio de una Lista",
            "code": "def average(lst):\n    return sum(lst) / len(lst)"
        },
        {
            "name": "Generar Número Aleatorio",
            "code": "import random\nrandom_number = random.randint(1, 100)"
        },
        {
            "name": "Leer Entrada del Usuario",
            "code": "user_input = input(\"Enter something: \")"
        },
        {
            "name": "Convertir String a Entero",
            "code": "num = int(\"123\")"
        },
        {
            "name": "Convertir Entero a String",
            "code": "str_num = str(123)"
        },
        {
            "name": "Eliminar Espacios en Blanco",
            "code": "s = \"  Hello, World!  \"\ncleaned = s.strip()"
        },
        {
            "name": "Reemplazar Texto en un String",
            "code": "s = \"Hello, World!\"\nreplaced = s.replace(\"World\", \"Python\")"
        },
        {
            "name": "Dividir un String",
            "code": "s = \"apple,banana,cherry\"\nfruits = s.split(',')"
        },
        {
            "name": "Unir una Lista de Strings",
            "code": "words = [\"Hello\", \"World\"]\nsentence = ' '.join(words)"
        },
        {
            "name": "Encontrar la Longitud de una Lista",
            "code": "length = len([1, 2, 3, 4, 5])"
        },
        {
            "name": "Concatenar Dos Listas",
            "code": "list1 = [1, 2, 3]\nlist2 = [4, 5, 6]\nconcatenated = list1 + list2"
        },
        {
            "name": "Crear un Diccionario",
            "code": "person = {\"name\": \"Alice\", \"age\": 30}"
        },
        {
            "name": "Usar Excepciones para Manejar Errores",
            "code": "try:\n    result = 10 / 0\nexcept ZeroDivisionError:\n    print(\"Cannot divide by zero!\")"
        },
        {
            "name": "Definir una Clase Básica",
            "code": "class Person:\n    def __init__(self, name, age):\n        self.name = name\n        self.age = age\n\n    def greet(self):\n        return f\"Hello, my name is {self.name}.\""
        },
        {
            "name": "Uso de Propiedades en Clases",
            "code": "class Circle:\n    def __init__(self, radius):\n        self._radius = radius\n\n    @property\n    def radius(self):\n        return self._radius\n\n    @radius.setter\n    def radius(self, value):\n        if value > 0:\n            self._radius = value\n        else:\n            raise ValueError(\"Radius must be positive.\")"
        },
        {
            "name": "Generadores en Python",
            "code": "def count_up_to(max):\n    count = 1\n    while count <= max:\n        yield count\n        count += 1"
        },
        {
            "name": "Leer Línea por Línea de un Archivo",
            "code": "with open('file.txt', 'r') as file:\n    for line in file:\n        print(line.strip())"
        },
        {
            "name": "Contar Palabras en un Texto",
            "code": "from collections import Counter\ntext = \"apple banana apple\"\nword_count = Counter(text.split())"
        },
        {
            "name": "Usar Decoradores",
            "code": "def my_decorator(func):\n    def wrapper():\n        print(\"Something is happening before the function.\")\n        func()\n        print(\"Something is happening after the function.\")\n    return wrapper\n\n@my_decorator\n def say_hello():\n    print(\"Hello!\")\n\nsay_hello()"
        },
        {
            "name": "Leer JSON de un Archivo",
            "code": "import json\n\nwith open('data.json', 'r') as file:\n    data = json.load(file)"
        },
        {
            "name": "Escribir JSON en un Archivo",
            "code": "import json\n\ndata = {\"name\": \"Alice\", \"age\": 30}\nwith open('data.json', 'w') as file:\n    json.dump(data, file)"
        },
        {
            "name": "Uso de args y kwargs",
            "code": "def func(*args, **kwargs):\n    print(\"Arguments:\", args)\n    print(\"Keyword arguments:\", kwargs)\n\nfunc(1, 2, 3, name=\"Alice\", age=30)"
        },
        {
            "name": "Ordenar Diccionario por Claves",
            "code": "dict_items = {'b': 2, 'a': 1, 'c': 3}\nsorted_dict = dict(sorted(dict_items.items()))"
        },
        {
            "name": "Ordenar Diccionario por Valores",
            "code": "dict_items = {'b': 2, 'a': 1, 'c': 3}\nsorted_dict = dict(sorted(dict_items.items(), key=lambda item: item[1]))"
        },
        {
            "name": "Uso de map y filter",
            "code": "numbers = [1, 2, 3, 4, 5]\nsquared = list(map(lambda x: x**2, numbers))\nevens = list(filter(lambda x: x % 2 == 0, numbers))"
        },
        {
            "name": "Uso de zip para Combinar Listas",
            "code": "names = [\"Alice\", \"Bob\", \"Charlie\"]\nscores = [85, 90, 88]\ncombined = list(zip(names, scores))"
        },
        {
            "name": "Conversión de Fecha a String",
            "code": "from datetime import datetime\n\nnow = datetime.now()\ndate_string = now.strftime(\"%Y-%m-%d %H:%M:%S\")"
        },
        {
            "name": "Conversión de String a Fecha",
            "code": "from datetime import datetime\n\ndate_string = \"2024-07-27\"\ndate_object = datetime.strptime(date_string, \"%Y-%m-%d\")"
        },
        {
            "name": "Uso de defaultdict",
            "code": "from collections import defaultdict\n\ndd = defaultdict(int)\ndd['key1'] += 1"
        },
        {
            "name": "Uso de namedtuple",
            "code": "from collections import namedtuple\n\nPerson = namedtuple('Person', 'name age')\nalice = Person(name=\"Alice\", age=30)"
        },
        {
            "name": "Uso de Counter",
            "code": "from collections import Counter\n\nelements = [\"a\", \"b\", \"a\", \"c\", \"b\", \"a\"]\ncounter = Counter(elements)"
        },
        {
            "name": "Verificar Tipo de Objeto",
            "code": "is_string = isinstance(\"Hello\", str)"
        },
        {
            "name": "Uso de enumerate",
            "code": "for index, value in enumerate([\"a\", \"b\", \"c\"]):\n    print(index, value)"
        },
        {
            "name": "Uso de socket para Crear un Servidor TCP",
            "code": "import socket\n\nserver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\nserver_socket.bind(('localhost', 12345))\nserver_socket.listen(1)\nclient_socket, client_address = server_socket.accept()"
        },
        {
            "name": "Uso de argparse para Procesar Argumentos de Línea de Comando",
            "code": "import argparse\n\nparser = argparse.ArgumentParser()\nparser.add_argument('number', type=int)\nargs = parser.parse_args()\nprint(args.number)"
        },
        {
            "name": "Uso de shutil para Copiar Archivos",
            "code": "import shutil\n\nshutil.copy('source.txt', 'destination.txt')"
        },
        {
            "name": "Uso de logging para Registrar Mensajes",
            "code": "import logging\n\nlogging.basicConfig(level=logging.INFO)\nlogging.info('This is an info message.')"
        },
        {
            "name": "Uso de requests para Hacer Solicitudes HTTP",
            "code": "import requests\n\nresponse = requests.get('https://api.example.com/data')\ndata = response.json()"
        },
        {
            "name": "Uso de pandas para Leer CSV",
            "code": "import pandas as pd\n\ndf = pd.read_csv('file.csv')"
        },
        {
            "name": "Uso de numpy para Operaciones Matriciales",
            "code": "import numpy as np\n\nmatrix = np.array([[1, 2], [3, 4]])\ntranspose = np.transpose(matrix)"
        },
        {
            "name": "Uso de matplotlib para Crear un Gráfico",
            "code": "import matplotlib.pyplot as plt\n\nx = [1, 2, 3, 4]\ny = [1, 4, 9, 16]\nplt.plot(x, y)\nplt.show()"
        },
        {
            "name": "Uso de sqlite3 para Conectar a una Base de Datos",
            "code": "import sqlite3\n\nconn = sqlite3.connect('database.db')\ncursor = conn.cursor()"
        },
        {
            "name": "Uso de asyncio para Tareas Asíncronas",
            "code": "import asyncio\n\nasync def say_hello():\n    print('Hello')\n    await asyncio.sleep(1)\n    print('World')\n\nasyncio.run(say_hello())"
        },
        {
            "name": "Uso de concurrent.futures para Ejecución en Hilos",
            "code": "from concurrent.futures import ThreadPoolExecutor\n\n def task(n):\n    return n * n\n\nwith ThreadPoolExecutor() as executor:\n    results = executor.map(task, [1, 2, 3, 4])\n    print(list(results))"
        },
        {
            "name": "Uso de collections.deque para Cola de Datos",
            "code": "from collections import deque\n\nqueue = deque([1, 2, 3])\nqueue.append(4)\nqueue.popleft()"
        },
        {
            "name": "Uso de datetime para Operaciones con Fechas y Horas",
            "code": "from datetime import datetime\n\nnow = datetime.now()\nprint(now)"
        },
        {
            "name": "Uso de timeit para Medir el Tiempo de Ejecución",
            "code": "import timeit\n\ntimeit.timeit(\"x = sum(range(10))\", number=1000)"
        },
        {
            "name": "Uso de itertools.count para Contadores Infinitos",
            "code": "import itertools\n\nfor i in itertools.count(start=5, step=2):\n    if i > 15:\n        break\n    print(i)"
        },
        {
            "name": "Uso de functools.lru_cache para Cache de Funciones",
            "code": "from functools import lru_cache\n\n@lru_cache(maxsize=32)\ndef fib(n):\n    if n < 2:\n        return n\n    return fib(n-1) + fib(n-2)"
        },
        {
            "name": "Uso de collections para Contar Elementos",
            "code": "from collections import Counter\n\ntext = \"apple orange banana apple apple orange\"\ncounter = Counter(text.split())\nprint(\"Word counts:\", counter)"
        },
        {
            "name": "Uso de random para Selección Aleatoria",
            "code": "import random\n\noptions = ['apple', 'banana', 'cherry']\nprint(random.choice(options))"
        },
        {
            "name": "Uso de decimal para Cálculos de Precisión Decimal",
            "code": "from decimal import Decimal\n\nprice = Decimal('19.99')\ntax = Decimal('0.07')\ntotal = price + (price * tax)\nprint(total)"
        },

        # Funciones más largas (por si se añade dificultad)

        {
            "name": "Función para Verificar Primos",
            "code": "def is_prime(n):\n    \"\"\"Verifica si un número es primo.\"\"\"\n    if n <= 1:\n        return False\n    if n <= 3:\n        return True\n    if n % 2 == 0 or n % 3 == 0:\n        return False\n    i = 5\n    while i * i <= n:\n        if n % i == 0 or n % (i + 2) == 0:\n            return False\n        i += 6\n    return True\n\nprint([num for num in range(1, 50) if is_prime(num)])"
        },
        {
            "name": "Función de Ordenamiento por Inserción",
            "code": "def insertion_sort(arr):\n    \"\"\"Ordena una lista usando el algoritmo de inserción.\"\"\"\n    for i in range(1, len(arr)):\n        key = arr[i]\n        j = i - 1\n        while j >= 0 and key < arr[j]:\n            arr[j + 1] = arr[j]\n            j -= 1\n        arr[j + 1] = key\n\n\narr = [12, 11, 13, 5, 6]\ninsertion_sort(arr)\nprint(\"Sorted array:\", arr)"
        },
        {
            "name": "Servidor HTTP Básico usando http.server",
            "code": "from http.server import SimpleHTTPRequestHandler, HTTPServer\n\nclass MyHandler(SimpleHTTPRequestHandler):\n    def do_GET(self):\n        if self.path == '/':\n            self.path = 'index.html'\n        return super().do_GET()\n\nserver_address = ('', 8000)\nhttpd = HTTPServer(server_address, MyHandler)\nprint(\"Serving on port 8000...\")\nhttpd.serve_forever()"
        },
        {
            "name": "Aplicación Web Básica con Flask",
            "code": "from flask import Flask, render_template, request\n\napp = Flask(__name__)\n\n@app.route('/')\ndef home():\n    return render_template('index.html')\n\n@app.route('/submit', methods=['POST'])\ndef submit():\n    data = request.form.get('data')\n    return f\"Received: {data}\"\n\nif __name__ == '__main__':\n    app.run(debug=True)"
        },
        {
            "name": "Clase con Métodos de Clase y Estáticos",
            "code": "class MathOperations:\n    @staticmethod\n    def add(a, b):\n        return a + b\n\n    @classmethod\n    def multiply(cls, a, b):\n        return a * b\n\n\nprint(MathOperations.add(5, 7))\nprint(MathOperations.multiply(4, 6))"
        },
        {
            "name": "Manejo de Archivos CSV con csv",
            "code": "import csv\n\n def write_csv(filename, rows):\n    with open(filename, 'w', newline='') as file:\n        writer = csv.writer(file)\n        writer.writerow(['Name', 'Age'])\n        writer.writerows(rows)\n\n def read_csv(filename):\n    with open(filename, 'r') as file:\n        reader = csv.reader(file)\n        for row in reader:\n            print(row)\n\nrows = [['Alice', 30], ['Bob', 25]]\nwrite_csv('people.csv', rows)\nread_csv('people.csv')"
        },
        {
            "name": "Interacción con un Sistema de Archivos",
            "code": "import os\n\n\nos.makedirs('example_dir', exist_ok=True)\n\n\nwith open('example_dir/sample.txt', 'w') as file:\n    file.write(\"Hello, World!\")\n\n\nfiles = os.listdir('example_dir')\nprint(\"Files in directory:\", files)\n\n\nos.remove('example_dir/sample.txt')\nos.rmdir('example_dir')"
        },
        {
            "name": "Uso de argparse para Procesar Argumentos de Línea de Comando",
            "code": "import argparse\n\n def main():\n    parser = argparse.ArgumentParser(description='Process some integers.')\n    parser.add_argument('integers', metavar='N', type=int, nargs='+', help='an integer to be processed')\n    parser.add_argument('--sum', dest='accumulate', action='store_const', default=max, const=sum, help='sum the integers (default: find the max)')\n    \n    args = parser.parse_args()\n    print(args.accumulate(args.integers))\n\nif __name__ == '__main__':\n    main()"
        },
        {
            "name": "Crear un Generador de Fibonacci",
            "code": "def fibonacci_generator():\n    a, b = 0, 1\n    while True:\n        yield a\n        a, b = b, a + b\n\n\nfib_gen = fibonacci_generator()\nfor _ in range(10):\n    print(next(fib_gen))"
        },
        {
            "name": "Uso de unittest para Pruebas Unitarias",
            "code": "import unittest\n\n def multiply(a, b):\n    return a * b\n\nclass TestMultiply(unittest.TestCase):\n    def test_multiply(self):\n        self.assertEqual(multiply(2, 3), 6)\n        self.assertEqual(multiply(-1, 1), -1)\n        self.assertEqual(multiply(0, 100), 0)\n\nif __name__ == '__main__':\n    unittest.main()"
        },
        {
            "name": "Uso de jsonschema para Validación de JSON",
            "code": "import json\nfrom jsonschema import validate, ValidationError\n\nschema = {\n    \"type\": \"object\",\n    \"properties\": {\n        \"name\": {\"type\": \"string\"},\n        \"age\": {\"type\": \"integer\"}\n    },\n    \"required\": [\"name\", \"age\"]\n}\n\n data = {\"name\": \"Alice\", \"age\": 30}\n\ntry:\n    validate(instance=data, schema=schema)\n    print(\"JSON is valid.\")\nexcept ValidationError as e:\n    print(\"JSON is invalid:\", e)"
        },
        {
            "name": "Creación de un Juego de Adivinanza",
            "code": "import random\n\n def guess_number():\n    number_to_guess = random.randint(1, 100)\n    tries = 0\n    while True:\n        guess = int(input(\"Guess the number (1-100): \"))\n        tries += 1\n        if guess < number_to_guess:\n            print(\"Too low!\")\n        elif guess > number_to_guess:\n            print(\"Too high!\")\n        else:\n            print(f\"Congratulations! You guessed the number in {tries} tries.\")\n            break\n\n guess_number()"
        },
        {
            "name": "Uso de asyncio para Tareas Concurrentes",
            "code": "import asyncio\n\nasync def say_after(delay, message):\n    await asyncio.sleep(delay)\n    print(message)\n\nasync def main():\n    await asyncio.gather(\n        say_after(1, 'Hello'),\n        say_after(2, 'World'),\n    )\n\nasyncio.run(main())"
        },
        {
            "name": "Manipulación de Imágenes con Pillow",
            "code": "from PIL import Image\n\n# Abrir una imagen\nimage = Image.open('example.jpg')\nimage.show()\n\n# Convertir a escala de grises\ngray_image = image.convert('L')\ngray_image.save('gray_example.jpg')"
        },
        {
            "name": "Manipulación de Datos con pandas",
            "code": "import pandas as pd\n\n\n data = {\n    'Name': ['Alice', 'Bob', 'Charlie'],\n    'Age': [30, 25, 35]\n}\ndf = pd.DataFrame(data)\n\n\n print(df)\n\n\n filtered_df = df[df['Age'] > 30]\nprint(filtered_df)"
        },
        {
            "name": "Uso de re para Expresiones Regulares",
            "code": "import re\n\ntext = \"The quick brown fox jumps over the lazy dog.\"\npattern = r'\\b\\w{5}\\b' \nmatches = re.findall(pattern, text)\nprint(\"5-letter words:\", matches)"
        },
        {
            "name": "Creación de una Clase con Propiedades",
            "code": "class Person:\n    def __init__(self, name, age):\n        self._name = name\n        self._age = age\n\n    @property\n    def name(self):\n        return self._name\n\n    @name.setter\n    def name(self, value):\n        self._name = value\n\n    @property\n    def age(self):\n        return self._age\n\n    @age.setter\n    def age(self, value):\n        if value < 0:\n            raise ValueError(\"Age cannot be negative\")\n        self._age = value\n\n# Ejemplo de uso\np = Person(\"Alice\", 30)\np.age = 31\nprint(p.name, p.age)"
        },
        {
            "name": "Manipulación Avanzada de Fechas con dateutil",
            "code": "from dateutil import parser, relativedelta\n\ndate1 = parser.parse(\"2024-07-27\")\ndate2 = parser.parse(\"2024-12-25\")\ndelta = relativedelta.relativedelta(date2, date1)\n\nprint(f\"Difference: {delta.years} years, {delta.months} months, {delta.days} days\")"
        },
        {
            "name": "Uso de functools para Decoradores",
            "code": "from functools import wraps\n\n def debug(func):\n     @wraps(func)\n     def wrapper(*args, **kwargs):\n         result = func(*args, **kwargs)\n         print(f\"{func.__name__}({args}, {kwargs}) = {result}\")\n         return result\n     return wrapper\n\n @debug\n def add(a, b):\n     return a + b\n\n add(3, 5)"
        },
        {
            "name": "Implementación de una Cola con queue.Queue",
            "code": "from queue import Queue\n\n q = Queue()\n q.put(1)\n q.put(2)\n q.put(3)\n\n while not q.empty():\n     item = q.get()\n     print(item)"
        },
        {
            "name": "Uso de tkinter para Crear una Interfaz Gráfica Básica",
            "code": "import tkinter as tk\n\n def on_button_click():\n     label.config(text=\"Button Clicked!\")\n\n root = tk.Tk()\n root.title(\"Simple GUI\")\n\n label = tk.Label(root, text=\"Hello, Tkinter!\")\n label.pack()\n\n button = tk.Button(root, text=\"Click Me\", command=on_button_click)\n button.pack()\n\n root.mainloop()"
        },
        {
            "name": "Uso de email para Enviar Correos Electrónicos",
            "code": "import smtplib\nfrom email.mime.text import MIMEText\nfrom email.mime.multipart import MIMEMultipart\n\n def send_email(to_email, subject, body):\n     from_email = 'your_email@example.com'\n     password = 'your_password'\n\n     msg = MIMEMultipart()\n     msg['From'] = from_email\n     msg['To'] = to_email\n     msg['Subject'] = subject\n\n     msg.attach(MIMEText(body, 'plain'))\n\n     with smtplib.SMTP('smtp.example.com', 587) as server:\n         server.starttls()\n         server.login(from_email, password)\n         server.sendmail(from_email, to_email, msg.as_string())\n\n send_email('recipient@example.com', 'Test Subject', 'This is a test email.')"
        },
        {
            "name": "Implementación de un Protocolo de Cliente TCP",
            "code": "import socket\n\n def client_program():\n     client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\n     client_socket.connect(('localhost', 12345))\n     \n     message = 'Hello, Server!'\n     client_socket.send(message.encode())\n     \n     response = client_socket.recv(1024).decode()\n     print('Received from server:', response)\n     \n     client_socket.close()\n\n client_program()"
        },
        {
            "name": "Uso de pytz para Manejo de Zonas Horarias",
            "code": "from datetime import datetime\nimport pytz\n\n timezone = pytz.timezone('America/New_York')\nlocalized_time = timezone.localize(datetime.now())\nprint(\"Localized time:\", localized_time)\n\nutc_time = pytz.utc.localize(datetime.utcnow())\nprint(\"UTC time:\", utc_time)"
        },
        {
            "name": "Creación de un DataFrame con pandas y numpy",
            "code": "import pandas as pd\nimport numpy as np\n\n df = pd.DataFrame({\n    'A': np.random.rand(10),\n    'B': np.random.rand(10),\n    'C': np.random.rand(10)\n})\n\nprint(df)\n\nmean = df.mean()\nprint(\"\\nMean of each column:\")\nprint(mean)"
        },
        {
            "name": "Manejo de Archivos JSON con json",
            "code": "import json\n\n data = {\n    'name': 'Alice',\n    'age': 30,\n    'city': 'Wonderland'\n}\n\n\nwith open('data.json', 'w') as f:\n    json.dump(data, f, indent=4)\n\n\nwith open('data.json', 'r') as f:\n    loaded_data = json.load(f)\n    print(loaded_data)"
        },
        {
            "name": "Uso de socket para Crear un Servidor TCP Simple",
            "code": "import socket\n\n def server_program():\n    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\n    server_socket.bind(('localhost', 12345))\n    server_socket.listen(1)\n\n    print(\"Server listening on port 12345...\")\n    conn, addr = server_socket.accept()\n    print(\"Connection from:\", addr)\n    \n    data = conn.recv(1024).decode()\n    print(\"Received:\", data)\n    \n    conn.send(\"Hello, Client!\".encode())\n    conn.close()\n\n server_program()"
        },
        {
            "name": "Uso de pandas para Leer y Escribir CSV",
            "code": "import pandas as pd\n\n data = {\n    'Name': ['Alice', 'Bob', 'Charlie'],\n    'Age': [30, 25, 35]\n}\n df = pd.DataFrame(data)\n df.to_csv('people.csv', index=False)\n\n df_read = pd.read_csv('people.csv')\n print(df_read)"
        },
        {
            "name": "Uso de schedule para Programar Tareas",
            "code": "import schedule\nimport time\n\n def job():\n    print(\"Job executed!\")\n\n schedule.every(10).seconds.do(job)\n\n while True:\n    schedule.run_pending()\n    time.sleep(1)"
        },
        {
            "name": "Uso de timeit para Medir el Tiempo de Ejecución",
            "code": "import timeit\n\n def test():\n    return sum(range(100))\n\n execution_time = timeit.timeit(test, number=10000)\n print(f\"Execution time: {execution_time} seconds\")"
        },
        {
            "name": "Uso de dataclasses para Crear Clases de Datos",
            "code": "from dataclasses import dataclass\n\n @dataclass\n class Person:\n     name: str\n     age: int\n\n person = Person(name=\"Alice\", age=30)\n print(person)"
        },
        {
            "name": "Creación de una Clase con Métodos y Atributos",
            "code": "class Dog:\n    def __init__(self, name, age):\n        self.name = name\n        self.age = age\n\n    def bark(self):\n        return f\"{self.name} says woof!\"\n\n\ndog = Dog(name=\"Rex\", age=5)\nprint(dog.bark())"
        },
        {
            "name": "Uso de django para Crear una Vista Simple",
            "code": "from django.http import HttpResponse\n\n def home(request):\n     return HttpResponse(\"Hello, Django!\")"
        },
        {
            "name": "Uso de requests para Realizar Peticiones HTTP",
            "code": "import requests\n\nresponse = requests.get('https://api.github.com')\nprint(response.json())"
        },
        {
            "name": "Uso de matplotlib para Crear un Gráfico Simple",
            "code": "import matplotlib.pyplot as plt\n\nx = [1, 2, 3, 4, 5]\ny = [1, 4, 9, 16, 25]\n\nplt.plot(x, y)\nplt.xlabel('x')\nplt.ylabel('y')\nplt.title('Simple Plot')\nplt.show()"
        },
        {
            "name": "Uso de seaborn para Crear un Gráfico con Datos",
            "code": "import seaborn as sns\nimport matplotlib.pyplot as plt\n\n# Cargar el conjunto de datos 'iris'\ndata = sns.load_dataset('iris')\n\n# Crear un gráfico de dispersión\nsns.scatterplot(x='sepal_length', y='sepal_width', data=data, hue='species')\nplt.show()"
        },
        {
            "name": "Uso de sqlalchemy para Crear una Base de Datos",
            "code": "from sqlalchemy import create_engine, Column, Integer, String\nfrom sqlalchemy.ext.declarative import declarative_base\nfrom sqlalchemy.orm import sessionmaker\n\n# Crear una clase base para el modelo\nBase = declarative_base()\n\n# Definir el modelo de datos\nclass User(Base):\n    __tablename__ = 'users'\n    id = Column(Integer, primary_key=True)\n    name = Column(String)\n    age = Column(Integer)\n\n# Crear la base de datos y la tabla\nengine = create_engine('sqlite:///example.db')\nBase.metadata.create_all(engine)\n\n# Crear una sesión para interactuar con la base de datos\nSession = sessionmaker(bind=engine)\nsession = Session()\n\n# Añadir un nuevo usuario\nnew_user = User(name='Alice', age=30)\nsession.add(new_user)\nsession.commit()"
        },
        {
            "name": "Uso de jsonschema para Validar JSON",
            "code": "import jsonschema\nfrom jsonschema import validate\n\nschema = {\n    \"type\": \"object\",\n    \"properties\": {\n        \"name\": {\"type\": \"string\"},\n        \"age\": {\"type\": \"number\"}\n    },\n    \"required\": [\"name\", \"age\"]\n}\n\n data = {\"name\": \"Alice\", \"age\": 30}\nvalidate(instance=data, schema=schema)"
        },
        {
            "name": "Uso de http.server para Crear un Servidor HTTP Simple",
            "code": "from http.server import SimpleHTTPRequestHandler, HTTPServer\n\nPORT = 8000\n\nclass MyHandler(SimpleHTTPRequestHandler):\n    def do_GET(self):\n        self.send_response(200)\n        self.send_header('Content-type', 'text/html')\n        self.end_headers()\n        self.wfile.write(b\"Hello, HTTP!\")\n\nhttpd = HTTPServer(('localhost', PORT), MyHandler)\nprint(f\"Serving on port {PORT}\")\nhttpd.serve_forever()"
        },
        {
            "name": "Uso de dataclasses para Crear Clases de Datos",
            "code": "from dataclasses import dataclass\n\n@dataclass\nclass Point:\n    x: int\n    y: int\n\np = Point(10, 20)\nprint(p)"
        },
        {
            "name": "Uso de pygame para Crear una Ventana de Juego",
            "code": "import pygame\nimport sys\n\npygame.init()\nscreen = pygame.display.set_mode((640, 480))\npygame.display.set_caption(\"Simple Pygame Window\")\n\nwhile True:\n    for event in pygame.event.get():\n        if event.type == pygame.QUIT:\n            pygame.quit()\n            sys.exit()\n\n    screen.fill((0, 0, 0))\n    pygame.display.flip()"
        },
        {
            "name": "Uso de pickle para Serializar y Deserializar Objetos",
            "code": "import pickle\n\ndata = {'key': 'value'}\nwith open('data.pkl', 'wb') as f:\n    pickle.dump(data, f)\n\nwith open('data.pkl', 'rb') as f:\n    loaded_data = pickle.load(f)\n    print(loaded_data)"
        },
        {
            "name": "Uso de scikit-learn para Entrenamiento de Modelos",
            "code": "from sklearn.datasets import load_iris\nfrom sklearn.model_selection import train_test_split\nfrom sklearn.ensemble import RandomForestClassifier\nfrom sklearn.metrics import accuracy_score\n\n data = load_iris()\nX, y = data.data, data.target\nX_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)\n\n model = RandomForestClassifier()\nmodel.fit(X_train, y_train)\npredictions = model.predict(X_test)\nprint(\"Accuracy:\", accuracy_score(y_test, predictions))"
        },
        {
            "name": "Uso de dataclasses para Crear y Comparar Instancias",
            "code": "from dataclasses import dataclass\n\n@dataclass\nclass Product:\n    name: str\n    price: float\n\nproduct1 = Product(name=\"Laptop\", price=999.99)\nproduct2 = Product(name=\"Laptop\", price=999.99)\n\nprint(product1 == product2)"
        },
        {
            "name": "Uso de websockets para Crear un Servidor WebSocket",
            "code": "import asyncio\nimport websockets\n\nasync def echo(websocket, path):\n    async for message in websocket:\n        await websocket.send(message)\n\nstart_server = websockets.serve(echo, \"localhost\", 8765)\n\nasyncio.get_event_loop().run_until_complete(start_server)\nasyncio.get_event_loop().run_forever()"
        },
        {
            "name": "Uso de paramiko para Conectar a un Servidor SSH",
            "code": "import paramiko\n\nclient = paramiko.SSHClient()\nclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())\nclient.connect('hostname', username='user', password='password')\n\nstdin, stdout, stderr = client.exec_command('ls')\nprint(stdout.read().decode())\n\nclient.close()"
        },
        {
            "name": "Uso de typing para Tipado Estático",
            "code": "from typing import List, Tuple\n\n def process_data(data: List[int]) -> Tuple[int, int]:\n     return min(data), max(data)\n\n print(process_data([1, 2, 3, 4, 5]))"
        },
    ]
    selected_function = random.choice(functions)
    return JsonResponse(selected_function)


def index(request):
    return render(request, "index.html")


def signup(request):
    if request.method == "POST":
        email = request.POST["email"]
        username = request.POST["username"]
        password = request.POST["password"]
        password2 = request.POST["password2"]

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, "Ya existe este email")
                return redirect("signup")
            elif User.objects.filter(username=username).exists():
                messages.info(request, "El nombre de usuario ya existe")
                return redirect(signup)
            else:
                user = User.objects.create_user(
                    username=username, email=email, password=password)
                user.save()

                # Autentificando al usuario
                user_login = auth.authenticate(
                    username=username, password=password)
                auth.login(request, user_login)
                return redirect("/")

        else:
            messages.info(request, "La contraseña no coincide")
            return redirect("signup")

    else:
        return render(request, "signup.html")


def login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = auth.authenticate(
            username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect("/")
        else:
            messages.info(request, "El Usuario o la contraseña no existe")
            return redirect("login")
    return render(request, "login.html")


@login_required(login_url="/")
def logout(request):
    auth.logout(request)
    return redirect("/")


@login_required
def save_typing_test_result(request):
    if request.method == 'POST':
        wpm = float(request.POST.get('wpm', 0))
        accuracy = float(request.POST.get('accuracy', 0))

        # Guardar el resultado en la base de datos
        TypingTestResult.objects.create(
            user=request.user,
            wpm=wpm,
            accuracy=accuracy
        )

        return JsonResponse({"message": "Resultado guardado exitosamente"})
    return JsonResponse({"error": "Método no permitido"}, status=405)


@login_required
def profile(request):
    # Filtrar los resultados del usuario autenticado, ordenados por fecha descendente
    results = TypingTestResult.objects.filter(
        user=request.user).order_by('-date')

    # Calcular los promedios de WPM y precisión
    avg_wpm = results.aggregate(Avg('wpm'))['wpm__avg']
    avg_accuracy = results.aggregate(Avg('accuracy'))['accuracy__avg']

    # Preparar el contexto para pasar a la plantilla
    context = {
        'on_profile_page': True,  # Este campo puede ser útil para personalizar la navegación
        'results': results,
        'avg_wpm': avg_wpm,
        'avg_accuracy': avg_accuracy,
    }

    # Renderizar la plantilla con el contexto
    return render(request, 'profile.html', context)
