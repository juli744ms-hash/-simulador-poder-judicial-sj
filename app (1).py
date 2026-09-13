# -*- coding: utf-8 -*-
"""
Simulador de Examen de Ingreso al Poder Judicial - Provincia de San Juan
=========================================================================
Versión "modo exigente": réplica más fiel de las condiciones de un
simulador comercial (tiempos que cortan la prueba solos, corrección
palabra por palabra haciendo clic sobre el error, errores generados
al azar en cada intento, penalización por corregir palabras que
estaban bien, banco de preguntas teóricas ampliado).

Basado en las bases oficiales del "Concurso de Aspirantes para Ingresar
al Poder Judicial 2026" (Corte de Justicia de San Juan):

    5 instancias eliminatorias:
      1. Prueba de dactilografía: 4 minutos para transcribir correctamente
         100 palabras de un texto jurídico.
      2. Prueba de ortografía: 5 minutos para corregir un texto con
         errores ortográficos.
      3. Curso virtual obligatorio (Escuela Judicial) - no evaluable aquí.
      4. Prueba de conocimientos teóricos: cuadernillo de 100 preguntas,
         75 minutos, se requieren 71 respuestas correctas para aprobar
         (umbral general del concurso: 71.00%).
      5. Entrevista personal obligatoria - no evaluable aquí.

IMPORTANTE: las preguntas del Módulo 3 son de elaboración propia, redactadas
a partir del "CUADERNILLO 2026" oficial de la Corte de Justicia de San Juan
(los 9 temas del programa del concurso: Derecho Constitucional, Constitución
Provincial, Organización del Poder Judicial de San Juan, Ministerio Público,
Derecho Civil y Procesal Civil, Derecho Laboral y Procesal Laboral, Derecho
de las Familias, Derecho Penal y Procesal Penal, y Normativa de Género). No
son las 100 preguntas exactas del examen real (que la Corte no publica), pero
sí cubren el mismo temario y citan los mismos artículos y leyes del material
de estudio oficial. Conviene igualmente repasar el cuadernillo completo.

Ejecutar con: streamlit run app.py
"""

import streamlit as st
import time
import random
import re
import unicodedata

try:
    from streamlit_autorefresh import st_autorefresh
    AUTOREFRESH_OK = True
except ImportError:
    AUTOREFRESH_OK = False

# =============================================================================
# CONFIGURACIÓN DE PÁGINA
# =============================================================================
st.set_page_config(
    page_title="Simulador de Examen - Poder Judicial de San Juan",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# CSS INSTITUCIONAL
# =============================================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;600;700&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
        font-size: 15px;
        line-height: 1.6;
    }
    .stApp { background-color: #F8F9FA; }

    section[data-testid="stSidebar"] { background-color: #FFFFFF; border-right: 1px solid #E0E3E7; }
    section[data-testid="stSidebar"] .stRadio label { font-weight: 600; color: #1B365D; }

    .institucional-header {
        background-color: #1B365D; color: #FFFFFF; padding: 22px 28px;
        border-radius: 10px; margin-bottom: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.12);
    }
    .institucional-header h1 { color: #FFFFFF !important; margin: 0; font-size: 26px; }
    .institucional-header p { color: #D6DEE8; margin: 4px 0 0 0; font-size: 14px; }

    .card {
        background-color: #FFFFFF; border-radius: 12px; padding: 22px 26px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08); border: 1px solid #ECEEF1; margin-bottom: 18px;
    }
    .card-titulo {
        color: #1B365D; font-weight: 700; font-size: 18px; margin-bottom: 10px;
        border-bottom: 2px solid #F0F2F5; padding-bottom: 8px;
    }

    .stButton > button {
        background-color: #1B365D; color: #FFFFFF; border: none; border-radius: 8px;
        padding: 8px 14px; font-weight: 600; font-size: 14px; transition: background-color 0.15s ease-in-out;
    }
    .stButton > button:hover { background-color: #142848; color: #FFFFFF; }

    .badge-aprobado {
        background-color: #E6F4EA; color: #1E7E34; font-weight: 700; padding: 8px 16px;
        border-radius: 8px; display: inline-block; border: 1px solid #B7E1C1;
    }
    .badge-reprobado {
        background-color: #FBEAEA; color: #B32424; font-weight: 700; padding: 8px 16px;
        border-radius: 8px; display: inline-block; border: 1px solid #F0C2C2;
    }

    .texto-modelo {
        background-color: #F8F9FA; border: 1px solid #E0E3E7; border-radius: 8px; padding: 18px;
        font-size: 15px; line-height: 1.7; color: #22272E;
    }
    .stTextArea textarea, .stTextInput input {
        font-size: 15px !important; line-height: 1.6 !important; border-radius: 8px !important;
        border: 1px solid #CED4DA !important;
    }
    .aviso-oficial {
        background-color: #EAF1FB; border-left: 4px solid #1B365D; padding: 12px 16px;
        border-radius: 6px; font-size: 14px; color: #1B365D; margin-bottom: 16px;
    }
    .aviso-advertencia {
        background-color: #FFF6E5; border-left: 4px solid #B37B00; padding: 12px 16px;
        border-radius: 6px; font-size: 14px; color: #7A5300; margin-bottom: 16px;
    }
    .cronometro {
        font-size: 22px; font-weight: 700; color: #1B365D; background: #EAF1FB;
        border-radius: 8px; padding: 8px 16px; display: inline-block; margin-bottom: 10px;
    }
    .cronometro-critico { color: #B32424 !important; background: #FBEAEA !important; }

    /* Botones-palabra del módulo de ortografía */
    div[data-testid="stHorizontalBlock"] .stButton > button {
        padding: 4px 8px; margin: 1px 0; font-weight: 500; font-size: 15px;
        background-color: #FFFFFF; color: #22272E; border: 1px solid #DDE1E6;
    }
    div[data-testid="stHorizontalBlock"] .stButton > button:hover {
        background-color: #EAF1FB; border-color: #1B365D; color: #1B365D;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

UMBRAL_APROBACION_ORTOGRAFIA = 75.00  # Acuerdo Gral. 83/26, punto 2.b: >= 75% de los errores corregidos
UMBRAL_APROBACION_TEORICO = 71.00     # Acuerdo Gral. 83/26, punto 4.c: >= 71% de respuestas correctas
UMBRAL_APROBACION = UMBRAL_APROBACION_TEORICO  # alias por compatibilidad con el resto del código

# =============================================================================
# MÓDULO 1 — ORTOGRAFÍA: BANCO DE TEXTOS + MOTOR DE ERRORES ALEATORIOS
# =============================================================================
# A diferencia de la versión anterior (errores fijos, siempre los mismos),
# acá los errores se generan al azar sobre palabras reales del texto en
# cada práctica nueva, igual que en el simulador comercial.

ORTOGRAFIA_TEXTOS = {
    "Privacidad y Protección de Datos Personales": (
        "La protección de datos personales en las redes sociales constituye un "
        "derecho fundamental reconocido por la Constitución Nacional y por los "
        "tratados internacionales incorporados a nuestro ordenamiento jurídico. "
        "Cuando una persona comparte información en plataformas digitales no "
        "renuncia automáticamente a su derecho a la intimidad, aunque asuma "
        "ciertos riesgos derivados de la exposición pública voluntaria. Los "
        "tribunales han sostenido reiteradamente que la difusión no autorizada "
        "de imágenes o datos sensibles puede configurar un daño resarcible, "
        "aún cuando la información haya sido publicada previamente por el "
        "propio titular en un contexto distinto al de su posterior circulación. "
        "Asimismo, las empresas que administran dichas plataformas tienen la "
        "obligación de implementar mecanismos efectivos de protección, bajo "
        "apercibimiento de incurrir en responsabilidad civil por omisión. La "
        "autoridad de aplicación puede imponer sanciones administrativas a "
        "quienes incumplan los deberes de resguardo, notificación y "
        "confidencialidad establecidos en la normativa vigente, sin perjuicio "
        "de las acciones judiciales que el afectado decida promover ante el "
        "fuero competente para reclamar el cese del daño y su reparación "
        "integral, incluyendo el daño moral cuando corresponda acreditarlo."
    ),
    "Debido Proceso Penal": (
        "El debido proceso penal constituye una garantía esencial del estado "
        "de derecho, que asegura a todo imputado el derecho a ser oído por un "
        "juez competente, independiente e imparcial, designado con anterioridad "
        "al hecho que motiva la causa. Ninguna persona puede ser condenada sin "
        "un juicio previo fundado en ley anterior al hecho del proceso, ni "
        "juzgada por comisiones especiales creadas al efecto. El acusado tiene "
        "derecho a conocer la acusación en su contra desde el primer momento, "
        "a ofrecer prueba de descargo, a controlar la producida por la "
        "contraparte y a contar con asistencia letrada durante toda la "
        "investigación. La violación de estas garantías acarrea la nulidad "
        "insanable de los actos procesales viciados, conforme reiterada "
        "jurisprudencia de la Corte, que además ha señalado que la duración "
        "razonable del proceso forma parte integrante de esta garantía, de "
        "modo que la dilación indebida e injustificada de la causa penal "
        "puede derivar en la extinción de la acción por prescripción o en la "
        "responsabilidad del Estado por su funcionamiento anormal."
    ),
    "Acceso a la Información Judicial": (
        "El acceso a la información judicial es un pilar de la transparencia "
        "institucional y permite a los ciudadanos ejercer un control efectivo "
        "sobre la actividad de los tribunales y sobre el uso de los recursos "
        "públicos destinados a la administración de justicia. Toda persona "
        "tiene derecho a solicitar copia de resoluciones y expedientes, salvo "
        "que exista una razón fundada de reserva vinculada a la protección de "
        "datos sensibles, a menores de edad o a la seguridad de las partes "
        "intervinientes. Los organismos judiciales deben responder las "
        "solicitudes dentro de los plazos establecidos por la reglamentación "
        "vigente, y su negativa injustificada puede ser recurrida ante la "
        "instancia superior correspondiente mediante el procedimiento previsto "
        "a tal efecto. La publicación de sentencias, con los recaudos que "
        "correspondan para preservar la identidad de las personas involucradas, "
        "fortalece la confianza pública en el sistema de justicia y contribuye "
        "a la previsibilidad de las decisiones judiciales, en tanto permite "
        "conocer los criterios interpretativos sostenidos por los distintos "
        "tribunales frente a situaciones jurídicas análogas."
    ),
    "Ética Pública y Función Judicial": (
        "La ética pública en el ejercicio de la función judicial exige de sus "
        "integrantes un comportamiento acorde a los principios de honestidad, "
        "imparcialidad y transparencia, tanto dentro como fuera del ámbito "
        "estrictamente laboral. Los magistrados y funcionarios deben excusarse "
        "de intervenir en aquellos asuntos en los que tengan un interés "
        "personal, directo o indirecto, que pueda comprometer su objetividad "
        "o generar una apariencia razonable de parcialidad ante terceros. La "
        "confianza de la sociedad en el Poder Judicial depende, en gran "
        "medida, de que sus miembros actúen con coherencia entre el discurso "
        "institucional y su conducta cotidiana, evitando cualquier situación "
        "que pueda comprometer la dignidad del cargo que ocupan. El "
        "incumplimiento de estos deberes puede dar lugar a sanciones "
        "disciplinarias, que van desde el apercibimiento hasta la remoción del "
        "cargo mediante el procedimiento de enjuiciamiento correspondiente, sin "
        "perjuicio de las responsabilidades civiles o penales que puedan "
        "corresponder por los mismos hechos ante la jurisdicción competente."
    ),
    "Violencia de Género y Acceso a la Justicia": (
        "El acceso a la justicia en situaciones de violencia de género exige "
        "de los operadores judiciales una perspectiva especializada que tenga "
        "en cuenta la particular vulnerabilidad de las víctimas y los "
        "obstáculos que enfrentan al momento de formular una denuncia. Las "
        "medidas de protección deben dictarse con celeridad, sin dilaciones "
        "que puedan agravar el riesgo, y deben ser efectivamente notificadas "
        "y controladas en su cumplimiento por los organismos competentes. La "
        "revictimización, entendida como el sometimiento reiterado de la "
        "persona afectada a relatos innecesarios de los hechos sufridos, "
        "constituye una práctica que los tribunales deben evitar activamente "
        "mediante protocolos de entrevista adecuados y ámbitos físicos que "
        "resguarden su intimidad. Asimismo, la valoración de la prueba en "
        "estos procesos debe realizarse con perspectiva de género, "
        "considerando las dificultades probatorias propias de hechos que "
        "suelen ocurrir en la esfera privada, sin que ello implique alterar "
        "las garantías del debido proceso que también asisten a la persona "
        "denunciada durante toda la tramitación de la causa."
    ),
    "Mediación y Resolución Alternativa de Conflictos": (
        "La mediación constituye un método alternativo de resolución de "
        "conflictos que privilegia la autocomposición de las partes por sobre "
        "la decisión heterónoma impuesta por un tercero. El mediador debe "
        "actuar con imparcialidad, neutralidad y confidencialidad, facilitando "
        "la comunicación entre las partes sin imponer soluciones ni emitir "
        "opiniones sobre el fondo del conflicto sometido a su intervención. "
        "En muchos fueros la instancia de mediación resulta obligatoria antes "
        "de habilitar la vía judicial, salvo en aquellas materias que la "
        "propia normativa excluye expresamente por razones de urgencia o de "
        "orden público. El acuerdo alcanzado en la mediación, una vez "
        "homologado por el juez competente, adquiere fuerza ejecutoria "
        "equivalente a la de una sentencia judicial firme, lo que permite su "
        "cumplimiento forzado ante el incumplimiento de alguna de las partes. "
        "La confidencialidad del proceso implica que lo manifestado durante "
        "las audiencias no puede ser utilizado posteriormente como prueba en "
        "un eventual juicio, salvo consentimiento expreso de ambas partes."
    ),
    "Ejecución de Sentencias y Medidas Cautelares": (
        "La ejecución de sentencias constituye la etapa final del proceso "
        "judicial, orientada a hacer efectivo en los hechos aquello que fue "
        "reconocido en la resolución firme. El incumplimiento voluntario de "
        "la condena habilita al acreedor a solicitar medidas compulsivas, "
        "tales como el embargo de bienes, la inhibición general o la "
        "designación de un oficial de justicia para el cumplimiento forzado "
        "de la obligación. Las medidas cautelares, por su parte, tienen por "
        "finalidad asegurar preventivamente el resultado práctico del proceso, "
        "evitando que el transcurso del tiempo torne ilusorio el derecho "
        "reclamado. Para su procedencia se exige la verificación de la "
        "verosimilitud del derecho invocado y del peligro en la demora, "
        "pudiendo el juez exigir una contracautela suficiente para responder "
        "por los eventuales daños que la medida pueda ocasionar si "
        "finalmente resultara infundada. La parte afectada por una cautelar "
        "puede solicitar su levantamiento ofreciendo caución bastante o "
        "acreditando la desaparición de los recaudos que justificaron su "
        "dictado en primer término."
    ),
    "Recursos Procesales: Apelación y Casación": (
        "El recurso de apelación constituye el remedio procesal ordinario "
        "por excelencia, mediante el cual la parte agraviada por una "
        "resolución judicial solicita su revisión ante un tribunal de "
        "instancia superior. Su interposición debe realizarse dentro del "
        "plazo perentorio establecido por la ley, bajo apercibimiento de "
        "tener por consentida la resolución impugnada. El tribunal de alzada "
        "se encuentra limitado por los agravios expresados por el apelante, "
        "sin poder pronunciarse sobre cuestiones que no fueron sometidas a "
        "su consideración, salvo que se trate de materias de orden público "
        "que habiliten su intervención de oficio. El recurso de casación, "
        "por su parte, tiene un carácter extraordinario y se encuentra "
        "reservado para supuestos de errónea aplicación o interpretación de "
        "la ley, o de inobservancia de las formas procesales sustanciales "
        "que puedan haber afectado la validez del pronunciamiento recurrido. "
        "A diferencia de la apelación, la casación no constituye una tercera "
        "instancia de revisión de los hechos ni de la prueba producida, sino "
        "un control de legalidad sobre la sentencia impugnada."
    ),
    "Prescripción y Caducidad de las Acciones": (
        "La prescripción es un modo de extinción de las acciones por el "
        "transcurso del tiempo sumado a la inacción del titular del derecho, "
        "que opera como una sanción frente a quien no ejerce oportunamente "
        "las facultades que la ley le reconoce. Los plazos de prescripción "
        "pueden ser interrumpidos mediante determinados actos procesales, "
        "tales como la interposición de la demanda o el reconocimiento "
        "expreso o tácito del deudor, cuyo efecto consiste en hacer perder "
        "todo el tiempo transcurrido y comenzar un nuevo cómputo. También "
        "puede ser suspendida en ciertos supuestos previstos legalmente, "
        "situación en la que el plazo se detiene temporalmente y continúa "
        "corriendo una vez desaparecida la causal que motivó la suspensión, "
        "sin perder el tiempo ya cumplido con anterioridad. La caducidad, en "
        "cambio, extingue directamente el derecho y no admite interrupción "
        "ni suspensión, operando de pleno derecho una vez vencido el plazo "
        "correspondiente, motivo por el cual los tribunales pueden declararla "
        "de oficio sin necesidad de que sea invocada expresamente por la "
        "parte interesada en el proceso."
    ),
    "Organización de la Corte de Justicia": (
        "La Corte de Justicia constituye el máximo tribunal del Poder "
        "Judicial provincial y ejerce, además de sus funciones "
        "jurisdiccionales propias, la superintendencia general sobre la "
        "administración de justicia en todo el territorio de la provincia. "
        "Entre sus atribuciones se encuentra la de dictar los reglamentos "
        "internos necesarios para el adecuado funcionamiento de los "
        "tribunales inferiores, así como establecer las normas de "
        "organización administrativa, distribución de tareas y horarios del "
        "personal que se desempeña en las distintas circunscripciones "
        "judiciales. Le corresponde también resolver los recursos "
        "extraordinarios que se interpongan contra las sentencias definitivas "
        "dictadas por las Cámaras de Apelaciones, cuando se invoque la "
        "existencia de una cuestión constitucional o una interpretación "
        "arbitraria de la ley aplicable al caso. Asimismo, interviene en los "
        "conflictos de competencia suscitados entre distintos órganos "
        "jurisdiccionales de la provincia, garantizando de este modo la "
        "coherencia y unidad del sistema judicial en su conjunto."
    ),
}

# Reglas de corrupción ortográfica: cada una intenta transformar una palabra
# "correcta" en una versión con un error típico. Devuelven None si la regla
# no es aplicable a esa palabra en particular.
_VOCALES_TILDE = "áéíóú"
_SIN_TILDE = "aeiou"
_MAPA_QUITAR_TILDE = str.maketrans(_VOCALES_TILDE, _SIN_TILDE)


def _quitar_tilde(w):
    if any(v in w.lower() for v in _VOCALES_TILDE):
        nueva = w.translate(_MAPA_QUITAR_TILDE).translate(
            str.maketrans(_VOCALES_TILDE.upper(), _SIN_TILDE.upper())
        )
        return nueva if nueva != w else None
    return None


def _b_v(w):
    idxs = [i for i, ch in enumerate(w.lower()) if ch in "bv"]
    if not idxs:
        return None
    i = random.choice(idxs)
    ch = w[i]
    reemplazo = "v" if ch.lower() == "b" else "b"
    if ch.isupper():
        reemplazo = reemplazo.upper()
    return w[:i] + reemplazo + w[i + 1:]


def _c_s_z(w):
    idxs = [i for i, ch in enumerate(w.lower()) if ch in "csz"]
    if not idxs:
        return None
    i = random.choice(idxs)
    ch = w[i]
    opciones = [x for x in "csz" if x != ch.lower()]
    reemplazo = random.choice(opciones)
    if ch.isupper():
        reemplazo = reemplazo.upper()
    return w[:i] + reemplazo + w[i + 1:]


def _quitar_h(w):
    if "h" in w.lower():
        i = w.lower().index("h")
        return w[:i] + w[i + 1:]
    return None


def _ll_y(w):
    lw = w.lower()
    if "ll" in lw:
        i = lw.index("ll")
        return w[:i] + ("Y" if w[i].isupper() else "y") + w[i + 2:]
    if "y" in lw and len(w) > 2:
        i = lw.index("y")
        return w[:i] + ("LL" if w[i].isupper() else "ll") + w[i + 1:]
    return None


def _g_j(w):
    lw = w.lower()
    for i, ch in enumerate(lw):
        if ch == "g" and i + 1 < len(lw) and lw[i + 1] in "ei":
            return w[:i] + ("J" if w[i].isupper() else "j") + w[i + 1:]
        if ch == "j" and i + 1 < len(lw) and lw[i + 1] in "ei":
            return w[:i] + ("G" if w[i].isupper() else "g") + w[i + 1:]
    return None


def _doble_consonante(w):
    for par in ("rr", "nn"):
        if par in w.lower():
            i = w.lower().index(par)
            return w[:i] + w[i] + w[i + 2:]
    return None


def _n_m_antes_bp(w):
    lw = w.lower()
    for par in ("mb", "mp"):
        if par in lw:
            i = lw.index(par)
            return w[:i] + ("N" if w[i].isupper() else "n") + w[i + 1:]
    return None


# Palabras que se confunden entre sí por sonar igual (homófonos) o por un
# uso gramatical incorrecto muy frecuente. Se aplican por coincidencia
# exacta de la palabra, no por regla fonética.
HOMOFONOS = {
    "haber": "aver", "hay": "ay", "ahi": "hay", "halla": "haya", "haya": "halla",
    "valla": "vaya", "vaya": "valla", "tubo": "tuvo", "tuvo": "tubo",
    "hecho": "echo", "echo": "hecho", "aser": "hacer", "hacer": "aser",
    "asia": "hacia", "hacia": "asia", "hiba": "iba", "vez": "ves",
}


def _homofono(w):
    clave = limpiar_palabra(w)
    if clave in HOMOFONOS:
        reemplazo = HOMOFONOS[clave]
        if w[0].isupper():
            reemplazo = reemplazo.capitalize()
        return reemplazo
    return None


# Lista ponderada: las que el usuario pidió reforzar (s/c/z, b/v, mp/mb)
# aparecen repetidas para que salgan con mucha más frecuencia que el resto.
REGLAS_ERROR = (
    [_homofono] * 3
    + [_c_s_z] * 5
    + [_b_v] * 5
    + [_n_m_antes_bp] * 4
    + [_quitar_tilde] * 2
    + [_quitar_h] * 2
    + [_ll_y]
    + [_g_j]
    + [_doble_consonante]
)


def limpiar_palabra(palabra: str) -> str:
    """Quita signos de puntuación de los extremos y pasa a minúsculas."""
    return re.sub(r"^[^\wáéíóúñÁÉÍÓÚÑ]+|[^\wáéíóúñÁÉÍÓÚÑ]+$", "", palabra).lower()


def generar_practica_ortografia(texto: str, n_errores: int, prop_puntuacion: float = 0.3):
    """Genera una versión del texto con errores al azar en cada intento.

    Devuelve (tokens_mostrados, errores) donde errores es un dict
    idx -> {"tipo": "ortografia"|"puntuacion", "correcta": ...}.

    - "ortografia": la palabra fue corrompida (tildes, s/c/z, b/v, mp/mb,
      homófonos como haber/aver, hay/ahí, halla/haya, tubo/tuvo, etc.).
      "correcta" es la palabra limpia (minúsculas, sin signos).
    - "puntuacion": se le sacó la coma o el punto final a esa palabra.
      "correcta" es el signo que falta ("," o ".").
    """
    tokens = texto.split()
    tokens_mostrados = list(tokens)
    errores = {}

    n_punt = max(1, round(n_errores * prop_puntuacion)) if n_errores > 2 else 0
    n_orto = max(0, n_errores - n_punt)

    # --- Errores de ortografía / homófonos sobre palabras ---
    candidatos = [
        i for i, t in enumerate(tokens)
        if len(limpiar_palabra(t)) >= 3 and limpiar_palabra(t).isalpha()
    ]
    random.shuffle(candidatos)

    for idx in candidatos:
        if len([e for e in errores.values() if e["tipo"] == "ortografia"]) >= n_orto:
            break
        token = tokens[idx]
        prefijo = re.match(r"^[^\wáéíóúñÁÉÍÓÚÑ]*", token).group(0)
        sufijo = re.search(r"[^\wáéíóúñÁÉÍÓÚÑ]*$", token).group(0)
        nucleo = token[len(prefijo):len(token) - len(sufijo)] if sufijo else token[len(prefijo):]
        if not nucleo:
            continue
        reglas = REGLAS_ERROR[:]
        random.shuffle(reglas)
        for regla in reglas:
            corrompida = regla(nucleo)
            if corrompida and corrompida.lower() != nucleo.lower():
                tokens_mostrados[idx] = prefijo + corrompida + sufijo
                errores[idx] = {"tipo": "ortografia", "correcta": limpiar_palabra(nucleo)}
                break

    # --- Errores de puntuación: falta la coma o el punto ---
    candidatos_punt = [
        i for i, t in enumerate(tokens)
        if i not in errores and i < len(tokens) - 1 and t and t[-1] in ",."
    ]
    random.shuffle(candidatos_punt)
    for idx in candidatos_punt:
        if len([e for e in errores.values() if e["tipo"] == "puntuacion"]) >= n_punt:
            break
        signo = tokens[idx][-1]
        tokens_mostrados[idx] = tokens[idx][:-1]
        errores[idx] = {"tipo": "puntuacion", "correcta": signo}

    return tokens_mostrados, errores


# =============================================================================
# MÓDULO 2 — DACTILOGRAFÍA
# =============================================================================

TIEMPO_LIMITE_DACTILOGRAFIA_SEG_DEFAULT = 240  # 4 minutos
PALABRAS_MINIMAS_DACTILOGRAFIA = 100
# Tolerancia por latencia técnica del corte automático (tick de 250ms del
# reloj JS + ida y vuelta del clic al servidor). No es tiempo "de gracia"
# para escribir más, es solo el margen de error de la medición.
MARGEN_LATENCIA_SEG = 5

DACTILOGRAFIA_TEXTOS = {
    "Ley Orgánica del Poder Judicial (extracto)": (
        "El Poder Judicial de la Provincia será ejercido por la Corte de "
        "Justicia, las Cámaras de Apelaciones, los Juzgados de Primera "
        "Instancia y los demás tribunales inferiores que la ley establezca. "
        "Los magistrados y funcionarios judiciales son inamovibles mientras "
        "dure su buena conducta y no podrán ser trasladados ni ascendidos "
        "sin su consentimiento. La Corte de Justicia ejercerá la "
        "superintendencia general sobre la administración de justicia, "
        "pudiendo dictar los reglamentos internos necesarios para el "
        "adecuado funcionamiento de los tribunales, así como establecer las "
        "normas de organización, distribución de tareas y horarios del "
        "personal administrativo y técnico que se desempeña en las distintas "
        "circunscripciones judiciales de la provincia. La Corte podrá "
        "asimismo delegar en las Cámaras de Apelaciones determinadas "
        "funciones de superintendencia sobre los juzgados de su "
        "dependencia, sin que ello implique renunciar a su facultad de "
        "avocación en los asuntos que considere de especial trascendencia "
        "institucional. Los juzgados de primera instancia se organizarán "
        "por materia, pudiendo crearse fueros especializados en lo civil, "
        "comercial, penal, laboral, de familia y contencioso administrativo "
        "según las necesidades del servicio de justicia y la carga procesal "
        "existente en cada circunscripción judicial. Durante la feria "
        "judicial de enero y la de julio se mantendrá un servicio de "
        "guardia para atender aquellas cuestiones urgentes que no admitan "
        "demora, tales como medidas cautelares, hábeas corpus y asuntos "
        "vinculados a la protección de niños, niñas y adolescentes. El "
        "ingreso a la carrera judicial se realizará mediante concurso "
        "público de oposición y antecedentes, garantizando la idoneidad, "
        "transparencia y publicidad del procedimiento de selección de los "
        "aspirantes a los distintos cargos administrativos y técnicos del "
        "organismo. Finalizado el proceso de evaluación, la nómina de "
        "aprobados integrará un orden de mérito que será utilizado para "
        "cubrir las vacantes que se produzcan durante su vigencia. En caso "
        "de acefalía transitoria de algún juzgado, la Corte podrá disponer "
        "la subrogancia mediante magistrados de otros fueros o mediante "
        "conjueces designados conforme a la lista aprobada anualmente, a "
        "fin de garantizar la continuidad del servicio de justicia sin "
        "dilaciones para los justiciables que tramitan sus causas."
    ),
    "Constitución Provincial (extracto)": (
        "El gobierno de la Provincia de San Juan es republicano, "
        "representativo y federal, de acuerdo con los principios, "
        "declaraciones y garantías establecidos en la Constitución Nacional. "
        "Todos los habitantes de la provincia son iguales ante la ley y "
        "gozan de los derechos y garantías que reconocen la Constitución "
        "Nacional y esta Constitución, sin más restricciones que las que "
        "ellas establecen. Ningún habitante puede ser penado sin juicio "
        "previo fundado en ley anterior al hecho del proceso, ni juzgado por "
        "comisiones especiales ni sacado de los jueces designados por la ley "
        "antes del hecho de la causa. Es inviolable la defensa en juicio de "
        "la persona y de los derechos, debiendo asegurarse a todo habitante "
        "el acceso gratuito a la justicia cuando por su condición "
        "económica se encuentre imposibilitado de afrontar los gastos que "
        "un proceso judicial pudiera irrogarle. El domicilio, la "
        "correspondencia y los papeles privados son inviolables, y una ley "
        "determinará en qué casos y con qué justificativos podrá "
        "procederse a su allanamiento u ocupación por parte de la "
        "autoridad competente. Todos los actos públicos deben ser "
        "susceptibles de conocimiento por parte de los habitantes de la "
        "provincia, salvo aquellas excepciones que la propia Constitución o "
        "las leyes dictadas en su consecuencia establezcan por razones "
        "fundadas de seguridad, intimidad o interés general. La provincia "
        "reconoce y garantiza el ejercicio de los derechos políticos, "
        "conforme al principio de la soberanía popular y de las leyes que "
        "se dicten en consecuencia, promoviendo la participación de todos "
        "los ciudadanos en los asuntos de gobierno de la comunidad. Los "
        "tratados internacionales de derechos humanos con jerarquía "
        "constitucional integran el bloque de constitucionalidad y deben "
        "ser tenidos en cuenta por todos los poderes públicos provinciales "
        "al momento de interpretar y aplicar el resto del ordenamiento "
        "jurídico local, incluyendo las normas procesales y administrativas "
        "que rigen el funcionamiento cotidiano de los organismos del Estado "
        "provincial y sus relaciones con los habitantes de la provincia, "
        "sin que pueda invocarse disposición interna alguna para justificar "
        "su incumplimiento ante los organismos de control correspondientes."
    ),
    "Hábeas Corpus (extracto)": (
        "Toda persona que de modo actual o inminente sufra una restricción "
        "ilegal o arbitraria de su libertad física, o agravamiento ilegítimo "
        "en la forma o condiciones en que se cumple la privación de la "
        "libertad, tiene derecho a interponer acción de hábeas corpus ante "
        "el juez competente, quien deberá resolver de inmediato. El "
        "procedimiento será sumarísimo y gratuito, y podrá promoverse por la "
        "persona afectada o por cualquiera en su nombre, sin necesidad de "
        "mandato ni patrocinio letrado, debiendo el magistrado interviniente "
        "disponer las medidas urgentes que resulten conducentes para hacer "
        "cesar la restricción denunciada. Se distinguen distintas "
        "modalidades según la situación que se pretenda remediar: el "
        "hábeas corpus preventivo, cuando existe amenaza actual de una "
        "restricción ilegal todavía no consumada; el correctivo, cuando la "
        "privación de la libertad se cumple en condiciones más gravosas "
        "que las legalmente autorizadas; y el reparador, dirigido a hacer "
        "cesar una detención ya efectivizada sin orden de autoridad "
        "competente. El juez que reciba la presentación deberá constituirse "
        "de inmediato en el lugar donde se encuentre la persona afectada si "
        "las circunstancias del caso así lo requieren, pudiendo ordenar su "
        "inmediata libertad si no encuentra motivo legal que justifique la "
        "restricción denunciada. La resolución que se dicte es apelable "
        "dentro de las veinticuatro horas de notificada, sin que la "
        "interposición del recurso suspenda el cumplimiento de la orden de "
        "libertad dispuesta en primera instancia, salvo disposición expresa "
        "en contrario debidamente fundada por el tribunal interviniente. "
        "El Estado provincial responde por los daños que pudiera ocasionar "
        "una privación ilegítima de la libertad, sin perjuicio de la "
        "responsabilidad personal que le pudiera corresponder al funcionario "
        "que la haya dispuesto o ejecutado en violación de las garantías "
        "constitucionales vigentes. La acción de hábeas corpus no puede ser "
        "suspendida bajo ninguna circunstancia, ni siquiera durante la "
        "vigencia del estado de sitio, en cuyo caso el control judicial se "
        "limitará a verificar la legitimidad de la orden de restricción, "
        "sin poder ingresar a evaluar el mérito de las razones que motivaron "
        "su dictado por parte de la autoridad competente."
    ),
    "Ética Pública (extracto)": (
        "Los funcionarios públicos están obligados a desempeñar sus "
        "funciones con honestidad, probidad, rectitud y buena fe, "
        "anteponiendo en todo momento el interés general sobre cualquier "
        "interés particular. Deberán abstenerse de intervenir en asuntos en "
        "los que tengan un interés personal que pueda comprometer su "
        "imparcialidad, así como excusarse cuando corresponda conforme a las "
        "normas vigentes. La transparencia en la gestión pública y el "
        "sometimiento pleno a la ley constituyen pilares indispensables para "
        "sostener la confianza de la ciudadanía en las instituciones del "
        "Estado provincial. Todo funcionario que ingrese a cumplir "
        "funciones en el Poder Judicial deberá presentar una declaración "
        "jurada de sus bienes e ingresos, la que deberá actualizarse "
        "anualmente y al momento de cesar en el cargo, con el fin de "
        "permitir el control patrimonial de la evolución de su situación "
        "económica durante el ejercicio de la función pública. Asimismo, "
        "regirá un régimen de incompatibilidades que impide el ejercicio "
        "simultáneo de determinadas actividades privadas con el desempeño "
        "de cargos judiciales, salvo las excepciones que la propia "
        "reglamentación contemple para la docencia universitaria y otras "
        "actividades académicas debidamente autorizadas. Los obsequios y "
        "beneficios que un funcionario reciba con motivo o en ocasión del "
        "ejercicio de sus funciones, cuyo valor supere el monto que fije la "
        "reglamentación, deberán ser registrados e incorporados al "
        "patrimonio del organismo al que pertenece, no pudiendo en ningún "
        "caso condicionar la imparcialidad de sus decisiones futuras. El "
        "incumplimiento de las obligaciones establecidas en el régimen de "
        "ética pública podrá dar lugar, según la gravedad del hecho, a "
        "sanciones que van desde el llamado de atención hasta la cesantía "
        "del agente, sin perjuicio de las acciones civiles o penales que "
        "puedan corresponder por los mismos hechos. La Oficina de Ética "
        "Pública tendrá a su cargo el asesoramiento a los funcionarios en "
        "materia de conflictos de interés, así como el seguimiento del "
        "cumplimiento efectivo de las declaraciones juradas patrimoniales "
        "exigidas por la normativa vigente en todo el ámbito del Poder "
        "Judicial provincial."
    ),
    "Código Procesal: Principios Generales (extracto)": (
        "El proceso judicial se rige por los principios de bilateralidad, "
        "congruencia y preclusión, en virtud de los cuales las partes deben "
        "tener igualdad de oportunidades para exponer sus pretensiones y "
        "defensas, el juez debe pronunciarse dentro de los límites de lo "
        "solicitado por las partes, y los actos procesales cumplidos no "
        "pueden volver a discutirse una vez consentidos o vencidos los "
        "plazos correspondientes. Las notificaciones deben practicarse en el "
        "domicilio constituido por las partes, y su omisión o defecto puede "
        "acarrear la nulidad del acto procesal respectivo cuando genere un "
        "perjuicio efectivo a la parte afectada. Rige también el principio "
        "de economía procesal, conforme al cual debe procurarse obtener el "
        "mayor resultado posible con el menor empleo de actividad procesal, "
        "evitando dilaciones innecesarias y la multiplicación injustificada "
        "de trámites que no aporten un beneficio real a la resolución del "
        "conflicto. El principio de inmediación exige que el juez tome "
        "contacto directo con las partes, los testigos y la prueba "
        "producida en el expediente, de modo de formar su convicción sobre "
        "la base de elementos que ha podido apreciar personalmente durante "
        "el trámite de la causa. Las partes y sus letrados deben actuar con "
        "lealtad, probidad y buena fe procesal, absteniéndose de plantear "
        "incidentes manifiestamente dilatorios o de utilizar los "
        "mecanismos previstos por la ley con una finalidad distinta a la "
        "que les es propia. La violación de estos deberes puede dar lugar a "
        "sanciones conminatorias o a la imposición de costas por temeridad "
        "o malicia procesal a cargo de la parte que incurra en ellas. "
        "Asimismo, rige el principio de publicidad de los actos procesales, "
        "conforme al cual las audiencias deben ser, como regla general, "
        "abiertas al público, salvo que existan razones fundadas de orden "
        "público, seguridad o protección de la intimidad de las partes que "
        "justifiquen su realización a puertas cerradas. El impulso procesal "
        "puede quedar a cargo de las partes o del propio tribunal según la "
        "naturaleza de la materia debatida, correspondiendo al juez velar "
        "en todo momento por el correcto desarrollo del proceso y por la "
        "efectiva vigencia de las garantías constitucionales de quienes "
        "intervienen en él."
    ),
    "Ministerio Público Fiscal (extracto)": (
        "El Ministerio Público Fiscal tiene por función promover la "
        "actuación de la justicia en defensa de la legalidad y de los "
        "intereses generales de la sociedad, ejerciendo sus funciones con "
        "unidad de actuación e independencia de criterio, sin sujetarse a "
        "instrucciones o directivas que provengan de órganos ajenos a su "
        "propia estructura. Los fiscales deben requerir la aplicación de la "
        "ley tanto en los procedimientos judiciales como en aquellas "
        "actuaciones que la normativa vigente les asigne fuera del ámbito "
        "estrictamente judicial, actuando siempre con objetividad y "
        "resguardando las garantías constitucionales del imputado. La "
        "estructura del Ministerio Público Fiscal se organiza en fiscalías "
        "de instrucción, encargadas de dirigir la investigación penal "
        "preparatoria, y fiscalías de juicio, que intervienen en la etapa "
        "de debate oral ante el tribunal correspondiente. Podrán "
        "constituirse además unidades fiscales especializadas para el "
        "tratamiento de determinadas materias, tales como delitos "
        "económicos, criminalidad organizada, violencia de género o "
        "delitos cometidos contra niños, niñas y adolescentes, con el "
        "objeto de brindar una respuesta más eficaz y especializada frente "
        "a la particular complejidad de estos casos. El fiscal general "
        "ejercerá la superintendencia sobre los restantes integrantes del "
        "Ministerio Público Fiscal, pudiendo impartir instrucciones "
        "generales de política criminal que resulten obligatorias para "
        "todos los fiscales, sin que ello implique afectar la "
        "independencia de criterio que corresponde a cada uno de ellos en "
        "la valoración de los casos concretos sometidos a su intervención. "
        "Los fiscales podrán solicitar la colaboración de las fuerzas de "
        "seguridad y de organismos técnicos y científicos para el "
        "esclarecimiento de los hechos investigados, debiendo estos "
        "organismos prestar el auxilio requerido dentro del plazo que se "
        "les fije, bajo apercibimiento de hacer efectiva la responsabilidad "
        "administrativa que pudiera corresponder por su incumplimiento "
        "injustificado. La actuación del Ministerio Público Fiscal deberá "
        "ajustarse en todo momento a criterios de razonabilidad y "
        "proporcionalidad, evitando el uso desmedido de las facultades "
        "coercitivas que la ley pone a su disposición durante la etapa de "
        "investigación penal preparatoria."
    ),
    "Reglamento de Archivo Judicial - Destrucción de Expedientes (Arts. 270 a 273)": (
        "Artículo 270.- La oportunidad de la destrucción de expedientes será "
        "determinada por el jefe de la sección, con autorización escrita del "
        "director del archivo, sin apelación alguna por parte de los "
        "interesados, salvo el derecho acordado por el Artículo 273. Se dará "
        "intervención a los directores del Archivo General, Departamento de "
        "Estudios Etnográficos y Coloniales de Santa Fe, Museo Histórico de "
        "Rosario y Servicio Provincial de Catastro e Información Territorial, "
        "los cuales podrán pedir la exclusión de los expedientes que, a su "
        "juicio, deban conservarse. No será necesario dar intervención, "
        "respecto a los expedientes de lo penal de sentencia, instrucción, "
        "correccional, comunal, de circuito y penal de faltas. Artículo 271.- "
        "Los expedientes a destruirse serán clasificados por una comisión "
        "revisora permanente, compuesta por personal técnico del archivo, "
        "nombrado al efecto. Artículo 272.- Efectuada la clasificación y "
        "confeccionada la nómina de los expedientes a destruir, se publicará "
        "un aviso en el Boletín Oficial durante tres días consecutivos, "
        "anunciando solamente la destrucción de expedientes del fuero que "
        "corresponda y años que comprende. Artículo 273.- Los interesados en "
        "la exclusión de algún expediente o actuaciones, deberán solicitarlo "
        "hasta diez días de vencido el término de publicación, con nota "
        "dirigida al director del archivo, expresando y justificando el "
        "interés y razones de su petición. Esta será resuelta por la sala de "
        "apelación que corresponda, con intervención del director del "
        "archivo; pero siempre los interesados podrán pedir desglose o copia "
        "a su costa, de todo o parte del expediente a destruirse."
    ),
    "Acuerdo General - Curso Virtual Obligatorio (extracto)": (
        "Que, actualmente, resulta conveniente incorporar al procedimiento "
        "de concurso de aspirantes para ingreso al Poder Judicial para "
        "cubrir cargos pertenecientes a la planta permanente del personal "
        "administrativo y técnico, un curso virtual, obligatorio, "
        "asincrónico y autogestionado, con la finalidad de facilitar a los "
        "postulantes, el estudio del cuadernillo oficial. Que, este curso "
        "permitirá organizar los contenidos del cuadernillo temático, con "
        "instancias de práctica, familiarizando a los participantes con "
        "temas respecto de los cuales serán evaluados. De esta forma se "
        "garantiza que quienes accedan a los exámenes posteriores "
        "eliminatorios, cumplan con una instancia previa de capacitación. "
        "Que, el curso mencionado, se realizará a través de la Escuela "
        "Judicial con las modalidades y requisitos que se establecen en el "
        "reglamento para llamado a concurso de ingreso."
    ),
    "Reglamento de Concursos - Requisitos de Ingreso (extracto, Art. 6)": (
        "Son requisitos para el ingreso: Nacionalidad argentina, nativo, "
        "naturalizado o por opción, con dos años en ejercicio de la "
        "ciudadanía, acreditada mediante la presentación de fotocopia "
        "certificada del Documento de Identidad; o extranjero con "
        "residencia permanente, entendiéndose por tal lo dispuesto en el "
        "Artículo 22 de la Ley N° 25.871, Ley de Política de Migraciones. "
        "Edad mayor de dieciocho años. Las personas de treinta y cinco años "
        "o más, deberán formalizar una manifestación con carácter de "
        "declaración jurada de los aportes previsionales efectivamente "
        "realizados, los que oportunamente deberán acreditarse. Título de "
        "enseñanza secundaria o polimodal completo, acreditado mediante la "
        "presentación de fotocopia certificada del título legalizado por la "
        "autoridad educativa que corresponda. Certificado de Antecedentes "
        "otorgado por la Policía de la Provincia de San Juan."
    ),
}

# =============================================================================
# MÓDULO 3 — EXAMEN TEÓRICO: BANCO AMPLIADO
# =============================================================================

TEORICO_PREGUNTAS = [
    # ============================================================
    # TEMA I - DERECHO CONSTITUCIONAL
    # ============================================================
    {"pregunta": "El artículo 31 de la Constitución Nacional consagra el principio de supremacía constitucional.",
     "opciones": ["Verdadero", "Falso"], "correcta": 0},
    {"pregunta": "Tras la reforma de 1994, ¿qué artículos integran la parte dogmática de la Constitución Nacional?",
     "opciones": ["Del 1 al 35 únicamente", "Del 1 al 43", "Del 44 al 129", "Del 36 al 129"], "correcta": 1},
    {"pregunta": "La parte orgánica de la Constitución Nacional (órganos de gobierno, sus facultades y relaciones) se extiende desde el artículo:",
     "opciones": ["1 al 35", "36 al 43", "44 al 129", "121 al 129"], "correcta": 2},
    {"pregunta": "En la estructura federal, ¿qué relación se institucionaliza a través de la Cámara de Senadores?",
     "opciones": ["La subordinación", "La participación", "La coordinación", "La delegación"], "correcta": 1},
    {"pregunta": "La reforma constitucional de 1994 incorporó la acción de hábeas corpus en el artículo 18 de la Constitución Nacional.",
     "opciones": ["Verdadero", "Falso"], "correcta": 1},
    {"pregunta": "En la Constitución de la Provincia de San Juan, ¿qué artículo consagra la acción de hábeas corpus?",
     "opciones": ["Artículo 18", "Artículo 32", "Artículo 40", "Artículo 41"], "correcta": 1},
    {"pregunta": "El amparo por mora, previsto en el artículo 41 de la Constitución de San Juan, permite reclamar judicialmente:",
     "opciones": ["La libertad física restringida ilegalmente", "El pronto despacho de actuaciones administrativas ante el silencio de la administración", "La nulidad de una sentencia firme", "La inconstitucionalidad de una ley"], "correcta": 1},
    {"pregunta": "Según el artículo 18 de la Constitución Nacional y el principio de inocencia, la única fuente legítima de privación de la libertad con carácter permanente es la sentencia condenatoria firme.",
     "opciones": ["Verdadero", "Falso"], "correcta": 0},
    {"pregunta": "En el sistema procesal penal acusatorio adversarial de San Juan (Ley 1851-O), la detención sin resolución de una medida de coerción puede extenderse hasta 96 horas.",
     "opciones": ["Verdadero", "Falso"], "correcta": 1},
    {"pregunta": "Según el artículo 114 de la Constitución Nacional, el Consejo de la Magistratura tiene a su cargo la selección de los magistrados y la administración del Poder Judicial.",
     "opciones": ["Verdadero", "Falso"], "correcta": 0},
    {"pregunta": "Conforme al artículo 115 de la Constitución Nacional, los jueces de tribunales inferiores de la Nación son removidos por:",
     "opciones": ["El Presidente de la Nación", "Un jurado de enjuiciamiento integrado por legisladores, magistrados y abogados de la matrícula federal", "El Congreso en pleno", "La Corte Suprema de Justicia"], "correcta": 1},
    {"pregunta": "En el Congreso de la Nación, ¿qué cámara representa proporcionalmente a la población?",
     "opciones": ["El Senado", "La Cámara de Diputados", "Ambas por igual", "Ninguna, la representación es territorial"], "correcta": 1},
    {"pregunta": "A cada provincia argentina y a la Ciudad de Buenos Aires les corresponden tres senadores nacionales.",
     "opciones": ["Verdadero", "Falso"], "correcta": 0},

    # ============================================================
    # TEMA II - CONSTITUCIÓN PROVINCIAL
    # ============================================================
    {"pregunta": "La actual Constitución de la Provincia de San Juan fue sancionada en 1994.",
     "opciones": ["Verdadero", "Falso"], "correcta": 1},
    {"pregunta": "¿Cuántos artículos componen la Constitución de la Provincia de San Juan?",
     "opciones": ["197", "218", "255", "281"], "correcta": 3},
    {"pregunta": "Según el artículo 201 de la Constitución Provincial, la Corte de Justicia de San Juan está integrada, como mínimo, por cinco miembros, en número siempre impar.",
     "opciones": ["Verdadero", "Falso"], "correcta": 0},
    {"pregunta": "Para ser miembro de la Corte de Justicia o Fiscal General, la Constitución Provincial exige, entre otros requisitos, una edad mínima de:",
     "opciones": ["25 años", "28 años", "30 años", "35 años"], "correcta": 2},
    {"pregunta": "Para ser miembro de las Cámaras, Juez, Agente Fiscal, Defensor o Asesor, la Constitución Provincial exige una edad mínima de:",
     "opciones": ["21 años", "25 años", "30 años", "40 años"], "correcta": 1},
    {"pregunta": "El Consejo de la Magistratura de San Juan, según el artículo 214 de la Constitución Provincial, está integrado únicamente por jueces de la Corte.",
     "opciones": ["Verdadero", "Falso"], "correcta": 1},
    {"pregunta": "El mandato de los miembros del Consejo de la Magistratura de San Juan dura:",
     "opciones": ["2 años", "3 años", "4 años", "6 años"], "correcta": 2},
    {"pregunta": "Los miembros de la Corte de Justicia y demás magistrados judiciales de San Juan son designados por:",
     "opciones": ["El Gobernador directamente", "La Cámara de Diputados, a propuesta de una terna elevada por el Consejo de la Magistratura", "El voto popular directo", "La Corte de Justicia en pleno"], "correcta": 1},
    {"pregunta": "Según el artículo 206 de la Constitución Provincial, las vacantes de funcionarios judiciales deben cubrirse dentro de los:",
     "opciones": ["30 días", "60 días", "90 días", "180 días"], "correcta": 2},
    {"pregunta": "El juicio político en San Juan puede promoverse, entre otros, contra:",
     "opciones": ["Cualquier empleado judicial", "El Gobernador, Vicegobernador, miembros de la Corte de Justicia, el Fiscal General y el Fiscal de Estado", "Los jueces de paz letrados únicamente", "Los agentes fiscales únicamente"], "correcta": 1},
    {"pregunta": "El Jurado de Enjuiciamiento de la Provincia de San Juan (para jueces de Cámara, primera instancia, jueces de paz, etc.) se integra con:",
     "opciones": ["Solo diputados", "Un miembro de la Corte, dos diputados y dos abogados de la matrícula", "Tres miembros de la Corte", "El Fiscal General y dos jueces"], "correcta": 1},
    {"pregunta": "Según el artículo 233 de la Constitución Provincial, son causales de remoción de los magistrados, entre otras:",
     "opciones": ["Tener más de 70 años", "La mala conducta, la negligencia, el desconocimiento reiterado y notorio del derecho, y la morosidad injustificada", "Haber sido trasladado de sede", "No haber ganado un concurso"], "correcta": 1},
    {"pregunta": "El Jurado de Enjuiciamiento de San Juan debe dictar sentencia dentro del término perentorio de:",
     "opciones": ["10 días", "15 días", "30 días", "60 días"], "correcta": 2},

    # ============================================================
    # TEMA III - ORGANIZACIÓN DEL PODER JUDICIAL DE SAN JUAN
    # ============================================================
    {"pregunta": "A los efectos de la competencia, el territorio de la Provincia de San Juan se divide en:",
     "opciones": ["Una sola circunscripción judicial", "Dos circunscripciones judiciales: Capital y Jáchal", "Diecinueve circunscripciones, una por departamento", "Tres circunscripciones"], "correcta": 1},
    {"pregunta": "La actual Ley Orgánica del Poder Judicial de San Juan es la Ley 754-O.",
     "opciones": ["Verdadero", "Falso"], "correcta": 1},
    {"pregunta": "¿Cuántos Juzgados de Paz Letrados hay actualmente en la Provincia de San Juan según la LOPJ?",
     "opciones": ["11", "17", "19", "25"], "correcta": 3},
    {"pregunta": "La Corte de Justicia de San Juan se divide, según la Ley Orgánica del Poder Judicial, en:",
     "opciones": ["Dos salas de cinco miembros", "Tres salas de tres miembros cada una", "Cuatro salas de dos miembros", "No se divide en salas"], "correcta": 1},
    {"pregunta": "La Cámara de Apelaciones en lo Civil, Comercial, Minería, Familia y Contencioso Administrativo de San Juan está integrada por:",
     "opciones": ["6 miembros en 2 salas", "9 miembros en 3 salas", "12 miembros en 4 salas", "15 miembros en 5 salas"], "correcta": 2},
    {"pregunta": "En el sistema procesal penal acusatorio adversarial (Ley 1851-O), el Tribunal de Impugnación de San Juan está integrado por:",
     "opciones": ["3 miembros", "6 miembros", "9 miembros", "12 miembros"], "correcta": 2},
    {"pregunta": "La Cámara en lo Penal y Correccional del sistema procesal mixto (Ley 754-O) está integrada por:",
     "opciones": ["3 miembros", "5 miembros", "6 miembros", "9 miembros"], "correcta": 0},
    {"pregunta": "Según el artículo 97 de la LOPJ, la Oficina Judicial es una estructura organizada por la Corte de Justicia que tiene como función:",
     "opciones": ["Reemplazar a los jueces en el dictado de sentencias", "Servir de soporte y apoyo a la actividad jurisdiccional de jueces y tribunales", "Ejercer la acusación penal", "Administrar el Consejo de la Magistratura"], "correcta": 1},
    {"pregunta": "Los juzgados con competencia civil, comercial y minería en San Juan tienen la llamada \"competencia residual\", lo que significa que:",
     "opciones": ["Solo atienden causas de menor cuantía", "Entienden en todas las cuestiones no asignadas expresamente a otros juzgados", "Solo actúan en la Segunda Circunscripción", "Solo intervienen en la etapa recursiva"], "correcta": 1},
    {"pregunta": "Los jueces con competencia en asuntos de familia en San Juan conocen, entre otros procesos, en:",
     "opciones": ["Únicamente sucesiones", "Nulidad de matrimonio, uniones convivenciales, adopción y divorcio", "Solo causas penales de niñez", "Ejecuciones hipotecarias"], "correcta": 1},
    {"pregunta": "El Recurso Extraordinario Provincial contra sentencias de las Cámaras de Apelaciones de San Juan se rige por la:",
     "opciones": ["Ley 754-O", "Ley 989-E", "Ley 2353-O", "Ley 26.485"], "correcta": 2},
    {"pregunta": "En San Juan, la Segunda Circunscripción Judicial tiene su asiento en la ciudad de:",
     "opciones": ["Caucete", "Jáchal", "Rawson", "Chimbas"], "correcta": 1},

    # ============================================================
    # TEMA IV - MINISTERIO PÚBLICO DE LA PROVINCIA DE SAN JUAN (Ley 633-E)
    # ============================================================
    {"pregunta": "Según la Ley del Ministerio Público (633-E), el Ministerio Público es:",
     "opciones": ["Un órgano ajeno al Poder Judicial", "Órgano del Poder Judicial con independencia orgánica funcional", "Una dependencia del Poder Ejecutivo", "Parte del Consejo de la Magistratura"], "correcta": 1},
    {"pregunta": "Para ser Fiscal General de la Corte de Justicia de San Juan se exige, entre otros requisitos:",
     "opciones": ["20 años de edad y 2 años de ejercicio profesional", "25 años de edad y 5 años de ejercicio profesional", "30 años de edad y 10 años de ejercicio profesional o magistratura", "No se exige edad mínima"], "correcta": 2},
    {"pregunta": "El Fiscal General de la Corte y los demás magistrados del Ministerio Público son designados por:",
     "opciones": ["El Fiscal General saliente", "La Cámara de Diputados, a propuesta de una terna del Consejo de la Magistratura", "El Gobernador sin intervención legislativa", "Concurso resuelto por la Corte en pleno"], "correcta": 1},
    {"pregunta": "Las vacantes de miembros del Ministerio Público de San Juan deben cubrirse dentro de:",
     "opciones": ["30 días", "60 días", "90 días", "120 días"], "correcta": 2},
    {"pregunta": "El Fiscal General de la Corte ejerce sobre los demás miembros del Ministerio Público:",
     "opciones": ["Ninguna autoridad, todos son independientes entre sí", "La superintendencia", "Solo funciones de consulta", "Autoridad exclusivamente disciplinaria"], "correcta": 1},
    {"pregunta": "Entre las facultades disciplinarias del Fiscal General de la Corte sobre miembros del Ministerio Público se encuentra la de imponer suspensión en el ejercicio de funciones de hasta:",
     "opciones": ["10 días", "15 días", "30 días", "60 días"], "correcta": 2},
    {"pregunta": "Contra las sanciones disciplinarias impuestas por el Fiscal General de la Corte procede:",
     "opciones": ["Ningún recurso", "El recurso de apelación ante la Corte de Justicia", "El recurso directo ante la Legislatura", "La acción de amparo únicamente"], "correcta": 1},
    {"pregunta": "Según la Ley del Ministerio Público, el Fiscal General debe disponer visitas a cárceles y establecimientos de detención, como mínimo:",
     "opciones": ["Una vez al año", "Tres veces al año", "Una vez por mes", "Solo si lo pide un juez"], "correcta": 1},
    {"pregunta": "Las instrucciones que un miembro del Ministerio Público imparte a sus inferiores jerárquicos deben transmitirse, como regla:",
     "opciones": ["Siempre en forma verbal", "Por escrito, admitiéndose forma verbal solo en casos de urgencia con constancia posterior", "Únicamente por vía telefónica", "A través de la prensa"], "correcta": 1},

    # ============================================================
    # TEMA V - DERECHO CIVIL Y DERECHO PROCESAL CIVIL
    # ============================================================
    {"pregunta": "Según el artículo 4 del Código Civil y Comercial, las leyes son obligatorias para:",
     "opciones": ["Solo los ciudadanos argentinos", "Todos los que habitan el territorio de la República, sean ciudadanos o extranjeros", "Solo quienes tienen domicilio legal constituido", "Solo los mayores de edad"], "correcta": 1},
    {"pregunta": "Conforme al artículo 5 del Código Civil y Comercial, las leyes rigen, salvo que ellas determinen otra fecha:",
     "opciones": ["Desde el día de su sanción", "Desde el día de su promulgación", "Después del octavo día de su publicación oficial", "Un año después de publicadas"], "correcta": 2},
    {"pregunta": "El principio de irretroactividad de la ley (artículo 7 CCyC) establece que las nuevas leyes:",
     "opciones": ["Siempre se aplican retroactivamente", "No tienen efecto retroactivo, sean o no de orden público, salvo disposición en contrario, sin afectar garantías constitucionales", "Solo rigen para el futuro si son penales", "No pueden aplicarse a relaciones jurídicas en curso"], "correcta": 1},
    {"pregunta": "Según el artículo 8 del Código Civil y Comercial (principio de inexcusabilidad):",
     "opciones": ["La ignorancia de las leyes puede excusar su incumplimiento en cualquier caso", "La ignorancia de las leyes no sirve de excusa para su cumplimiento, salvo excepción autorizada por el ordenamiento", "Solo los abogados están obligados a conocer la ley", "La ignorancia excusa siempre que sea de buena fe"], "correcta": 1},
    {"pregunta": "El domicilio real de una persona humana, conforme al artículo 73 del CCyC, es:",
     "opciones": ["El que la ley presume sin admitir prueba en contra", "El lugar de su residencia habitual, o donde desempeña su actividad profesional o económica para esas obligaciones", "El domicilio constituido en un juicio", "El domicilio de sus padres"], "correcta": 1},
    {"pregunta": "El domicilio legal, según el artículo 74 del CCyC, es:",
     "opciones": ["El que la persona elige libremente", "El que la ley presume, sin admitir prueba en contra, como lugar de residencia permanente para el ejercicio de derechos y obligaciones", "El mismo que el domicilio real siempre", "El domicilio procesal"], "correcta": 1},
    {"pregunta": "El domicilio procesal o ad litem debe constituirse, según el Código Procesal Civil de San Juan:",
     "opciones": ["Solo si el juez lo requiere expresamente", "Dentro de la circunscripción judicial correspondiente al tribunal, en el primer escrito o audiencia", "En cualquier lugar del país", "Solo en causas penales"], "correcta": 1},
    {"pregunta": "¿Cuál de las siguientes es una excepción a la obligatoriedad del patrocinio letrado en el Código Procesal Civil de San Juan?",
     "opciones": ["Contestar una demanda de daños y perjuicios", "Solicitar la declaratoria de pobreza", "Interponer un recurso de apelación", "Ofrecer prueba pericial"], "correcta": 1},
    {"pregunta": "Según el artículo 1 del Código Civil y Comercial, los usos, prácticas y costumbres son vinculantes cuando:",
     "opciones": ["Nunca lo son", "Las leyes o los interesados se refieren a ellos, o en situaciones no regladas legalmente, siempre que no sean contrarios a derecho", "Solo si están escritos en un contrato", "Solo en materia comercial"], "correcta": 1},
    {"pregunta": "El artículo 2 del Código Civil y Comercial, sobre interpretación de la ley, indica que debe tenerse en cuenta, entre otras pautas:",
     "opciones": ["Únicamente la letra literal de la norma", "Las palabras de la ley, sus finalidades, las leyes análogas y los tratados de derechos humanos", "Solo la intención original del legislador de 1871", "Solo la jurisprudencia extranjera"], "correcta": 1},
    {"pregunta": "En San Juan, a diferencia del Código Procesal Civil de la Nación, la sustitución de parte por enajenación del bien litigioso:",
     "opciones": ["Requiere siempre la conformidad expresa de la contraria", "No requiere conformidad expresa de la contraria y el proceso continúa sin retrotraer actos cumplidos", "Está prohibida", "Solo puede hacerse antes de la contestación de demanda"], "correcta": 1},

    # ============================================================
    # TEMA VI - DERECHO LABORAL Y PROCESAL LABORAL
    # ============================================================
    {"pregunta": "Según el artículo 4 de la Ley de Contrato de Trabajo, constituye trabajo:",
     "opciones": ["Cualquier actividad humana, remunerada o no", "Toda actividad lícita que se preste a favor de quien tiene la facultad de dirigirla, mediante una remuneración", "Solo la actividad realizada bajo relación de dependencia registrada", "Solo el trabajo manual"], "correcta": 1},
    {"pregunta": "La relación de dependencia laboral se caracteriza por una subordinación de triple tipo:",
     "opciones": ["Jurídica, técnica y económica", "Civil, penal y administrativa", "Política, social y cultural", "Nacional, provincial y municipal"], "correcta": 0},
    {"pregunta": "El principio protectorio del Derecho del Trabajo se manifiesta, entre otras, en la regla:",
     "opciones": ["In dubio pro reo", "In dubio pro operario", "Pacta sunt servanda", "Iura novit curia"], "correcta": 1},
    {"pregunta": "El principio de irrenunciabilidad de los derechos laborales implica que los derechos que surgen de normas imperativas son:",
     "opciones": ["Negociables a título oneroso", "Indisponibles e irrenunciables", "Transferibles a terceros", "Prescriptibles a los 6 meses"], "correcta": 1},
    {"pregunta": "El plazo de prescripción de los créditos laborales, desde que el crédito es exigible, es de:",
     "opciones": ["6 meses", "1 año", "2 años", "5 años"], "correcta": 2},
    {"pregunta": "El plazo de prescripción en materia de seguridad social es de:",
     "opciones": ["2 años", "5 años", "10 años", "20 años"], "correcta": 2},
    {"pregunta": "El principio de gratuidad en el derecho procesal laboral tiene por finalidad:",
     "opciones": ["Eximir al empleador de pagar indemnizaciones", "Garantizar el acceso gratuito de los trabajadores a la justicia", "Eliminar la necesidad de patrocinio letrado", "Reducir los plazos procesales"], "correcta": 1},
    {"pregunta": "El principio de continuidad de la relación laboral establece que, ante la duda sobre la continuación del contrato, se debe resolver:",
     "opciones": ["A favor de la extinción del contrato", "A favor de la existencia de un contrato por tiempo indeterminado", "A favor del empleador", "Según lo que decida el sindicato"], "correcta": 1},
    {"pregunta": "Los convenios colectivos de trabajo y los estatutos profesionales son considerados fuentes del Derecho del Trabajo de tipo:",
     "opciones": ["Clásicas, comunes a todas las ramas del derecho", "Propias, exclusivas del Derecho del Trabajo", "Materiales únicamente", "Subsidiarias del derecho penal"], "correcta": 1},

    # ============================================================
    # TEMA VII - DERECHO DE LAS FAMILIAS Y PROCESO DE FAMILIA
    # ============================================================
    {"pregunta": "El Código Procesal de Familia de la Provincia de San Juan es la:",
     "opciones": ["Ley 754-O", "Ley 989-E", "Ley 2435-O", "Ley 26.061"], "correcta": 2},
    {"pregunta": "Según el artículo 706 del Código Civil y Comercial, los procesos de familia se rigen, entre otros, por los principios de:",
     "opciones": ["Escritura, secreto y formalismo estricto", "Tutela judicial efectiva, inmediación, buena fe y lealtad procesal, oficiosidad y oralidad", "Doble instancia obligatoria en todos los casos", "Prueba tasada"], "correcta": 1},
    {"pregunta": "El Código Procesal de Familia de San Juan agrega expresamente, entre los principios del proceso de familia:",
     "opciones": ["La oralidad exclusiva sin excepciones", "La celeridad y la confidencialidad", "El secreto de sumario", "La prueba tasada"], "correcta": 1},
    {"pregunta": "En los procesos que deciden derechos de niñas, niños y adolescentes, la competencia territorial se determina principalmente por:",
     "opciones": ["El domicilio del progenitor demandado", "El centro de vida del niño, niña o adolescente", "El lugar donde se inició el matrimonio", "El domicilio del abogado interviniente"], "correcta": 1},
    {"pregunta": "Según el artículo 25 del Código Civil y Comercial, se considera adolescente a la persona menor de edad que:",
     "opciones": ["Cumplió 10 años", "Cumplió 13 años", "Cumplió 16 años", "Cumplió 18 años"], "correcta": 1},
    {"pregunta": "La función del abogado del niño consiste en:",
     "opciones": ["Reemplazar a los progenitores en todas sus funciones", "Brindar asistencia y defensa técnica propia al niño, niña o adolescente", "Actuar solo como intérprete en la audiencia", "Sustituir al Ministerio Público"], "correcta": 1},
    {"pregunta": "Conforme al artículo 109 del Código Civil y Comercial, corresponde designar tutor especial cuando, entre otros supuestos:",
     "opciones": ["El niño cumple 18 años", "Existe conflicto de intereses entre el representado y quien debería representarlo", "Los padres se divorcian", "El proceso dura más de un año"], "correcta": 1},
    {"pregunta": "La intervención del Ministerio Público respecto de personas menores de edad o con capacidad restringida, según el artículo 103 del CCyC, puede ser:",
     "opciones": ["Solo complementaria", "Solo principal", "Complementaria o principal, según el caso", "Inexistente en los procesos de familia"], "correcta": 2},
    {"pregunta": "La perspectiva de género en los conflictos de familia, receptada en el Código Procesal de Familia de San Juan, tiene como finalidad:",
     "opciones": ["Favorecer siempre a la mujer en la sentencia", "Identificar desigualdades, estereotipos o relaciones de poder que afecten el ejercicio de derechos", "Reemplazar el principio de igualdad ante la ley", "Aplicarse solo en causas penales"], "correcta": 1},

    # ============================================================
    # TEMA VIII - DERECHO PENAL Y PROCESAL PENAL
    # ============================================================
    {"pregunta": "El delito se define como una conducta o acción:",
     "opciones": ["Solo antijurídica", "Típica, antijurídica, culpable y punible", "Únicamente culpable", "Prevista en cualquier reglamento administrativo"], "correcta": 1},
    {"pregunta": "Los delitos de acción pública, como regla general, se inician:",
     "opciones": ["Solo a instancia de la víctima", "De oficio por los órganos del Estado", "Solo si lo pide el Ministerio Público de la Defensa", "Nunca sin denuncia previa"], "correcta": 1},
    {"pregunta": "Son ejemplos de delitos de acción privada, según el Código Penal:",
     "opciones": ["El homicidio y el robo", "Las calumnias e injurias", "El narcotráfico", "La evasión fiscal"], "correcta": 1},
    {"pregunta": "En los delitos de acción dependiente de instancia privada, el proceso:",
     "opciones": ["Solo puede iniciarse por denuncia del agraviado, y luego prosigue como si fuera de acción pública", "Se inicia siempre de oficio", "Nunca puede proseguir de oficio", "Requiere siempre juicio por jurados"], "correcta": 0},
    {"pregunta": "El sistema procesal penal acusatorio adversarial vigente en San Juan se estableció mediante la:",
     "opciones": ["Ley 754-O", "Ley 1851-O", "Ley 2352-O", "Ley 26.485"], "correcta": 1},
    {"pregunta": "El sistema procesal penal mixto, aplicado en forma residual en San Juan para causas anteriores, se rige por la:",
     "opciones": ["Ley 754-O", "Ley 1851-O", "Ley 2353-O", "Ley 633-E"], "correcta": 0},
    {"pregunta": "La implementación total del sistema acusatorio a todos los delitos de jurisdicción provincial en San Juan fue dispuesta por:",
     "opciones": ["Un decreto del Poder Ejecutivo provincial", "La Acordada 6/2024 de la Corte de Justicia", "Un fallo de la Corte Suprema de la Nación", "Un plebiscito provincial"], "correcta": 1},
    {"pregunta": "En el sistema inquisitivo, a diferencia del acusatorio:",
     "opciones": ["El fiscal investiga y el juez solo decide", "El juez concentra las tareas de investigar y juzgar", "No existen jueces", "El proceso es siempre oral y público"], "correcta": 1},
    {"pregunta": "En el sistema acusatorio, la función de acusar corresponde a:",
     "opciones": ["El juez", "El fiscal", "El defensor", "El Poder Ejecutivo"], "correcta": 1},
    {"pregunta": "La facultad de dictar el Código Penal de fondo corresponde, conforme al artículo 75 inciso 12 de la Constitución Nacional, a:",
     "opciones": ["Cada provincia por separado", "El Congreso de la Nación, correspondiendo su aplicación a las provincias", "La Corte Suprema de Justicia", "El Poder Ejecutivo Nacional"], "correcta": 1},
    {"pregunta": "Entre los mecanismos alternativos que el sistema acusatorio permite al fiscal para disponer de la acción penal se encuentran:",
     "opciones": ["Solo la condena o absolución", "Criterios de oportunidad, conciliación, mediación y suspensión del proceso a prueba, entre otros", "Únicamente el sobreseimiento", "El indulto presidencial"], "correcta": 1},

    # ============================================================
    # TEMA IX - NORMATIVA DE GÉNERO (Ley 26.485)
    # ============================================================
    {"pregunta": "La Ley 26.485 de protección integral a las mujeres tiene por objeto, entre otros fines:",
     "opciones": ["Regular exclusivamente el régimen de visitas", "Promover la eliminación de la discriminación entre mujeres y varones y garantizar una vida sin violencia", "Establecer el régimen de licencias por maternidad", "Modificar el Código Penal exclusivamente"], "correcta": 1},
    {"pregunta": "Según el artículo 4 de la Ley 26.485, se entiende por violencia contra las mujeres:",
     "opciones": ["Solo la violencia física ejercida por el cónyuge", "Toda conducta, basada en razones de género, que afecte su vida, libertad, dignidad o integridad, en el ámbito público o privado", "Únicamente los delitos tipificados en el Código Penal", "Solo la ejercida por agentes del Estado"], "correcta": 1},
    {"pregunta": "¿Cuál de las siguientes NO es un tipo de violencia contra la mujer enumerado en el artículo 5 de la Ley 26.485?",
     "opciones": ["Violencia física", "Violencia simbólica", "Violencia económica y patrimonial", "Violencia contractual"], "correcta": 3},
    {"pregunta": "La violencia doméstica contra las mujeres, como modalidad de la Ley 26.485, se caracteriza porque:",
     "opciones": ["Requiere siempre convivencia entre agresor y víctima", "Es ejercida por un integrante del grupo familiar, sin que sea requisito la convivencia", "Solo puede ser ejercida por el cónyuge", "Excluye a las parejas o noviazgos"], "correcta": 1},
    {"pregunta": "La violencia institucional contra las mujeres, según la Ley 26.485, es aquella ejercida por:",
     "opciones": ["Un integrante del grupo familiar", "Funcionarios o agentes de organismos públicos que retardan u obstaculizan el acceso a políticas públicas o derechos", "Medios de comunicación masivos", "El personal de salud exclusivamente"], "correcta": 1},
    {"pregunta": "La violencia obstétrica, conforme a la Ley 26.485, es la ejercida por:",
     "opciones": ["El empleador sobre la trabajadora embarazada", "El personal de salud sobre el cuerpo y los procesos reproductivos de las mujeres", "Los medios de comunicación", "Los funcionarios judiciales"], "correcta": 1},
    {"pregunta": "La violencia mediática contra las mujeres, según la Ley 26.485, se manifiesta a través de:",
     "opciones": ["Agresiones físicas en la vía pública", "Mensajes e imágenes estereotipados difundidos por medios masivos de comunicación que discriminen o humillen a las mujeres", "El control de los ingresos económicos", "La negativa a otorgar licencias laborales"], "correcta": 1},
    {"pregunta": "Entre los preceptos rectores que deben garantizar los tres poderes del Estado según el artículo 7 de la Ley 26.485 se encuentra:",
     "opciones": ["La eliminación de la discriminación y de las desiguales relaciones de poder sobre las mujeres", "La reducción del presupuesto destinado a políticas de género", "La exclusión de la sociedad civil en su implementación", "La reserva absoluta de toda la información, incluso para la víctima"], "correcta": 0},
    {"pregunta": "La Ley 26.485 es de orden público y de aplicación:",
     "opciones": ["Solo en la Ciudad de Buenos Aires", "En todo el territorio de la República, con las excepciones procesales que la propia ley establece", "Solo en las provincias que adhieran expresamente", "Únicamente en el ámbito laboral"], "correcta": 1},
    {"pregunta": "El trato respetuoso hacia las mujeres que padecen violencia, evitando toda conducta que produzca revictimización, está reconocido en la Ley 26.485 como:",
     "opciones": ["Un derecho protegido de la mujer que padece violencia", "Una facultad discrecional del tribunal", "Una obligación exclusiva de las fuerzas de seguridad", "Un principio que solo aplica en sede penal"], "correcta": 0},
]

# =============================================================================
# UTILIDADES DE PRESENTACIÓN
# =============================================================================

def render_header():
    st.markdown(
        """
        <div class="institucional-header">
            <h1>⚖️ Simulador de Examen de Ingreso al Poder Judicial</h1>
            <p>Provincia de San Juan — Concurso de Aspirantes 2026 · Modo exigente</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_resultado(aprobado: bool, puntaje: float, etiqueta: str = "Puntaje", umbral: float = UMBRAL_APROBACION_TEORICO):
    col1, col2 = st.columns([1, 2])
    with col1:
        if aprobado:
            st.markdown('<div class="badge-aprobado">✅ APROBADO</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="badge-reprobado">❌ NO APROBADO</div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f"**{etiqueta}:** {puntaje:.2f}% &nbsp;&nbsp;|&nbsp;&nbsp; **Umbral oficial de aprobación:** {umbral:.2f}%")


def render_cronometro(segundos_restantes: float, critico_seg: int = 30):
    mins, secs = divmod(max(0, int(segundos_restantes)), 60)
    clase = "cronometro cronometro-critico" if segundos_restantes <= critico_seg else "cronometro"
    st.markdown(f'<div class="{clase}">⏱️ {mins:02d}:{secs:02d}</div>', unsafe_allow_html=True)


def render_diff_dactilografia(texto_modelo: str, transcripcion: str):
    """Muestra el texto modelo resaltando en verde las palabras que
    coinciden con lo escrito, en rojo las que no coinciden, y en gris las
    que no llegaste a escribir."""
    palabras_modelo = texto_modelo.split()
    palabras_usuario = transcripcion.split()
    partes = []
    for i, palabra in enumerate(palabras_modelo):
        if i < len(palabras_usuario):
            if palabras_usuario[i] == palabra:
                partes.append(f'<span style="color:#1E7E34;">{palabra}</span>')
            else:
                partes.append(
                    f'<span style="background:#FBEAEA;color:#B32424;'
                    f'border-bottom:2px solid #B32424;" title="Escribiste: {palabras_usuario[i]}">{palabra}</span>'
                )
        else:
            partes.append(f'<span style="color:#B5BCC4;">{palabra}</span>')
    st.markdown(f'<div class="texto-modelo">{" ".join(partes)}</div>', unsafe_allow_html=True)
    st.caption("🟢 correcta · 🔴 no coincide (pasá el mouse para ver qué escribiste) · ⚪ no llegaste a escribirla")


def registrar_historial(modulo: str, detalle: str, puntaje: float, aprobado: bool):
    st.session_state["historial"].insert(
        0,
        {"modulo": modulo, "detalle": detalle, "puntaje": puntaje, "aprobado": aprobado, "hora": time.strftime("%H:%M:%S")},
    )
    st.session_state["historial"] = st.session_state["historial"][:30]

# =============================================================================
# ESTADO GLOBAL
# =============================================================================

def init_state():
    defaults = {
        "historial": [],
        # Ajustes configurables (como el panel "Ajustes" del simulador comercial)
        "cfg_tiempo_orto_min": 5,
        "cfg_tiempo_dacti_min": 4,
        "cfg_n_errores_orto": 12,
        "cfg_tiempo_teorico_min": 75,
        "cfg_n_preguntas_teorico": len(TEORICO_PREGUNTAS),

        # Ortografía
        "orto_texto_actual": None,
        "orto_tokens": [],
        "orto_errores": {},
        "orto_texto_editable": "",
        "orto_activa": False,
        "orto_finalizada": False,
        "orto_inicio": None,
        "orto_acumulado": 0.0,
        "orto_pausada": False,
        "orto_resultado": None,

        # Dactilografía
        "dacti_texto_actual": None,
        "dacti_iniciada": False,
        "dacti_inicio": None,
        "dacti_transcripcion": "",
        "dacti_finalizada": False,
        "dacti_resultado": None,

        # Teórico
        "teorico_preguntas_sesion": None,
        "teorico_iniciado": False,
        "teorico_inicio": None,
        "teorico_respuestas": {},
        "teorico_evaluado": False,
        "teorico_resultado": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_state()

# =============================================================================
# SIDEBAR — NAVEGACIÓN, AJUSTES E HISTORIAL
# =============================================================================

with st.sidebar:
    st.markdown("### 🏛️ Poder Judicial de San Juan")
    st.caption("Concurso de Aspirantes 2026 · Modo exigente")
    st.markdown("---")
    modulo = st.radio(
        "Seleccione un módulo:",
        [
            "✍️ Módulo 1: Ortografía",
            "⌨️ Módulo 2: Dactilografía",
            "📋 Módulo 3: Examen Teórico",
            "ℹ️ Módulo 4: Instrucciones",
        ],
        label_visibility="collapsed",
    )

    with st.expander("⚙️ Ajustes"):
        st.session_state["cfg_tiempo_orto_min"] = st.number_input(
            "Tiempo ortografía (min)", min_value=1, max_value=30, value=st.session_state["cfg_tiempo_orto_min"]
        )
        st.session_state["cfg_n_errores_orto"] = st.number_input(
            "Cantidad de errores a insertar", min_value=3, max_value=40, value=st.session_state["cfg_n_errores_orto"]
        )
        st.session_state["cfg_tiempo_dacti_min"] = st.number_input(
            "Tiempo dactilografía (min)", min_value=1, max_value=20, value=st.session_state["cfg_tiempo_dacti_min"]
        )
        st.session_state["cfg_tiempo_teorico_min"] = st.number_input(
            "Tiempo examen teórico (min)", min_value=5, max_value=180, value=st.session_state["cfg_tiempo_teorico_min"]
        )
        st.session_state["cfg_n_preguntas_teorico"] = st.number_input(
            "Cantidad de preguntas teórico",
            min_value=5,
            max_value=len(TEORICO_PREGUNTAS),
            value=min(st.session_state["cfg_n_preguntas_teorico"], len(TEORICO_PREGUNTAS)),
        )
        if not AUTOREFRESH_OK:
            st.caption(
                "ℹ️ El paquete `streamlit-autorefresh` no está instalado. "
                "Los cronómetros igual se ven y corren bien (son JavaScript en "
                "el navegador); lo único que cambia es que el corte automático "
                "de la prueba puede demorar unos segundos si no interactuás con "
                "la pantalla. Para el corte instantáneo: "
                "pip install streamlit-autorefresh"
            )

    with st.expander("🕘 Historial de esta sesión"):
        if not st.session_state["historial"]:
            st.caption("Todavía no completaste ninguna práctica.")
        else:
            for h in st.session_state["historial"]:
                icono = "✅" if h["aprobado"] else "❌"
                st.markdown(f"{icono} **{h['modulo']}** — {h['detalle']} — {h['puntaje']:.1f}% ({h['hora']})")

    st.markdown("---")
    st.caption(
        "Simulador no oficial, elaborado a partir de los parámetros "
        "públicos difundidos por la Corte de Justicia de San Juan para "
        "el concurso 2026. Las preguntas del examen teórico se redactaron "
        "en base al CUADERNILLO 2026 oficial (los 9 temas del programa), "
        "pero no son las 100 preguntas exactas del examen real. Verifique "
        "siempre la información oficial en jussanjuan.gov.ar"
    )

render_header()

# =============================================================================
# MÓDULO 1: ORTOGRAFÍA (corrección sobre el texto completo + timer real)
# =============================================================================

if modulo.startswith("✍️"):
    st.markdown('<div class="card"><div class="card-titulo">✍️ Prueba de Ortografía y Redacción Forense</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="aviso-oficial">📌 Parámetro oficial: {st.session_state["cfg_tiempo_orto_min"]} minutos '
        "para corregir un texto con errores ortográficos, aprobando con un mínimo del "
        "75% de los errores corregidos correctamente (Acuerdo General N° 83/26, punto "
        "2.b). Corregí directamente sobre el texto completo, igual que en el examen "
        "real: pueden faltar tildes, confundirse s/c/z, b/v, mp/mb, faltar comas o "
        "puntos, o aparecer confusiones de gramática típicas (haber/a ver, hay/ahí, "
        "halla/haya, tubo/tuvo). El cronómetro corre solo y corta la prueba "
        "automáticamente al llegar a cero.</div>",
        unsafe_allow_html=True,
    )

    articulo = st.selectbox("Seleccione un texto normativo:", list(ORTOGRAFIA_TEXTOS.keys()))

    def _nueva_practica_orto(articulo_sel):
        n_err = int(st.session_state["cfg_n_errores_orto"])
        tokens, errores = generar_practica_ortografia(ORTOGRAFIA_TEXTOS[articulo_sel], n_err)
        st.session_state["orto_texto_actual"] = articulo_sel
        st.session_state["orto_tokens"] = tokens
        st.session_state["orto_errores"] = errores
        st.session_state["orto_texto_editable"] = " ".join(tokens)
        st.session_state["orto_activa"] = False
        st.session_state["orto_finalizada"] = False
        st.session_state["orto_inicio"] = None
        st.session_state["orto_acumulado"] = 0.0
        st.session_state["orto_pausada"] = False
        st.session_state["orto_resultado"] = None

    if st.session_state["orto_texto_actual"] != articulo:
        _nueva_practica_orto(articulo)

    n_palabras = len(st.session_state["orto_tokens"])
    n_orto_gen = sum(1 for e in st.session_state["orto_errores"].values() if e["tipo"] == "ortografia")
    n_punt_gen = sum(1 for e in st.session_state["orto_errores"].values() if e["tipo"] == "puntuacion")
    st.caption(f"Texto de {n_palabras} palabras · {n_orto_gen} errores de ortografía/gramática + {n_punt_gen} de puntuación en esta práctica.")

    col_a, col_b, col_c = st.columns([1, 1, 3])
    with col_a:
        if not st.session_state["orto_activa"] and not st.session_state["orto_finalizada"]:
            if st.button("▶️ Iniciar", type="primary", key="orto_iniciar"):
                st.session_state["orto_activa"] = True
                st.session_state["orto_pausada"] = False
                st.session_state["orto_inicio"] = time.time()
                st.rerun()
        elif st.session_state["orto_activa"]:
            etiqueta_pausa = "⏸️ Detener" if not st.session_state["orto_pausada"] else "▶️ Reanudar"
            if st.button(etiqueta_pausa, key="orto_pausa"):
                if not st.session_state["orto_pausada"]:
                    st.session_state["orto_acumulado"] += time.time() - st.session_state["orto_inicio"]
                    st.session_state["orto_pausada"] = True
                else:
                    st.session_state["orto_inicio"] = time.time()
                    st.session_state["orto_pausada"] = False
                st.rerun()
    with col_b:
        if st.button("🔄 Nueva práctica", key="orto_nueva"):
            _nueva_practica_orto(articulo)
            st.rerun()

    limite_seg = int(st.session_state["cfg_tiempo_orto_min"]) * 60

    def _elapsed_orto():
        acumulado = st.session_state["orto_acumulado"]
        if st.session_state["orto_activa"] and not st.session_state["orto_pausada"]:
            acumulado += time.time() - st.session_state["orto_inicio"]
        return acumulado

    def _evaluar_orto(texto_editado):
        tokens_mostrados = st.session_state["orto_tokens"]
        errores = st.session_state["orto_errores"]
        editado_palabras = texto_editado.split()
        total_errores = len(errores)
        corregidos = 0
        falsos_positivos = 0
        detalle = []
        for idx, token_mostrado in enumerate(tokens_mostrados):
            token_usuario = editado_palabras[idx] if idx < len(editado_palabras) else ""
            if idx in errores:
                info = errores[idx]
                tipo = info["tipo"]
                correcta = info["correcta"]
                if tipo == "puntuacion":
                    ok = token_usuario.rstrip().endswith(correcta)
                    correcta_mostrar = f'"{correcta}" al final de la palabra'
                else:
                    ok = limpiar_palabra(token_usuario) == correcta
                    correcta_mostrar = correcta
                if ok:
                    corregidos += 1
                detalle.append({
                    "idx": idx, "tipo": tipo, "mostrado": token_mostrado,
                    "correcta": correcta_mostrar, "ingresado": token_usuario, "ok": ok,
                })
            else:
                if limpiar_palabra(token_usuario) != limpiar_palabra(token_mostrado):
                    falsos_positivos += 1

        puntaje = 0.0
        if total_errores:
            puntaje = max(0.0, (corregidos - 0.5 * falsos_positivos) / total_errores * 100)
        aprobado = puntaje >= UMBRAL_APROBACION_ORTOGRAFIA
        st.session_state["orto_resultado"] = {
            "total_errores": total_errores,
            "corregidos": corregidos,
            "falsos_positivos": falsos_positivos,
            "puntaje": puntaje,
            "aprobado": aprobado,
            "detalle": detalle,
        }
        st.session_state["orto_finalizada"] = True
        st.session_state["orto_activa"] = False
        registrar_historial("Ortografía", st.session_state["orto_texto_actual"], puntaje, aprobado)

    if st.session_state["orto_activa"]:
        restante = limite_seg - _elapsed_orto()
        if st.session_state["orto_pausada"]:
            render_cronometro(max(0, restante))
        else:
            render_cronometro(max(0, restante))
        if restante <= 0 and not st.session_state["orto_finalizada"]:
            _evaluar_orto(st.session_state.get("orto_area_widget", st.session_state["orto_texto_editable"]))
            # Sin st.rerun() acá a propósito: el estado ya quedó actualizado
            # y el resto del script lo refleja en esta misma pasada.
        # El cronómetro JS de arriba solo bloquea el textarea visualmente al
        # llegar a cero (no clickea ningún botón: hacerlo generaba un
        # "NotFoundError: removeChild" al chocar con la reconciliación de
        # React). El corte real en el servidor lo dispara este autorefresh,
        # que es el mecanismo que Streamlit sí soporta para forzar reruns.
        if not st.session_state["orto_finalizada"] and not st.session_state["orto_pausada"] and AUTOREFRESH_OK:
            st_autorefresh(interval=1500, key="orto_autorefresh")

    if st.session_state["orto_activa"]:
        st.write("**Corrija directamente en el siguiente cuadro los errores ortográficos que encuentre:**")
        texto_editado = st.text_area(
            "Texto a corregir",
            value=st.session_state["orto_texto_editable"],
            height=380,
            key="orto_area_widget",
            label_visibility="collapsed",
        )
        st.session_state["orto_texto_editable"] = texto_editado

        if st.button("⏹️ Finalizar y corregir", type="primary", key="orto_finalizar"):
            st.session_state["orto_acumulado"] = _elapsed_orto()
            _evaluar_orto(texto_editado)
            st.rerun()
    elif not st.session_state["orto_finalizada"]:
        st.markdown(f'<div class="texto-modelo">{st.session_state["orto_texto_editable"]}</div>', unsafe_allow_html=True)
        st.caption("Presioná ▶️ Iniciar para habilitar la edición y arrancar el cronómetro.")

    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state["orto_finalizada"] and st.session_state["orto_resultado"]:
        r = st.session_state["orto_resultado"]
        st.markdown('<div class="card"><div class="card-titulo">Resultado de la corrección</div>', unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        m1.metric("Errores en el texto", r["total_errores"])
        m2.metric("Corregidos correctamente", r["corregidos"])
        m3.metric("Falsos positivos (editaste algo que estaba bien)", r["falsos_positivos"])
        render_resultado(r["aprobado"], r["puntaje"], umbral=UMBRAL_APROBACION_ORTOGRAFIA)

        st.markdown("#### Detalle")
        for item in r["detalle"]:
            icono = "✅" if item["ok"] else "❌"
            etiqueta_tipo = "🔤 Ortografía/gramática" if item["tipo"] == "ortografia" else "✍️ Puntuación"
            st.markdown(
                f"{icono} {etiqueta_tipo} — Palabra mostrada: `{item['mostrado']}` &nbsp;→&nbsp; "
                f"Corrección esperada: `{item['correcta']}` &nbsp;→&nbsp; "
                f"Usted ingresó: `{item['ingresado'] if item['ingresado'] else '(vacío)'}`"
            )
        if r["falsos_positivos"]:
            st.caption(f"⚠️ Además modificaste {r['falsos_positivos']} palabra(s) que en realidad estaban bien escritas (penalizan el puntaje).")
        st.markdown("</div>", unsafe_allow_html=True)


# =============================================================================
# MÓDULO 2: DACTILOGRAFÍA (timer real que corta la prueba)
# =============================================================================

elif modulo.startswith("⌨️"):
    st.markdown('<div class="card"><div class="card-titulo">⌨️ Prueba de Dactilografía y Velocidad</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="aviso-oficial">📌 Parámetro oficial: {st.session_state["cfg_tiempo_dacti_min"]} minutos para '
        "transcribir de manera textual y sin modificaciones al menos 100 palabras "
        "correctas de un texto jurídico. El texto modelo es a propósito más largo "
        "que esas 100 palabras (no hace falta llegar al final): lo que importa es "
        "cuántas palabras correctas lograste transcribir cuando se corta el tiempo. "
        "La prueba se corta sola al agotarse el tiempo.</div>",
        unsafe_allow_html=True,
    )

    texto_sel = st.selectbox("Seleccione el texto modelo:", list(DACTILOGRAFIA_TEXTOS.keys()))

    if st.session_state["dacti_texto_actual"] != texto_sel:
        st.session_state["dacti_texto_actual"] = texto_sel
        st.session_state["dacti_iniciada"] = False
        st.session_state["dacti_inicio"] = None
        st.session_state["dacti_transcripcion"] = ""
        st.session_state["dacti_finalizada"] = False
        st.session_state["dacti_resultado"] = None

    texto_modelo = DACTILOGRAFIA_TEXTOS[texto_sel]
    n_palabras_modelo = len(texto_modelo.split())
    limite_seg = int(st.session_state["cfg_tiempo_dacti_min"]) * 60

    def _evaluar_dacti(transcripcion, tiempo_final):
        palabras_modelo = texto_modelo.split()
        palabras_usuario = transcripcion.split()
        coincidencias = 0
        for i, palabra_modelo in enumerate(palabras_modelo):
            if i < len(palabras_usuario) and palabras_usuario[i] == palabra_modelo:
                coincidencias += 1
        total_palabras_escritas = len(palabras_usuario)
        ppm = (total_palabras_escritas / tiempo_final) * 60 if tiempo_final > 0 else 0
        precision = (coincidencias / len(palabras_modelo)) * 100 if palabras_modelo else 0
        # Margen de tolerancia: cuando el corte es automático, "tiempo_final"
        # SIEMPRE va a ser un poquito mayor al límite exacto (el reloj tickea
        # cada 250ms y el clic tarda un instante en llegar al servidor). Ese
        # desfasaje es latencia técnica, no tiempo extra que el usuario usó
        # para escribir, así que no debe hacer reprobar a alguien que llegó
        # a las 100 palabras dentro del tiempo real.
        aprobado_oficial = (
            coincidencias >= PALABRAS_MINIMAS_DACTILOGRAFIA
            and tiempo_final <= limite_seg + MARGEN_LATENCIA_SEG
        )
        st.session_state["dacti_finalizada"] = True
        st.session_state["dacti_iniciada"] = False
        st.session_state["dacti_resultado"] = {
            "tiempo_seg": tiempo_final, "ppm": ppm, "precision": precision,
            "coincidencias": coincidencias, "total_modelo": len(palabras_modelo),
            "total_escritas": total_palabras_escritas, "aprobado": aprobado_oficial,
            "transcripcion": transcripcion, "texto_modelo": texto_modelo,
        }
        registrar_historial("Dactilografía", texto_sel, precision, aprobado_oficial)

    if not st.session_state["dacti_iniciada"] and not st.session_state["dacti_finalizada"]:
        st.write(f"**Texto modelo** ({n_palabras_modelo} palabras):")
        st.markdown(f'<div class="texto-modelo">{texto_modelo}</div>', unsafe_allow_html=True)
        if st.button("▶️ Comenzar Prueba", type="primary"):
            st.session_state["dacti_iniciada"] = True
            st.session_state["dacti_inicio"] = time.time()
            st.session_state["dacti_finalizada"] = False
            st.rerun()
    elif st.session_state["dacti_iniciada"]:
        transcurrido = time.time() - st.session_state["dacti_inicio"]
        restante = limite_seg - transcurrido
        render_cronometro(max(0, restante))

        if restante <= 0:
            st.warning("⏱️ Se agotó el tiempo. La prueba se corrigió automáticamente con lo transcripto hasta ahora.")
            # Se registra el tiempo REAL transcurrido (puede ser un poco mayor
            # a limite_seg por el margen del autorefresh), nunca el límite
            # nominal: usar limite_seg acá inflaba el resultado porque la
            # condición de aprobación "tiempo_final <= limite_seg" quedaba
            # siempre en True aunque el corte hubiera llegado tarde.
            _evaluar_dacti(st.session_state.get("dacti_input_area", ""), transcurrido)
            # Sin st.rerun() acá a propósito (ver nota en Ortografía): evita
            # chocar con el rerun que ya disparó el autorefresh. El estado
            # queda actualizado y el resultado se muestra en esta misma pasada.
        else:
            col_texto, col_input = st.columns([1, 1])
            with col_texto:
                st.write(f"**Texto modelo** ({n_palabras_modelo} palabras):")
                st.markdown(
                    '<div style="position: sticky; top: 12px; z-index: 5;">'
                    f'<div class="texto-modelo" style="height:340px; overflow-y:auto;">{texto_modelo}</div>'
                    "</div>",
                    unsafe_allow_html=True,
                )
            with col_input:
                st.write("**Tu transcripción:**")
                transcripcion = st.text_area(
                    "Transcriba el texto exactamente como aparece a la izquierda:",
                    height=340,
                    key="dacti_input_area",
                    label_visibility="collapsed",
                )
            st.session_state["dacti_transcripcion"] = transcripcion

            col_a, col_b = st.columns([1, 5])
            with col_a:
                finalizar = st.button("⏹️ Finalizar", type="primary")
            with col_b:
                if st.button("Cancelar / Reiniciar"):
                    st.session_state["dacti_iniciada"] = False
                    st.session_state["dacti_finalizada"] = False
                    st.rerun()

            if finalizar:
                tiempo_final = time.time() - st.session_state["dacti_inicio"]
                _evaluar_dacti(transcripcion, tiempo_final)
                st.rerun()

            # El cronómetro JS de arriba solo bloquea el textarea
            # visualmente al llegar a cero (no clickea ningún botón: eso
            # generaba "NotFoundError: removeChild" al chocar con React).
            # El corte real en el servidor lo dispara este autorefresh.
            if AUTOREFRESH_OK:
                st_autorefresh(interval=1500, key="dacti_autorefresh")

    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state["dacti_finalizada"] and st.session_state["dacti_resultado"]:
        r = st.session_state["dacti_resultado"]
        st.markdown('<div class="card"><div class="card-titulo">Resultado de la prueba de dactilografía</div>', unsafe_allow_html=True)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Tiempo empleado", f"{r['tiempo_seg']:.1f} s")
        m2.metric("Palabras por minuto", f"{r['ppm']:.1f} PPM")
        m3.metric("Palabras correctas", f"{r['coincidencias']}/{r['total_modelo']}")
        m4.metric("Precisión", f"{r['precision']:.2f}%")
        col1, col2 = st.columns([1, 2])
        with col1:
            if r["aprobado"]:
                st.markdown('<div class="badge-aprobado">✅ APROBADO</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="badge-reprobado">❌ NO APROBADO</div>', unsafe_allow_html=True)
        with col2:
            st.markdown(
                f"**Criterio oficial:** transcribir correctamente al menos "
                f"**{PALABRAS_MINIMAS_DACTILOGRAFIA} palabras** dentro de "
                f"**{st.session_state['cfg_tiempo_dacti_min']} minutos**."
            )

        st.markdown("#### Dónde te confundiste")
        render_diff_dactilografia(r["texto_modelo"], r["transcripcion"])

        if st.button("🔁 Repetir este texto", key="dacti_repetir"):
            st.session_state["dacti_iniciada"] = False
            st.session_state["dacti_finalizada"] = False
            st.session_state["dacti_resultado"] = None
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# MÓDULO 3: EXAMEN TEÓRICO TÉCNICO (timer real de 75 min + banco ampliado)
# =============================================================================

elif modulo.startswith("📋"):
    st.markdown('<div class="card"><div class="card-titulo">📋 Examen Teórico Técnico</div>', unsafe_allow_html=True)
    n_preg_cfg = int(st.session_state["cfg_n_preguntas_teorico"])
    tiempo_cfg = int(st.session_state["cfg_tiempo_teorico_min"])
    st.markdown(
        f'<div class="aviso-oficial">📌 Parámetro oficial: cuadernillo de 100 preguntas '
        f"en 75 minutos, con un mínimo de 71 respuestas correctas para aprobar (71.00%). "
        f"Esta práctica está configurada en {n_preg_cfg} preguntas / {tiempo_cfg} minutos "
        "(ajustable en el panel de Ajustes), redactadas sobre los 9 temas del "
        "CUADERNILLO 2026 oficial: Derecho Constitucional, Constitución Provincial, "
        "Organización del Poder Judicial de San Juan, Ministerio Público, Civil y "
        "Procesal Civil, Laboral y Procesal Laboral, Familias, Penal y Procesal Penal, "
        "y Normativa de Género. El examen se autoenvía si se acaba el tiempo.</div>",
        unsafe_allow_html=True,
    )

    limite_seg_teo = tiempo_cfg * 60

    def _armar_preguntas_sesion():
        banco = TEORICO_PREGUNTAS[:]
        random.shuffle(banco)
        st.session_state["teorico_preguntas_sesion"] = banco[:n_preg_cfg]
        st.session_state["teorico_respuestas"] = {}
        st.session_state["teorico_evaluado"] = False
        st.session_state["teorico_resultado"] = None

    if st.session_state["teorico_preguntas_sesion"] is None:
        _armar_preguntas_sesion()

    col_i, col_n = st.columns([1, 1])
    with col_i:
        if not st.session_state["teorico_iniciado"]:
            if st.button("▶️ Iniciar examen", type="primary"):
                st.session_state["teorico_iniciado"] = True
                st.session_state["teorico_inicio"] = time.time()
                st.rerun()
    with col_n:
        if st.button("🔄 Nuevo cuestionario (preguntas al azar)"):
            _armar_preguntas_sesion()
            st.session_state["teorico_iniciado"] = False
            st.rerun()

    def _evaluar_teorico(respuestas_usuario):
        preguntas = st.session_state["teorico_preguntas_sesion"]
        total = len(preguntas)
        correctas = 0
        detalle = []
        for i, pregunta in enumerate(preguntas):
            respuesta = respuestas_usuario.get(i)
            ok = respuesta == pregunta["correcta"]
            if ok:
                correctas += 1
            detalle.append({
                "pregunta": pregunta["pregunta"],
                "respuesta_correcta": pregunta["opciones"][pregunta["correcta"]],
                "respuesta_usuario": pregunta["opciones"][respuesta] if respuesta is not None else "(sin responder)",
                "ok": ok,
            })
        incorrectas = total - correctas
        puntaje = (correctas / total) * 100 if total else 0
        aprobado = puntaje >= UMBRAL_APROBACION_TEORICO
        st.session_state["teorico_evaluado"] = True
        st.session_state["teorico_iniciado"] = False
        st.session_state["teorico_resultado"] = {
            "correctas": correctas, "incorrectas": incorrectas, "total": total,
            "puntaje": puntaje, "aprobado": aprobado, "detalle": detalle,
        }
        registrar_historial("Teórico", f"{total} preguntas", puntaje, aprobado)

    if st.session_state["teorico_iniciado"]:
        transcurrido = time.time() - st.session_state["teorico_inicio"]
        restante = limite_seg_teo - transcurrido
        render_cronometro(max(0, restante), critico_seg=120)

        if restante <= 0:
            st.warning("⏱️ Se agotó el tiempo. El examen se envió automáticamente con las respuestas marcadas hasta el momento.")
            _evaluar_teorico(st.session_state["teorico_respuestas"])
            # Sin st.rerun() acá a propósito (ver nota en Ortografía/Dactilografía).
        else:
            if AUTOREFRESH_OK:
                st_autorefresh(interval=4000, key="teorico_autorefresh")

            preguntas = st.session_state["teorico_preguntas_sesion"]
            with st.form("form_teorico"):
                respuestas_usuario = {}
                for i, pregunta in enumerate(preguntas):
                    st.markdown(f"**{i + 1}. {pregunta['pregunta']}**")
                    respuestas_usuario[i] = st.radio(
                        f"pregunta_{i}",
                        options=list(range(len(pregunta["opciones"]))),
                        format_func=lambda x, p=pregunta: p["opciones"][x],
                        key=f"teorico_q_{i}",
                        label_visibility="collapsed",
                        index=None,
                    )
                    st.markdown("---")
                enviar = st.form_submit_button("Enviar Examen", type="primary")

            if enviar:
                _evaluar_teorico(respuestas_usuario)
                st.rerun()
            else:
                st.session_state["teorico_respuestas"] = respuestas_usuario

    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state["teorico_evaluado"] and st.session_state["teorico_resultado"]:
        r = st.session_state["teorico_resultado"]
        st.markdown('<div class="card"><div class="card-titulo">Resultado del examen teórico</div>', unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        m1.metric("Respuestas correctas", f"{r['correctas']}/{r['total']}")
        m2.metric("Respuestas incorrectas", r["incorrectas"])
        m3.metric("Puntaje", f"{r['puntaje']:.2f}%")
        render_resultado(r["aprobado"], r["puntaje"])

        with st.expander("Ver detalle de respuestas"):
            for item in r["detalle"]:
                icono = "✅" if item["ok"] else "❌"
                st.markdown(
                    f"{icono} **{item['pregunta']}**  \n"
                    f"Respuesta correcta: *{item['respuesta_correcta']}* &nbsp;|&nbsp; "
                    f"Su respuesta: *{item['respuesta_usuario']}*"
                )
        st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# MÓDULO 4: INSTRUCCIONES
# =============================================================================

else:
    st.markdown('<div class="card"><div class="card-titulo">ℹ️ Instrucciones del Simulador</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
Este simulador reproduce los parámetros oficiales difundidos por la
**Corte de Justicia de San Juan** para el **Concurso de Aspirantes 2026**,
en un modo más exigente que replica el comportamiento de un simulador
comercial: los tiempos cortan la prueba solos, los errores de ortografía
se generan al azar en cada intento y la corrección se hace palabra por
palabra, igual que en el examen real.

### Las 5 instancias eliminatorias del concurso real

1. **Prueba de dactilografía** — {st.session_state['cfg_tiempo_dacti_min']} minutos para transcribir
   correctamente 100 palabras de un texto jurídico, de forma textual y sin modificaciones.
2. **Prueba de ortografía** — {st.session_state['cfg_tiempo_orto_min']} minutos para corregir un texto con
   errores ortográficos.
3. **Curso virtual obligatorio** (Escuela Judicial) — asincrónico y autogestionado.
4. **Prueba de conocimientos teóricos** — cuadernillo de 100 preguntas, 75 minutos,
   se requieren **71 respuestas correctas** para aprobar.
5. **Entrevista personal** — obligatoria y eliminatoria (no evaluada en este simulador).

### Qué cambia respecto de la versión anterior

- **Ortografía:** banco de {len(ORTOGRAFIA_TEXTOS)} textos jurídicos más largos; los errores se
  generan al azar en cada práctica (no siempre los mismos): confusiones de s/c/z, b/v y
  mp/mb, tildes, comas y puntos faltantes, y confusiones de gramática/homófonos (haber/a
  ver, hay/ahí, halla/haya). Se corrige sobre el texto completo, como en el examen real,
  y se penaliza corregir palabras que en realidad estaban bien escritas.
- **Dactilografía:** textos de ~230 a 350 palabras (más largos que las 100 exigidas, a
  propósito) y el cronómetro corta la prueba solo al llegar a cero.
- **Teórico:** banco de {len(TEORICO_PREGUNTAS)} preguntas redactadas sobre los 9 temas del
  CUADERNILLO 2026 oficial, con selección aleatoria en cada práctica y cronómetro de 75
  minutos que autoenvía el examen.
- **Ajustes:** podés configurar tiempos y cantidades desde el panel lateral.
- **Historial:** cada práctica completada queda registrada en la barra lateral
  durante la sesión.

### Criterio de aprobación

En todas las instancias evaluables, el umbral de aprobación aplicado es
**≥ 71.00%**, en línea con el criterio oficial (71 de 100 respuestas
correctas) del examen teórico del concurso.

> ⚠️ **Aviso:** este es un simulador no oficial con fines de práctica. Las
> preguntas del examen teórico se redactaron en base al CUADERNILLO 2026
> oficial, pero no son las 100 preguntas exactas del examen real (que la
> Corte no publica). La información y los parámetros pueden actualizarse:
> consulte siempre la fuente oficial en **jussanjuan.gov.ar**.
        """
    )
    st.markdown("</div>", unsafe_allow_html=True)
