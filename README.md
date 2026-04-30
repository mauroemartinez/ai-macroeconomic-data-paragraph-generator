# 🤖 AI Macroeconomic Data Paragraph Generator 📊

**⚠️ NOTA IMPORTANTE:** Este proyecto es una **versión previa y modular** que será integrada en el pipeline principal del RPA. Ver el proyecto completo en: [RPA - Exchange Rate Scrapping Automatic Mailing](https://github.com/mauroemartinez/RPA-exchange-rate-scrapping-automatic-mailing)

---

## 📝 Descripción

Este módulo genera **párrafos de análisis profesional en español** sobre datos macroeconómicos argentinos utilizando la **API de Gemini** (Google's Generative AI). Toma datos diarios de tipos de cambio, tasas de interés y riesgo país, y produce análisis narrativo que será integrado en reportes de mailing automático.

El sistema es **inteligente**: solo menciona indicadores cuando su variación es significativa, evitando ruido en la narrativa. Implementa **API key rotation** para manejar cuotas de forma robusta.

---

## 🚀 Funcionalidades Clave

* **Generación de Análisis con IA:** Integración con Gemini API para narrativa profesional y contextualizada.
* **Monitoreo Inteligente de Indicadores:**
  - **BCRA TEA:** Se menciona solo si varía más de ±0.2% (cambio significativo)
  - **FED TEA:** Se menciona ante cualquier cambio (rara vez varía)
  - **Tipos de Cambio (Blue, MEP, Billete):** Análisis de tendencias de 25 ruedas (~ 1 mes hábil)
  - **Riesgo País:** Comparativas diarias y mensuales

* **Manejo Robusto de Errores:** Rotación automática entre múltiples API keys ante límites de cuota (HTTP 429).
* **Data Processing:** Validación de historial mínimo, cálculos de variación y formateo de contexto.
* **Output en Español:** Párrafos profesionales, secos y disclaimer legal incluido.

---

## 🛠️ Stack Tecnológico

### 🤖 AI & APIs
* `google-genai`: Cliente oficial de Gemini API con manejo de excepciones específicas.
* `google-api-core`: Utilidades para detectar errores de cuota (ResourceExhausted).

### 🧮 Procesamiento de Datos
* `pandas`: Lectura y manipulación de CSV, ordenamiento temporal.
* `python-dotenv`: Gestión segura de API keys en variables de entorno.

### 🔒 Seguridad
* Variables de entorno para API keys (nunca hardcodeadas).
* Soporte para múltiples keys con failover automático.

---

## 📊 Flujo de Datos

```
CSV (datos históricos)
    ↓
Validación de historial mínimo (26 registros)
    ↓
Extracción de puntos de control (hoy, ayer, hace 25 ruedas)
    ↓
Cálculo de variaciones y contexto
    ↓
Evaluación de umbrales (BCRA TEA >0.2%, FED TEA >0%)
    ↓
Construcción de prompt inteligente
    ↓
Llamada a Gemini API (con rotación de keys)
    ↓
Párrafo generado en español
```

---

## 📥 Requisitos

### Archivos Necesarios
- **CSV con datos históricos** que contenga columnas:
  - `Fecha`
  - `TCV_Blue` (Dólar Blue)
  - `TCV_MEP` (Dólar MEP)
  - `TCV_Billete` (Dólar Billete)
  - `bcra_tea` (Tasa Efectiva del BCRA)
  - `fed_tea` (Tasa Efectiva de la FED)
  - `riesgo_pais` (Risk País en puntos)

### Variables de Entorno (.env)
```
RUTA_BBDD=C:\ruta\a\tu\archivo.csv
GEMINI_API_KEY_1=tu_api_key_1
GEMINI_API_KEY_2=tu_api_key_2
```

Obtén tus API keys en: [Google AI Studio](https://aistudio.google.com)

---

## 🚀 Uso

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python "AI Paragraph.py"
```

**Salida esperada:**
```
🤖 Analizando datos del 29/04/2026...

--- PÁRRAFO GENERADO ---
Al 29/04/2026, la brecha del 1,56% entre el Blue ($1415,0) y el MEP 
($1437,45) posiciona al paralelo como opción más económica siendo la 
tendencia descendente mensual del 1,39%. El riesgo país consolida una 
baja de 3 puntos a 584 pts, mientras que la TEA del BCRA (48,07%) 
evidencia aceleración mensual del 7,52%...
```

---

## 🔄 Lógica de Decisión de Indicadores

| Indicador | Condición | Acción |
|-----------|-----------|--------|
| BCRA TEA | Variación diaria > ±0.2% | ✅ Incluir en párrafo |
| BCRA TEA | Variación diaria ≤ ±0.2% | ❌ Omitir |
| FED TEA | Variación diaria > 0% (cualquier cambio) | ✅ Incluir en párrafo |
| FED TEA | Sin variación | ❌ Omitir |
| Blue/MEP/Billete | Siempre | ✅ Siempre incluir |
| Riesgo País | Siempre | ✅ Siempre incluir |

---

## 🛡️ Manejo de Errores

### API Key Rotation
Si la API Key 1 alcanza límite de cuota (HTTP 429):
```
⚠️ Key 1 agotada (Cuota excedida).
🔄 Reintentando con la siguiente API Key...
```

Si todas las keys se agotan:
```
❌ Se agotaron todas las API Keys por límite de cuota (429).
```

Otros errores (red, validación, etc.) detienen la ejecución inmediatamente.

---

## 🏔️ Roadmap: Integración en RPA Principal

- [ ] **Fase 1 (Actual):** Modulo standalone de generación de párrafos ✅
- [ ] **Fase 2:** Integración en pipeline de mailing automático
- [ ] **Fase 3:** Almacenamiento de párrafos generados en SQL Server

Ver: [RPA-exchange-rate-scrapping-automatic-mailing](https://github.com/mauroemartinez/RPA-exchange-rate-scrapping-automatic-mailing)

---

## 📚 Estructura del Código

```python
# 1. Configuración Inicial
load_dotenv()
RUTA = os.getenv("RUTA_BBDD")
API_KEYS = [key1, key2]

# 2. Función de Failover
def generar_con_failover(prompt):
    # Rotación inteligente de keys

# 3. Procesamiento de Datos
df = pd.read_csv(RUTA)
# Extracción de puntos de control

# 4. Evaluación de Umbrales
tea_var_diaria = calc_var(tea_hoy, ayer['bcra_tea'])
tea_strong_change = abs(tea_var_diaria) > 0.2

# 5. Construcción de Prompt
prompt_final = f"""Actuá como analista financiero..."""

# 6. Generación
reporte = generar_con_failover(prompt_final)
```

---

## 🔐 Consideraciones de Seguridad

✅ **API keys en `.env`**, nunca en código fuente
✅ **`.gitignore`** excluye `.env` y datos sensibles
✅ Manejo seguro de excepciones sin exponer tokens
✅ Validación de datos antes de procesamiento

---

## 📬 Contribuciones & Feedback

Este es un módulo educativo y de portfolio. Si tienes sugerencias o quieres contribuir:
- 📧 martinezmauroezequiel@gmail.com
- 🔗 [LinkedIn](https://www.linkedin.com/in/mauro-martinez-ba/)

---

**Última actualización:** Abril 2026  
**Versión:** 1.0 (Pre-release para integración)
