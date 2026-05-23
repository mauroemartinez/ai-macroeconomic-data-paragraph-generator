import os
import pandas as pd
from dotenv import load_dotenv
from google import genai
from google.api_core import exceptions # Para detectar específicamente el error 429
from sqlalchemy import create_engine
import urllib

# Configuración Inicial
load_dotenv()
RUTA = os.getenv("RUTA_BBDD")
API_KEYS = [os.getenv("GEMINI_API_KEY_1"), os.getenv("GEMINI_API_KEY_2")]
params = urllib.parse.quote_plus(
    r'DRIVER={ODBC Driver 17 for SQL Server};'
    r'SERVER=localhost\SQLEXPRESS;'
    r'DATABASE=MacroeconomicAnalytics;'
    r'Trusted_Connection=yes;'
)
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

def generar_con_failover(prompt):
    """
    Intenta generar el reporte. Si recibe un error 429, rota a la siguiente Key.
    Si el error es de otro tipo o se agotan las Keys, detiene la ejecución.
    """
    for i, key in enumerate(API_KEYS):
        if not key: 
            continue
        
        try:
            client = genai.Client(api_key=key)
            # Usamos gemini-2.0-flash para máxima calidad de análisis
            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=prompt
            )
            return response.text # Éxito: corta el loop y devuelve el texto
        except exceptions.ResourceExhausted:
            # ERROR 429 detectado
            print(f"⚠️ Key {i+1} agotada (Cuota excedida).")
            if i == len(API_KEYS) - 1:
                raise Exception("❌ Se agotaron todas las API Keys por límite de cuota (429).")
            print("🔄 Reintentando con la siguiente API Key...")
            continue 

        except Exception as e:
            # Otros errores (Red, lógica, etc.): No rota la Key, avisa y corta.
            print(f"❌ Error técnico inesperado: {e}")
            raise e

# Procesamiento de Datos
try:
    query = """
        SELECT 
            Fecha, TCV_MEP, TCV_Blue, TCV_Billete, riesgo_pais, bcra_tea, fed_tea 
        FROM Fact_Mercado_Macro 
        ORDER BY Fecha ASC;
    """
    
    print("🔌 Conectando a SQL Server para extraer historial...")
    
    df = pd.read_sql(query, con=engine)
    
    # Limpieza estándar por si las dudas
    df.columns = df.columns.str.strip()
    df['Fecha'] = pd.to_datetime(df['Fecha']) 

    # Validación de historial mínimo para comparar 25 ruedas (aprox. 1 mes hábil)
    if len(df) < 26:
        raise Exception(f"Historial insuficiente en SQL Server. La tabla solo tiene {len(df)} registros.")
    # Validación de historial mínimo para comparar 25 ruedas (aprox. 1 mes hábil)
    if len(df) < 26:
        raise Exception(f"Historial insuficiente. El CSV solo tiene {len(df)} registros.")

    # Definición de puntos de control
    hoy = df.iloc[-1]       # Última cotización
    ayer = df.iloc[-2]      # Cotización anterior
    hace_25 = df.iloc[-26]  # Hace 25 cotizaciones
    
    # Definimos variables clave para el análisis
    mep_hoy = hoy['TCV_MEP']
    blue_hoy = hoy['TCV_Blue']
    tea_hoy = hoy['bcra_tea']
    fed_tea_hoy = hoy['fed_tea']
 
    # Calculamos la brecha absoluta entre blue y mep
    brecha_valor = abs(((blue_hoy / mep_hoy) - 1) * 100)
    mas_bajo = "Blue" if blue_hoy < mep_hoy else "MEP"
    
    # Cálculos de variaciones para el prompt
    def calc_var(actual, previo):
        return ((actual / previo) - 1) * 100

    contexto_masticado = {
        "fecha": hoy['Fecha'].strftime('%d/%m/%Y'),
        "blue_val": f"${blue_hoy}",
        "blue_stats": f"(Día: {calc_var(blue_hoy, ayer['TCV_Blue']):+.2f}% | Mes: {calc_var(blue_hoy, hace_25['TCV_Blue']):+.2f}%)",
        "mep_val": f"${mep_hoy}",
        "brecha_porc": f"{brecha_valor:.2f}%",
        "opcion_barata": mas_bajo,
        "riesgo_pais": {
            "actual": f"{hoy['riesgo_pais']} pts",
            "dif_diaria": f"{hoy['riesgo_pais'] - ayer['riesgo_pais']:+} pts",
            "dif_25_ruedas": f"{hoy['riesgo_pais'] - hace_25['riesgo_pais']:+} pts"
        },
        "billete": {
            "actual": f"${hoy['TCV_Billete']}",
            "var_diaria": f"{calc_var(hoy['TCV_Billete'], ayer['TCV_Billete']):+.2f}%",
            "var_25_ruedas": f"{calc_var(hoy['TCV_Billete'], hace_25['TCV_Billete']):+.2f}%"
        },
        "tea": {
            "actual": f"{tea_hoy:.2f}%",
            "var_diaria": f"{calc_var(tea_hoy, ayer['bcra_tea']):+.2f}%",
            "var_25_ruedas": f"{calc_var(tea_hoy, hace_25['bcra_tea']):+.2f}%"
        },
        "fed_tea": {
            "actual": f"{fed_tea_hoy:.2f}%",
            "var_diaria": f"{calc_var(fed_tea_hoy, ayer['fed_tea']):+.2f}%"
        }
    }

    # Check if TEA change is significant (>0.5% absolute daily variation)
    tea_var_diaria = calc_var(tea_hoy, ayer['bcra_tea'])
    tea_strong_change = abs(tea_var_diaria) > 0.2    
    # Check if FED TEA changed at all (any movement)
    fed_var_diaria = calc_var(fed_tea_hoy, ayer['fed_tea'])
    fed_any_change = abs(fed_var_diaria) > 0
    # Prompt con instrucciones de formato estrictas
    prompt_final = f"""
    Actuá como analista financiero Senior. Redactá un párrafo de 3-4 líneas.
    DATOS REALES AL {contexto_masticado['fecha']}:
    - Blue: {contexto_masticado['blue_val']} {contexto_masticado['blue_stats']}
    - MEP: {contexto_masticado['mep_val']}
    - Brecha: {contexto_masticado['brecha_porc']}
    - Más barato hoy: {contexto_masticado['opcion_barata']}
    - Billete: {contexto_masticado['billete']['actual']} (Día: {contexto_masticado['billete']['var_diaria']} | Mes: {contexto_masticado['billete']['var_25_ruedas']})
    - Riesgo País: {contexto_masticado['riesgo_pais']['actual']} (Día: {contexto_masticado['riesgo_pais']['dif_diaria']} | Mes: {contexto_masticado['riesgo_pais']['dif_25_ruedas']})
{f"- TEA BCRA: {contexto_masticado['tea']['actual']} (Día: {contexto_masticado['tea']['var_diaria']} | Mes: {contexto_masticado['tea']['var_25_ruedas']})" if tea_strong_change else ""}
{f"- TEA FED: {contexto_masticado['fed_tea']['actual']} (Día: {contexto_masticado['fed_tea']['var_diaria']})" if fed_any_change else ""}

    Instrucciones obligatorias:
    1. Al mencionar la brecha, escribí explícitamente los valores de ambos, ejemplo: "entre el Blue ({contexto_masticado['blue_val']}) y el MEP ({contexto_masticado['mep_val']})".
    2. Para la comparativa de precios, usá la frase "siendo la opción más económica de las dos".
    3. Mantené el análisis de tendencia de 25 ruedas para Blue, Billete y Riesgo País{f", y Tasa Efectiva del BCRA" if tea_strong_change else ""} cuando sea significativo{f". Para la Tasa Efectiva de la FED, mencionála únicamente si cambió, sin requerir análisis de tendencia mensual" if fed_any_change else ""}.
    4. Tono seco, profesional y recordá que no somos asesores financieros.
    """
    print(f"🤖 Analizando datos del {contexto_masticado['fecha']}...")
    reporte = generar_con_failover(prompt_final)
    
    print("\n--- PÁRRAFO GENERADO ---")
    print(reporte)
    
except Exception as e:
    print(f"\n❌ Proceso interrumpido: {e}")