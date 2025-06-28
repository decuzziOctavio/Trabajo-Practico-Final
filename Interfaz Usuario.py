import sqlite3
import requests
import matplotlib.pyplot as plt
import pandas as pd
import random

OBJETIVOS_VALIDOS = ["Ganar masa muscular", "Perder peso", "Mantenimiento"]
RESTRICCIONES_VALIDAS = [
    "Sin gluten", "Diabetes", "Vegano", "Vegetariano"
]

class Usuario:
    def __init__(self, id, nombre, email, objetivo, restricciones, peso, altura, planPremium=False):
        self.id = id
        self.nombre = nombre
        self.email = email
        self.objetivo = objetivo
        self.restricciones = restricciones
        self.peso = peso
        self.altura = altura
        self.planPremium = planPremium

    def __str__(self):
        return (
            f'\n\tNombre: {self.nombre}'
            f'\n\tEmail: {self.email}'
            f'\n\tPeso: {self.peso}'
            f'\n\tAltura: {self.altura}'
            f'\n\tObjetivo: {self.objetivo}'
            f'\n\tRestricciones: {self.restricciones}'
            f'\n\tPlan Premium: {self.planPremium}'
        )

def generar_usuarios():
    conn = sqlite3.connect('eatwise.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM usuarios')
    filas = cursor.fetchall()
    conn.close()
    lista_usuarios = []

    for fila in filas:
        nuevoUsuario = Usuario(
            id=fila[0], nombre=fila[1], email=fila[2],
            objetivo=fila[3], restricciones=fila[4],
            peso=fila[5], altura=fila[6], planPremium=bool(fila[7])
        )
        lista_usuarios.append(nuevoUsuario)

    return lista_usuarios

def login(usuarios):
    print("*" * 20, "BIENVENIDO A EATWISE!!", "*" * 20)

    while True:
        log = input("Escriba su nombre para logearse: ")

        if log:
            for usuario in usuarios:
                if usuario.nombre == log:
                    print("✅ Usuario Encontrado.")
                    return usuario
            print("❌ Usuario no encontrado.")
        else:
            return None

def menu():
    print("\n--- MENÚ ---")
    print("Asegurese de especificar el tipo de producto y la marca en cada ocasion, de ser posible.")
    print("1. Evaluar alimento según objetivo")
    print("2. Evaluar alimento según restricciones")
    print("3. Información nutricional (OpenFoodFacts)")
    print("4. Calcular IMC")
    print("5. Gráfico de nutrientes")
    print("6. Gráfico según objetivo (disponible para Plan premium)")
    print("7. Analizar Membresias")
    print("0. Salir")
    while True:
        try:
            opcion = int(input("Seleccione una opción: "))
            if opcion < 0 or opcion > 7:
                raise ValueError
            break
        except ValueError:
            print("La opción debe de ser un valor numerico dentro del rango!")
            continue
    return opcion

def obtener_info_producto(nombre_producto):
    url = "https://world.openfoodfacts.org/cgi/search.pl"
    params = {
        "search_terms": nombre_producto,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": 1
    }

    resp = requests.get(url, params=params)

    if resp.status_code != 200:
        print("Error de conexión con API.")
        return None

    productos = resp.json().get("products", [])

    if not productos:
        print("No se encontraron productos.")
        return None

    prod = productos[0]
    nutrimentos = prod.get("nutriments", {})
    ingredientes = prod.get("ingredients_text", "")

    datos = nutrimentos.copy()
    datos["ingredients_text"] = ingredientes

    return datos

def evaluar_alimento_por_objetivo(usuario):
    mostrar_promo_no_premium(usuario)
    nombre = input("Producto a evaluar: ")
    datos = obtener_info_producto(nombre)

    if not datos:
        return

    cal = float(datos.get("energy-kcal_100g", 0))
    prot = float(datos.get("proteins_100g", 0))

    if usuario.objetivo == "Ganar masa muscular":
        if prot > 10:
            print("✅ Rico en proteínas.")
        else:
            print("⚠️ Bajo en proteínas.")

    elif usuario.objetivo == "Perder peso":
        if cal < 200:
            print("✅ Bajo en calorías.")
        else:
            print("⚠️ Calórico.")

    elif usuario.objetivo == "Mantenimiento":
        if cal < 300:
            print("ℹ️ Compatible con mantenimiento.")
        else:
            print("️ℹ️ Consuma con regularidad.")

def evaluar_alimento_por_restriccion(usuario):
    mostrar_promo_no_premium(usuario)
    nombre = input("Producto a evaluar (intente especificar marcas): ")
    datos = obtener_info_producto(nombre)

    if not datos:
        return

    ing = datos.get("ingredients_text", "")
    if not ing:
        print("⚠️ No se encontró información de ingredientes.")
        return

    ing = ing.lower()
    r = usuario.restricciones.lower()

    if r == "sin gluten":
        palabras_clave = ["trigo", "wheat", "avena", "oats", "cebada", "barley", "centeno", "rye"]
        if any(palabra in ing for palabra in palabras_clave):
            print("❌ Contiene gluten.")
            return

    elif r == "vegano":
        palabras_clave = ["leche", "milk", "huevo", "egg", "carne", "meat", "queso", "cheese", "manteca", "butter"]
        if any(palabra in ing for palabra in palabras_clave):
            print("❌ No es vegano.")
            return

    elif r == "vegetariano":
        palabras_clave = ["carne", "meat", "gelatina", "gelatin"]
        if any(palabra in ing for palabra in palabras_clave):
            print("❌ No es vegetariano.")
            return

    elif r == "diabetes":
        palabras_clave = ["azúcar", "sugar", "jarabe", "syrup", "glucosa", "glucose", "fructosa", "fructose"]
        if any(palabra in ing for palabra in palabras_clave):
            print("⚠️ Puede tener alto contenido de azúcar.")
            return

    print("✅ Compatible con la restricción.")


def buscar_nutrientes_por_nombre(usuario,nombre_producto, cantidad_resultados=1):
    mostrar_promo_no_premium(usuario)
    url = "https://world.openfoodfacts.org/cgi/search.pl"
    params = {
        "search_terms": nombre_producto,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": cantidad_resultados
    }

    respuesta = requests.get(url, params=params)

    if respuesta.status_code != 200:
        print("Error al buscar producto.")
        return

    productos = respuesta.json().get("products", [])

    if not productos:
        print("No se encontraron productos.")
        return

    for producto in productos:
        nombre = producto.get("product_name", "Desconocido")
        nutrientes = producto.get("nutriments", {})
        if not nombre or not nutrientes:
            continue  # saltar productos incompletos

        print(f"\n📦 Producto (informacion cada 100g): {nombre}")
        print(f"⚡ Calorías: {nutrientes.get('energy-kcal_100g', 'N/A')}")
        print(f"🥄 Azúcar: {nutrientes.get('sugars_100g', 'N/A')}")
        print(f"🧂 Sodio: {nutrientes.get('sodium_100g', 'N/A')}")
        print(f"🥑 Grasas: {nutrientes.get('fat_100g', 'N/A')}")
        print(f"🥬 Fibra: {nutrientes.get('fiber_100g', 'N/A')}")
        print(f"🅰️ Nutri-Score: {producto.get('nutrition_grades', 'N/A')}")

def calcular_imc(usuario):
    mostrar_promo_no_premium(usuario)
    imc = usuario.peso / (usuario.altura ** 2)
    print(f"\n📊 IMC: {round(imc, 2)}")

    if imc < 18.5:
        print("⚠️ Bajo peso")
    elif imc < 25:
        print("✅ Peso normal")
    elif imc < 30:
        print("⚠️ Sobrepeso")
    else:
        print("⚰️🫄🏻 Obesidad")

def mostrar_nutrientes_en_grafico(nombre_producto):
    datos = obtener_info_producto(nombre_producto)

    if not datos:
        return

    labels = ['Proteínas', 'Grasas', 'Carbohidratos', 'Fibra']
    valores = [
        float(datos.get('proteins_100g', 0)),
        float(datos.get('fat_100g', 0)),
        float(datos.get('carbohydrates_100g', 0)),
        float(datos.get('fiber_100g', 0))
    ]

    plt.figure(figsize=(6, 6))
    plt.pie(valores, labels=labels, autopct='%1.1f%%', startangle=90)
    plt.title(f'Composición nutricional de {nombre_producto}')
    plt.axis('equal')
    plt.show()

def mostrar_grafico_objetivo(usuario):
    if not usuario.planPremium:
        return print("Opcion solo disponible para Plan Premium!")
    objetivos = {
        "Ganar masa muscular": {"Proteínas": 0.4, "Carbohidratos": 0.45, "Grasas": 0.15},
        "Perder peso": {"Proteínas": 0.6, "Carbohidratos": 0.2, "Grasas": 0.2},
        "Mantenimiento": {"Proteínas": 0.4, "Carbohidratos": 0.4, "Grasas": 0.2}
    }

    if usuario.objetivo not in objetivos:
        print("⚠️ Objetivo no reconocido.")
        return

    datos = objetivos[usuario.objetivo]
    df = pd.DataFrame.from_dict(datos, orient='index', columns=['Proporción'])
    df.plot.pie(y='Proporción', autopct='%1.1f%%', legend=False, figsize=(6, 6))
    plt.title(f'Distribución ideal para {usuario.objetivo}')
    plt.ylabel('')
    plt.show()

def analizar_membresias():
    conn = sqlite3.connect('eatwise.db')
    df = pd.read_sql_query("SELECT planpremium FROM usuarios", conn)
    conn.close()

    conteo = df['planpremium'].value_counts().rename(index={0: 'No Premium', 1: 'Premium'})
    print("\nEstado de membresía de los usuarios:")
    print(conteo)

    plt.figure(figsize=(10, 6))
    conteo.plot(kind='bar', color=['red', 'green'], width=0.5)
    plt.title('Usuarios Premium vs No Premium')
    plt.ylabel('Cantidad de usuarios')
    plt.xticks(rotation=0)
    plt.yticks(range(0, 11, 1))
    plt.ylim(0, 10)
    plt.show()

def mostrar_promo_no_premium(usuario):
    if not usuario.planPremium:
        promosNopremium = [
            "PROMOCIÓN, APROVECHE: Desde Buenos Aires, UCEMA te lanza al futuro: estudiá Analítica de Negocios y Negocios Digitales con Sergio Sirotinsky. Convertí tu pasión por los datos en impacto real. Inscribite ya.",
            "PROMOCIÓN, APROVECHE: Desde el corazón del Microcentro porteño, El Buen Libro te sirve los sánguches de milanesa más épicos. Pan casero, milanesa crocante y sabor inolvidable. Vení y probalo vos mismo.",
            "PROMOCIÓN, APROVECHE: Samsung Argentina te prende fuego este Hot Sale: hasta 40 por ciento de descuento en smartphones, televisores y más. Ingresá a samsung.com.ar y llevate lo último en tecnología.",
            "PROMOCIÓN, APROVECHE: Desde Argentina al Mundial de Clubes 2025 en Miami: vuelo, hotel y entradas desde 899 dólares. Solo en Despegar.com. Viví el mejor fútbol bajo el sol de Florida."
        ]
        print(random.choice(promosNopremium))

if __name__ == '__main__':
    usuarios = generar_usuarios()
    usuario_logueado = login(usuarios)

    if usuario_logueado:
        while True:
            opcion = menu()

            if opcion == 1:
                evaluar_alimento_por_objetivo(usuario_logueado)

            elif opcion == 2:
                evaluar_alimento_por_restriccion(usuario_logueado)

            elif opcion == 3:
                nombre = input("Producto a buscar: ")
                buscar_nutrientes_por_nombre(usuario_logueado,nombre, cantidad_resultados=3)

            elif opcion == 4:
                calcular_imc(usuario_logueado)

            elif opcion == 5:
                nombre = input("Producto a graficar: ")
                mostrar_nutrientes_en_grafico(nombre)

            elif opcion == 6:
                mostrar_grafico_objetivo(usuario_logueado)

            elif opcion == 7:
                analizar_membresias()

            elif opcion == 0:
                print("¡Hasta luego!")
                break

            else:
                print("❌ Opción inválida")