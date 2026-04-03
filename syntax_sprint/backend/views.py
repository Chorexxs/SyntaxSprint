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
import json
# Create your views here.


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
import json


# Create your views here


def get_python_function(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        language = data.get('language', 'python')
    else:
        language = 'python'

    # Code snippets by language
    code_snippets = {
        'python': [
            {"name": "Hello World", "code": "print(\"Hello, World!\")"},
            {"name": "Function Definition", "code": "def add(a, b):\n    return a + b"},
            {"name": "List Comprehension", "code": "squares = [x**2 for x in range(10)]"},
            {"name": "Class Definition", "code": "class Person:\n    def __init__(self, name):\n        self.name = name"},
            {"name": "Dictionary Operations", "code": "d = {\"a\": 1, \"b\": 2}\nprint(d.get(\"a\"))"},
            {"name": "Exception Handling", "code": "try:\n    x = 1 / 0\nexcept ZeroDivisionError:\n    print(\"Error\")"},
            {"name": "Lambda Function", "code": "double = lambda x: x * 2"},
            {"name": "File Reading", "code": "with open('file.txt', 'r') as f:\n    content = f.read()"},
            {"name": "Decorator", "code": "def decorator(func):\n    return func\n\n@decorator\ndef hello():\n    pass"},
            {"name": "Generator", "code": "def gen():\n    yield 1\n    yield 2"},
            {"name": "Context Manager", "code": "class MyContext:\n    def __enter__(self): return self\n    def __exit__(self, *args): pass"},
            {"name": "Async Function", "code": "async def fetch():\n    return await data"},
            {"name": "Type Hints", "code": "def greet(name: str) -> str:\n    return f\"Hi {name}\""},
            {"name": " dataclass", "code": "from dataclasses import dataclass\n\n@dataclass\nclass Point:\n    x: int\n    y: int"},
            {"name": "Enum", "code": "from enum import Enum\n\nclass Color(Enum):\n    RED = 1\n    GREEN = 2"},
        ],
        'javascript': [
            {"name": "Console Log", "code": "console.log(\"Hello, World!\");"},
            {"name": "Arrow Function", "code": "const add = (a, b) => a + b;"},
            {"name": "Array Map", "code": "const doubled = nums.map(n => n * 2);"},
            {"name": "Class Definition", "code": "class Person {\n  constructor(name) {\n    this.name = name;\n  }\n}"},
            {"name": "Async/Await", "code": "async function fetchData() {\n  const res = await fetch(url);\n  return res.json();\n}"},
            {"name": "Destructuring", "code": "const { name, age } = person;"},
            {"name": "Spread Operator", "code": "const newArr = [...arr1, ...arr2];"},
            {"name": "Promise", "code": "const promise = new Promise((resolve) => {\n  setTimeout(() => resolve(\"done\"), 1000);\n});"},
            {"name": "Template Literals", "code": "const msg = `Hello, ${name}!`;"},
            {"name": "Object Methods", "code": "const keys = Object.keys(obj);\nconst values = Object.values(obj);"},
            {"name": "Array Filter", "code": "const evens = nums.filter(n => n % 2 === 0);"},
            {"name": "Array Reduce", "code": "const sum = nums.reduce((a, b) => a + b, 0);"},
            {"name": "Optional Chaining", "code": "const value = user?.profile?.name;"},
            {"name": "Nullish Coalescing", "code": "const x = null ?? \"default\";"},
            {"name": "Import/Export", "code": "import { func } from './module';\nexport const value = 42;"},
        ],
        'typescript': [
            {"name": "Interface", "code": "interface User {\n  name: string;\n  age: number;\n}"},
            {"name": "Type Alias", "code": "type ID = string | number;"},
            {"name": "Generic Function", "code": "function identity<T>(arg: T): T {\n  return arg;\n}"},
            {"name": "Enum", "code": "enum Direction {\n  Up,\n  Down,\n  Left,\n  Right\n}"},
            {"name": "Union Types", "code": "function printId(id: string | number): void {\n  console.log(id);\n}"},
            {"name": "Mapped Types", "code": "type Readonly<T> = {\n  readonly [P in keyof T]: T[P];\n};"},
            {"name": "Class with Generics", "code": "class Container<T> {\n  private value: T;\n  constructor(value: T) { this.value = value; }\n}"},
            {"name": "Type Guards", "code": "function isString(val: unknown): val is string {\n  return typeof val === 'string';\n}"},
            {"name": "Implements Interface", "code": "class Animal implements Named {\n  name: string = \"\";\n}"},
            {"name": "Namespace", "code": "namespace MyMath {\n  export function add(a: number, b: number): number {\n    return a + b;\n  }\n}"},
            {"name": "Decorator", "code": "@Component({ selector: 'app' })\nclass MyClass {}"},
            {"name": "Utility Types", "code": "type PartialUser = Partial<User>;\ntype RequiredUser = Required<User>;"},
            {"name": "Keyof Operator", "code": "type KeyOf = keyof User;"},
            {"name": "Asynchronous", "code": "async function getData(): Promise<User[]> {\n  return await fetch(url).then(r => r.json());\n}"},
            {"name": "Module Export", "code": "export type { User };\nexport default class App {}"},
        ],
        'html': [
            {"name": "Basic Structure", "code": "<!DOCTYPE html>\n<html>\n<head>\n  <title>Page</title>\n</head>\n<body></body>\n</html>"},
            {"name": "Div Element", "code": "<div class=\"container\">\n  <h1>Hello</h1>\n</div>"},
            {"name": "Form Element", "code": "<form action=\"/submit\" method=\"POST\">\n  <input type=\"text\" name=\"name\">\n  <button type=\"submit\">Submit</button>\n</form>"},
            {"name": "Table", "code": "<table>\n  <thead><tr><th>Name</th></tr></thead>\n  <tbody><tr><td>Value</td></tr></tbody>\n</table>"},
            {"name": "Image", "code": "<img src=\"photo.jpg\" alt=\"Description\" loading=\"lazy\">"},
            {"name": "Link", "code": "<a href=\"https://example.com\" target=\"_blank\">Link</a>"},
            {"name": "List", "code": "<ul>\n  <li>Item 1</li>\n  <li>Item 2</li>\n</ul>"},
            {"name": "Input Types", "code": "<input type=\"email\" required>\n<input type=\"password\">\n<input type=\"date\">"},
            {"name": "Semantic Tags", "code": "<header><nav></nav></header>\n<main><article></article></main>\n<footer></footer>"},
            {"name": "Data Attributes", "code": "<div data-user-id=\"123\" data-role=\"admin\">Content</div>"},
            {"name": "SVG Inline", "code": "<svg width=\"100\" height=\"100\">\n  <circle cx=\"50\" cy=\"50\" r=\"40\"/>\n</svg>"},
            {"name": "Audio/Video", "code": "<video controls>\n  <source src=\"video.mp4\" type=\"video/mp4\">\n</video>"},
            {"name": "Meta Tags", "code": "<meta name=\"description\" content=\"Description\">\n<meta name=\"viewport\" content=\"width=device-width\">"},
            {"name": "Script Tag", "code": "<script src=\"app.js\" defer></script>"},
            {"name": "Style Tag", "code": "<style>\n  .class { color: red; }\n</style>"},
        ],
        'css': [
            {"name": "Selector", "code": ".container { display: flex; }"},
            {"name": "Flexbox", "code": ".flex {\n  display: flex;\n  justify-content: center;\n  align-items: center;\n}"},
            {"name": "Grid", "code": ".grid {\n  display: grid;\n  grid-template-columns: repeat(3, 1fr);\n  gap: 1rem;\n}"},
            {"name": "Media Query", "code": "@media (max-width: 768px) {\n  .mobile { display: block; }\n}"},
            {"name": "Pseudo-classes", "code": ".btn:hover { background: blue; }\n.input:focus { border-color: blue; }"},
            {"name": "Animations", "code": "@keyframes fade {\n  from { opacity: 0; }\n  to { opacity: 1; }\n}\n.anim { animation: fade 1s; }"},
            {"name": "Variables", "code": ":root {\n  --primary: #007bff;\n  --spacing: 16px;\n}"},
            {"name": "Transform", "code": ".rotate { transform: rotate(45deg); }\n.scale { transform: scale(1.5); }"},
            {"name": "Transition", "code": ".hover { transition: all 0.3s ease; }"},
            {"name": "Position", "code": ".sticky { position: sticky; top: 0; }\n.absolute { position: absolute; }"},
            {"name": "Gradient", "code": ".gradient {\n  background: linear-gradient(to right, red, blue);\n}"},
            {"name": "Box Shadow", "code": ".shadow { box-shadow: 0 4px 6px rgba(0,0,0,0.1); }"},
            {"name": "Border Radius", "code": ".rounded { border-radius: 8px; }\n.circle { border-radius: 50%; }"},
            {"name": "Z-Index", "code": ".modal { position: fixed; z-index: 1000; }"},
            {"name": "Backdrop Filter", "code": ".glass { backdrop-filter: blur(10px); }"},
        ],
        'sql': [
            {"name": "SELECT", "code": "SELECT * FROM users WHERE active = true;"},
            {"name": "JOIN", "code": "SELECT u.name, o.total FROM users u\nJOIN orders o ON u.id = o.user_id;"},
            {"name": "GROUP BY", "code": "SELECT COUNT(*), status FROM orders\nGROUP BY status;"},
            {"name": "INSERT", "code": "INSERT INTO users (name, email)\nVALUES ('John', 'john@example.com');"},
            {"name": "UPDATE", "code": "UPDATE users SET active = false\nWHERE created_at < '2024-01-01';"},
            {"name": "DELETE", "code": "DELETE FROM sessions WHERE expires < NOW();"},
            {"name": "CREATE TABLE", "code": "CREATE TABLE products (\n  id SERIAL PRIMARY KEY,\n  name VARCHAR(255) NOT NULL\n);"},
            {"name": "ALTER TABLE", "code": "ALTER TABLE users ADD COLUMN phone VARCHAR(20);"},
            {"name": "INDEX", "code": "CREATE INDEX idx_email ON users(email);"},
            {"name": "SUBQUERY", "code": "SELECT * FROM users WHERE id IN (\n  SELECT user_id FROM orders\n);"},
            {"name": "CASE", "code": "SELECT CASE WHEN total > 100 THEN 'high'\n  ELSE 'low' END FROM orders;"},
            {"name": "COALESCE", "code": "SELECT COALESCE(name, 'Unknown') FROM users;"},
            {"name": "COUNT", "code": "SELECT COUNT(*) FROM orders WHERE status = 'completed';"},
            {"name": "LIMIT OFFSET", "code": "SELECT * FROM users LIMIT 10 OFFSET 20;"},
            {"name": "UNION", "code": "SELECT name FROM users\nUNION ALL SELECT name FROM admins;"},
        ],
        'java': [
            {"name": "Main Method", "code": "public static void main(String[] args) {\n  System.out.println(\"Hello\");\n}"},
            {"name": "Class", "code": "public class Person {\n  private String name;\n  public Person(String name) { this.name = name; }\n}"},
            {"name": "Interface", "code": "interface Drawable {\n  void draw();\n}"},
            {"name": "Lambda", "code": "list.forEach(item -> System.out.println(item));"},
            {"name": "Stream", "code": "list.stream().filter(x -> x > 0).collect(Collectors.toList());"},
            {"name": "Optional", "code": "String name = user.getName().orElse(\"Unknown\");"},
            {"name": "Try-Catch", "code": "try {\n  int x = Integer.parseInt(str);\n} catch (NumberFormatException e) { }"},
            {"name": "Generic Method", "code": "<T> void print(T item) { System.out.println(item); }"},
            {"name": "Enum", "code": "enum Color { RED, GREEN, BLUE }"},
            {"name": "Record", "code": "record Point(int x, int y) {}"},
            {"name": "Thread", "code": "new Thread(() -> System.out.println(\"Running\")).start();"},
            {"name": "List Operations", "code": "List<String> list = new ArrayList<>();\nlist.add(\"item\");"},
            {"name": "Map Operations", "code": "Map<String, Integer> map = new HashMap<>();\nmap.put(\"key\", 1);"},
            {"name": "Annotation", "code": "@Override\npublic String toString() { return \"\"; }"},
            {"name": "Builder Pattern", "code": "User user = User.builder()\n  .name(\"John\")\n  .build();"},
        ],
        'go': [
            {"name": "Main Function", "code": "package main\n\nfunc main() {\n  println(\"Hello\")\n}"},
            {"name": "Function", "code": "func add(a, b int) int {\n  return a + b\n}"},
            {"name": "Struct", "code": "type Person struct {\n  Name string\n  Age  int\n}"},
            {"name": "Interface", "code": "type Reader interface {\n  Read(p []byte) (n, error)\n}"},
            {"name": "Slice", "code": "nums := []int{1, 2, 3}\nnums = append(nums, 4)"},
            {"name": "Map", "code": "m := make(map[string]int)\nm[\"key\"] = 42"},
            {"name": "Goroutine", "code": "go func() {\n  // async work\n}()"},
            {"name": "Channel", "code": "ch := make(chan int)\ngo func() { ch <- 42 }()"},
            {"name": "Defer", "code": "defer file.Close()\n// work with file"},
            {"name": "Error Handling", "code": "if err != nil {\n  return err\n}"},
            {"name": "Struct Tags", "code": "type User struct {\n  Name string `json:\"name\"`\n}"},
            {"name": "Pointer", "code": "func swap(a, b *int) {\n  *a, *b = *b, *a\n}"},
            {"name": "Method", "code": "func (p Person) Greet() string {\n  return \"Hi \" + p.Name\n}"},
            {"name": "Type Assertion", "code": "if v, ok := i.(string); ok {\n  fmt.Println(v)\n}"},
            {"name": "Context", "code": "ctx, cancel := context.WithTimeout(context.Background(), time.Second)"}
        ],
    }
    
    # Get snippets for language, fallback to Python
    snippets = code_snippets.get(language, code_snippets['python'])
    selected = random.choice(snippets)
    return JsonResponse(selected)


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
                messages.info(request, "Email already exists")
                return redirect("signup")
            elif User.objects.filter(username=username).exists():
                messages.info(request, "Username already exists")
                return redirect("signup")
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
            messages.info(request, "Passwords do not match")
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
            messages.info(request, "Invalid username or password")
            return redirect("login")
    return render(request, "login.html")


@login_required(login_url="/")
def logout(request):
    auth.logout(request)
    return redirect("/")


@login_required
def save_typing_test_result(request):
    if request.method == 'POST':
        data = json.loads(request.body)  # Asegúrate de cargar los datos JSON
        wpm = data.get('wpm')
        accuracy = data.get('accuracy')

        if wpm is not None and accuracy is not None:
            TypingTestResult.objects.create(
                user=request.user,
                wpm=wpm,
                accuracy=accuracy
            )
            return JsonResponse({"message": "Resultado guardado exitosamente"})
        return JsonResponse({"error": "Datos no válidos"}, status=400)
    return JsonResponse({"error": "Método no permitido"}, status=405)


@login_required
def profile(request):
    results = TypingTestResult.objects.filter(
        user=request.user).order_by('-date')

    # Verifica que existan resultados antes de calcular los promedios
    if results.exists():
        avg_wpm = results.aggregate(Avg('wpm'))['wpm__avg']
        avg_accuracy = results.aggregate(Avg('accuracy'))['accuracy__avg']
    else:
        avg_wpm = 0
        avg_accuracy = 0

    context = {
        'on_profile_page': True,
        'results': results,
        'avg_wpm': avg_wpm or 0,
        'avg_accuracy': avg_accuracy or 0,
    }

    return render(request, 'profile.html', context)
