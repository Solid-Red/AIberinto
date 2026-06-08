import urllib.request
import urllib.error
import json
import random
from config import (
    OLLAMA_URL, OLLAMA_MODEL, INTELLIGENCES,
    INT_LOGICAL, INT_LINGUISTIC, INT_SPATIAL, INT_MUSICAL,
    INT_KINESTHETIC, INT_INTRAPERSONAL, INT_INTERPERSONAL, INT_NATURALIST
)

class AIClient:
    def __init__(self):
        self.offline_mode = False
        self.check_connection()
        
        # Base de datos narrativa de contingencia (Offline Fallback - 20 desafíos)
        self.fallback_rooms = [
            {
                "narrativa": "Te topas con una gran cara de piedra tallada en la pared. Sus ojos brillan levemente y te dice: 'Soy el guardián de las runas. Resuelve este acertijo: Se rompe al pronunciar su nombre. ¿Qué soy?'",
                "inteligencia_evaluada": INT_LINGUISTIC,
                "opciones": [
                    {
                        "texto": "Responder poéticamente: 'Eres el Silencio, el manto invisible que cubre este calabozo'.",
                        "respuesta_resultado": "La estatua sonríe con polvo de piedra y se abre, alabando tu elocuencia. Sientes tu mente más aguda.",
                        "puntaje": {INT_LINGUISTIC: 2}
                    },
                    {
                        "texto": "Analizarlo lógicamente: 'El Silencio es la única respuesta correcta que cumple la condición física del enigma'.",
                        "respuesta_resultado": "La estatua asiente solemnemente. Valoró tu precisión racional.",
                        "puntaje": {INT_LOGICAL: 2}
                    },
                    {
                        "texto": "Golpear la estatua con tu escudo para romper el mecanismo del acertijo.",
                        "respuesta_resultado": "La estatua cruje y se rompe por el impacto. Consigues pasar por la fuerza bruta.",
                        "puntaje": {INT_KINESTHETIC: 2}
                    }
                ]
            },
            {
                "narrativa": "Llegas a una sala donde el suelo está compuesto por grandes baldosas de piedra numeradas (2, 4, 8...). Una reja de hierro bloquea la salida y una placa dice: 'Pisa el eslabón de la progresión'.",
                "inteligencia_evaluada": INT_LOGICAL,
                "opciones": [
                    {
                        "texto": "Pisar la baldosa con el número 16 (duplicando el valor anterior de la serie exponencial).",
                        "respuesta_resultado": "Se escucha un mecanismo de engranajes y la reja se abre limpiamente.",
                        "puntaje": {INT_LOGICAL: 2}
                    },
                    {
                        "texto": "Examinar los relieves tridimensionales de las baldosas para ver si hay desgaste físico en alguna de ellas.",
                        "respuesta_resultado": "Notas que el relieve de la baldosa 16 tiene marcas de presión ocultas. La pisas y pasas.",
                        "puntaje": {INT_SPATIAL: 2}
                    },
                    {
                        "texto": "Derramar agua de tu cantimplora para ver qué baldosas absorben el líquido de forma diferente.",
                        "respuesta_resultado": "El agua revela una hendidura en la losa 16. La pisas y la reja se levanta.",
                        "puntaje": {INT_NATURALIST: 2}
                    }
                ]
            },
            {
                "narrativa": "Una sala circular contiene tres campanas de bronce suspendidas. Al golpearlas, notas que emiten notas armónicas y vibran de forma peculiar. Hay un grabado de un pentagrama sin notas.",
                "inteligencia_evaluada": INT_MUSICAL,
                "opciones": [
                    {
                        "texto": "Tocar las campanas en orden ascendente y tararear una melodía que complete la tercera armónica.",
                        "respuesta_resultado": "El sonido vibra en las paredes y la puerta se abre por resonancia sonora.",
                        "puntaje": {INT_MUSICAL: 2}
                    },
                    {
                        "texto": "Analizar la tensión de las cuerdas y la masa de las campanas para deducir cuál tiene más peso físico.",
                        "respuesta_resultado": "Determinas la campana correcta por su física. Al golpearla, activa la puerta.",
                        "puntaje": {INT_LOGICAL: 2}
                    },
                    {
                        "texto": "Sentarte a escuchar el zumbido de fondo, meditando en cómo te afecta emocionalmente el tono.",
                        "respuesta_resultado": "Encuentras paz en la resonancia. Al levantarte, tu intuición te guía al botón correcto.",
                        "puntaje": {INT_INTRAPERSONAL: 2}
                    }
                ]
            },
            {
                "narrativa": "Un foso con enredaderas de espinas venenosas bloquea tu paso. Las plantas parecen reaccionar al movimiento y vibran amenazadoramente cuando te acercas.",
                "inteligencia_evaluada": INT_NATURALIST,
                "opciones": [
                    {
                        "texto": "Estudiar el patrón botánico de las hojas para identificar si son sensibles a la luz de tu antorcha.",
                        "respuesta_resultado": "Descubres que repelen la luz. Usas la antorcha para ahuyentarlas sin dañarlas.",
                        "puntaje": {INT_NATURALIST: 2}
                    },
                    {
                        "texto": "Usar tu espada templada para cortar las enredaderas con movimientos rápidos y precisos.",
                        "respuesta_resultado": "Esquivas las espinas con agilidad y cortas el paso. Tu cuerpo responde perfectamente.",
                        "puntaje": {INT_KINESTHETIC: 2}
                    },
                    {
                        "texto": "Cantar un silbido suave e imitativo de un pájaro del bosque para camuflar tu presencia acústica.",
                        "respuesta_resultado": "Las enredaderas confunden el sonido con el entorno natural y se relajan, dejándote pasar.",
                        "puntaje": {INT_INTERPERSONAL: 2}
                    }
                ]
            },
            {
                "narrativa": "Encuentras un espejo de cristal oscuro. Al mirarte, no ves tu reflejo físico, sino tus mayores miedos y fracasos proyectados como fantasmas de humo.",
                "inteligencia_evaluada": INT_INTRAPERSONAL,
                "opciones": [
                    {
                        "texto": "Cerrar los ojos, respirar hondo y aceptar esas dudas como parte de tu propio ser y crecimiento.",
                        "respuesta_resultado": "Al aceptarlo, los fantasmas del espejo se disuelven y el cristal se abre como un pasaje.",
                        "puntaje": {INT_INTRAPERSONAL: 2}
                    },
                    {
                        "texto": "Recitar un juramento de caballero en voz alta para reafirmar tu fuerza de voluntad a través del lenguaje.",
                        "respuesta_resultado": "Tus palabras firmes hacen estallar el cristal ilusorio. El camino queda libre.",
                        "puntaje": {INT_LINGUISTIC: 2}
                    },
                    {
                        "texto": "Analizar la refracción de la luz en los bordes del espejo para buscar el interruptor del mecanismo.",
                        "respuesta_resultado": "Ignoras la ilusión mental y encuentras la palanca oculta en el marco del espejo.",
                        "puntaje": {INT_SPATIAL: 2}
                    }
                ]
            },
            {
                "narrativa": "Un goblin guardia herido y exhausto bloquea la puerta de salida. Te apunta con una ballesta temblorosa, asustado de tu armadura de acero.",
                "inteligencia_evaluada": INT_INTERPERSONAL,
                "opciones": [
                    {
                        "texto": "Bajar tu espada, hablarle con tono calmado y ofrecerle tus vendas y raciones de comida.",
                        "respuesta_resultado": "El goblin baja la ballesta, llorando de alivio. Te entrega la llave agradecido.",
                        "puntaje": {INT_INTERPERSONAL: 2}
                    },
                    {
                        "texto": "Proponerle un trato: tú le das una moneda de oro a cambio de la llave y de no reportar su fracaso.",
                        "respuesta_resultado": "El goblin sopesa la oferta comercial. Acepta el intercambio lógico de inmediato.",
                        "puntaje": {INT_LOGICAL: 2}
                    },
                    {
                        "texto": "Cargar hacia él con tu escudo para desarmarlo antes de que pueda disparar.",
                        "respuesta_resultado": "Usa tu fuerza física para noquearlo limpiamente. Tomas la llave de su cinturón.",
                        "puntaje": {INT_KINESTHETIC: 2}
                    }
                ]
            },
            {
                "narrativa": "La sala contiene una pintura abstracta gigante en el muro. Notas que al moverte lateralmente en la sala, la perspectiva de la pintura cambia revelando un laberinto visual.",
                "inteligencia_evaluada": INT_SPATIAL,
                "opciones": [
                    {
                        "texto": "Moverte de forma que alinees las sombras del calabozo con las líneas de la pintura para resolver el puzzle.",
                        "respuesta_resultado": "Los trazos se alinean tridimensionalmente y el muro rota, abriendo paso.",
                        "puntaje": {INT_SPATIAL: 2}
                    },
                    {
                        "texto": "Leer las pequeñas runas explicativas grabadas en los bordes del marco.",
                        "respuesta_resultado": "Traduces el texto antiguo que te indica la contraseña verbal para abrir la puerta.",
                        "puntaje": {INT_LINGUISTIC: 2}
                    },
                    {
                        "texto": "Confiar en tu sentido interno de orientación y cruzar la sala con paso firme sin mirar las ilusiones.",
                        "respuesta_resultado": "Mantienes la calma y cruzas. Tu templanza mental evita que caigas en las trampas.",
                        "puntaje": {INT_INTRAPERSONAL: 2}
                    }
                ]
            },
            {
                "narrativa": "Un foso profundo con un puente roto y un péndulo de piedra oscilante te separa de la salida. El péndulo oscila con fuerza letal.",
                "inteligencia_evaluada": INT_KINESTHETIC,
                "opciones": [
                    {
                        "texto": "Calcular el tiempo de oscilación, tomar carrera y saltar en el momento de menor aceleración del péndulo.",
                        "respuesta_resultado": "Saltas con agilidad atlética perfecta, pasando justo al otro lado del foso.",
                        "puntaje": {INT_KINESTHETIC: 2}
                    },
                    {
                        "texto": "Calcular la velocidad angular y el ángulo de impacto del péndulo para resolver cuándo se detendrá.",
                        "respuesta_resultado": "Encuentras el punto muerto del péndulo y caminas en el momento exacto.",
                        "puntaje": {INT_LOGICAL: 2}
                    },
                    {
                        "texto": "Untar musgo resbaladizo del calabozo en el eje superior para frenar la oscilación.",
                        "respuesta_resultado": "El musgo orgánico ralentiza la maquinaria, deteniendo el péndulo para cruzar seguro.",
                        "puntaje": {INT_NATURALIST: 2}
                    }
                ]
            },
            # --- NUEVOS DESAFÍOS (9 a 20) ---
            {
                "narrativa": "Encuentras un mural de piedra con letras desordenadas grabadas en relieve. Una inscripción dice: 'Ordena tu mente: ARMOA. El sentimiento que une al caballero con su tierra'.",
                "inteligencia_evaluada": INT_LINGUISTIC,
                "opciones": [
                    {
                        "texto": "Reordenar las letras en la palabra 'AMOR' y pronunciarla solemnemente frente al altar.",
                        "respuesta_resultado": "El mural brilla con una luz cálida y se desliza hacia un lado, alabando tu ingenio lingüístico.",
                        "puntaje": {INT_LINGUISTIC: 2}
                    },
                    {
                        "texto": "Calcular la probabilidad matemática de combinaciones para forzar el cerrojo del alfabeto.",
                        "respuesta_resultado": "Tus cálculos lógicos te guían al orden correcto en pocos intentos.",
                        "puntaje": {INT_LOGICAL: 2}
                    },
                    {
                        "texto": "Golpear la baldosa central del mural donde se concentran los engranajes mecánicos del relieve.",
                        "respuesta_resultado": "Tu fuerza física deforma el mecanismo y libera el cerrojo por la fuerza.",
                        "puntaje": {INT_KINESTHETIC: 2}
                    }
                ]
            },
            {
                "narrativa": "Una mesa tiene una balanza de bronce y cuatro pesas de piedra que lucen idénticas pero tienen ligeras diferencias. Una placa reza: 'Solo el peso del equilibrio te abrirá la puerta'.",
                "inteligencia_evaluada": INT_LOGICAL,
                "opciones": [
                    {
                        "texto": "Realizar mediciones sistemáticas combinando pares de pesas en la balanza para deducir el orden matemático de peso.",
                        "respuesta_resultado": "Resuelves el enigma matemático con lógica impecable. La reja trasera se levanta.",
                        "puntaje": {INT_LOGICAL: 2}
                    },
                    {
                        "texto": "Medir el volumen visual y estimar la densidad tridimensional de cada piedra al sostenerlas.",
                        "respuesta_resultado": "Tu instinto espacial y visual te permite equilibrar la balanza rápidamente.",
                        "puntaje": {INT_SPATIAL: 2}
                    },
                    {
                        "texto": "Sopesar las piedras en tus manos directamente para sentir la gravedad mediante tu sensibilidad muscular corporal.",
                        "respuesta_resultado": "Tu fina destreza cenestésica capta la diferencia de peso exacta y resuelves el reto.",
                        "puntaje": {INT_KINESTHETIC: 2}
                    }
                ]
            },
            {
                "narrativa": "El techo de esta sala simula una bóveda celeste nocturna con cristales que simulan estrellas. En el suelo hay grabados con formas geométricas complejas.",
                "inteligencia_evaluada": INT_SPATIAL,
                "opciones": [
                    {
                        "texto": "Alinear la perspectiva visual de los cristales del techo con los grabados del suelo rotando unos espejos.",
                        "respuesta_resultado": "El alineamiento geométrico refleja la luz de forma exacta, abriendo el pasaje secreto.",
                        "puntaje": {INT_SPATIAL: 2}
                    },
                    {
                        "texto": "Analizar la relación angular de los cristales utilizando trigonometría mental.",
                        "respuesta_resultado": "Calculas la posición teórica correcta del mecanismo por pura geometría analítica.",
                        "puntaje": {INT_LOGICAL: 2}
                    },
                    {
                        "texto": "Buscar restos de musgo acumulados en los grabados que indiquen qué espejos han sido rotados recientemente por otros.",
                        "respuesta_resultado": "Tu observación naturalista de las marcas orgánicas revela los espejos correctos.",
                        "puntaje": {INT_NATURALIST: 2}
                    }
                ]
            },
            {
                "narrativa": "El agua gotea rítmicamente desde el techo en cuatro cuencos de piedra de diferentes tamaños, creando una percusión hueca que resuena en la bóveda.",
                "inteligencia_evaluada": INT_MUSICAL,
                "opciones": [
                    {
                        "texto": "Reorganizar la posición de los cuencos para crear un patrón de compás armónico de cuatro tiempos.",
                        "respuesta_resultado": "La acústica armónica reverbera con fuerza y activa un interruptor sónico en las paredes.",
                        "puntaje": {INT_MUSICAL: 2}
                    },
                    {
                        "texto": "Medir el nivel de líquido de cada cuenco para deducir la relación matemática de velocidad de goteo.",
                        "respuesta_resultado": "Tu análisis matemático del volumen del agua te guía al patrón correcto.",
                        "puntaje": {INT_LOGICAL: 2}
                    },
                    {
                        "texto": "Usar la velocidad de tu cuerpo para golpear los cuencos en un tempo exacto y rápido.",
                        "respuesta_resultado": "Tu coordinación motora emula el ritmo perfecto y activa la compuerta.",
                        "puntaje": {INT_KINESTHETIC: 2}
                    }
                ]
            },
            {
                "narrativa": "Una fosa con estacas afiladas se interpone en tu camino. La única forma de cruzar es saltando sobre una serie de troncos cilíndricos flotantes que giran en falso.",
                "inteligencia_evaluada": INT_KINESTHETIC,
                "opciones": [
                    {
                        "texto": "Saltar con rapidez y precisión, usando tus brazos para equilibrar dinámicamente tu centro de gravedad en cada impacto.",
                        "respuesta_resultado": "Cruzas de un salto acrobático asombroso. Tu cuerpo responde con agilidad suprema.",
                        "puntaje": {INT_KINESTHETIC: 2}
                    },
                    {
                        "texto": "Calcular los momentos de inercia y la velocidad de rotación de cada tronco antes de dar el primer paso.",
                        "respuesta_resultado": "Tu física teórica te permite saber con precisión matemática dónde pararte.",
                        "puntaje": {INT_LOGICAL: 2}
                    },
                    {
                        "texto": "Estudiar la humedad y la corteza de los troncos para identificar los que son menos resbaladizos por no tener musgo.",
                        "respuesta_resultado": "Tu conocimiento de las plantas te ayuda a elegir los troncos seguros y cruzas sin resbalar.",
                        "puntaje": {INT_NATURALIST: 2}
                    }
                ]
            },
            {
                "narrativa": "Un jardín subterráneo de hongos luminosos y líquenes florece aquí. Para continuar, debes recolectar el hongo curativo correcto para disolver una barrera de esporas venenosas.",
                "inteligencia_evaluada": INT_NATURALIST,
                "opciones": [
                    {
                        "texto": "Clasificar los hongos según su textura, coloración de esporas y el tipo de suelo de tierra donde crecen.",
                        "respuesta_resultado": "Identificas el espécimen curativo de forma botánica correcta y cruzas a salvo.",
                        "puntaje": {INT_NATURALIST: 2}
                    },
                    {
                        "texto": "Analizar la refracción y el espectro de luz ultravioleta que emite el hongo en la oscuridad del entorno.",
                        "respuesta_resultado": "Deduces el hongo curativo por su longitud de onda visual. Pasas seguro.",
                        "puntaje": {INT_SPATIAL: 2}
                    },
                    {
                        "texto": "Meditar frente al micelio, calmando tu propia mente para ralentizar tus latidos y respirar menos esporas.",
                        "respuesta_resultado": "Tu autocontrol corporal e intrapersonal te permite tolerar el aire denso y cruzar.",
                        "puntaje": {INT_INTRAPERSONAL: 2}
                    }
                ]
            },
            {
                "narrativa": "El fantasma de un niño caballero llora desconsoladamente sentado en una tumba de piedra. La puerta trasera está sellada por su pena espiritual.",
                "inteligencia_evaluada": INT_INTERPERSONAL,
                "opciones": [
                    {
                        "texto": "Sentarte a su lado, escuchar su triste relato con sincera empatía y ofrecerle palabras de consuelo caballeresco.",
                        "respuesta_resultado": "El niño sonríe, encontrando la paz que buscaba. Se desvanece dejando la puerta abierta.",
                        "puntaje": {INT_INTERPERSONAL: 2}
                    },
                    {
                        "texto": "Explicarle con lógica e historia antigua por qué su alma ya no pertenece a este plano material del calabozo.",
                        "respuesta_resultado": "Tu argumento racional lo convence de liberar la zona solemnemente.",
                        "puntaje": {INT_LOGICAL: 2}
                    },
                    {
                        "texto": "Escribir un mensaje de aliento con tiza en el suelo para que pueda leerlo y entender que no está solo.",
                        "respuesta_resultado": "Tus palabras escritas reconfortan al pequeño espectro y el bloqueo se disuelve.",
                        "puntaje": {INT_LINGUISTIC: 2}
                    }
                ]
            },
            {
                "narrativa": "Un pedestal sostiene un cáliz dorado brillante. Al mirarlo de cerca, un susurro en tu mente te cuestiona: '¿Por qué buscas el tesoro? ¿Es por codicia, deber o autoconocimiento?'",
                "inteligencia_evaluada": INT_INTRAPERSONAL,
                "opciones": [
                    {
                        "texto": "Examinar tus verdaderos motivos internos con honestidad y confesarle al cáliz: 'Lo busco para poner a prueba mis propios límites y miedos'.",
                        "respuesta_resultado": "El cáliz brilla y el pedestal baja. Has superado una prueba de honestidad personal.",
                        "puntaje": {INT_INTRAPERSONAL: 2}
                    },
                    {
                        "texto": "Responder formalmente usando el código de honor lingüístico del caballero medieval sobre la lealtad al reino.",
                        "respuesta_resultado": "Tu impecable oratoria satisface las condiciones del pedestal y se abre.",
                        "puntaje": {INT_LINGUISTIC: 2}
                    },
                    {
                        "texto": "Analizar la base del pedestal en busca de cables mecánicos o trampas ocultas de presión.",
                        "respuesta_resultado": "Ignoras el enigma metafísico y desactivas el pestillo físico con destreza espacial.",
                        "puntaje": {INT_SPATIAL: 2}
                    }
                ]
            },
            {
                "narrativa": "Tres palancas de hierro tienen grabados los números romanos IX, IV y VII. Una inscripción advierte: 'Solo la suma de las palancas primas activará el puente colgante'.",
                "inteligencia_evaluada": INT_LOGICAL,
                "opciones": [
                    {
                        "texto": "Activar únicamente la palanca VII, ya que es el único número primo de la serie mostrada.",
                        "respuesta_resultado": "El puente colgante desciende ruidosamente y encaja perfectamente en el foso.",
                        "puntaje": {INT_LOGICAL: 2}
                    },
                    {
                        "texto": "Examinar los grabados con los dedos para ver cuál palanca está más gastada por el uso histórico.",
                        "respuesta_resultado": "Tu agudo tacto cenestésico detecta el desgaste en la palanca VII y la activas.",
                        "puntaje": {INT_KINESTHETIC: 2}
                    },
                    {
                        "texto": "Observar la inclinación tridimensional de los cables de tensión que sostienen el puente para deducir el contrapeso.",
                        "respuesta_resultado": "Tu percepción espacial te ayuda a entender el mecanismo y cruzar.",
                        "puntaje": {INT_SPATIAL: 2}
                    }
                ]
            },
            {
                "narrativa": "Encuentras un trozo de pergamino antiguo con un poema inconcluso. Faltan palabras clave al final y hay un tintero listo sobre un atril de madera.",
                "inteligencia_evaluada": INT_LINGUISTIC,
                "opciones": [
                    {
                        "texto": "Tomar la pluma y completar los versos usando rimas y estructuras poéticas métricas perfectas en español.",
                        "respuesta_resultado": "El pergamino se ilumina y se disuelve en aire templado, abriendo el pasaje secreto.",
                        "puntaje": {INT_LINGUISTIC: 2}
                    },
                    {
                        "texto": "Analizar la estructura lógica de las oraciones para rellenar los huecos por simple sintaxis gramatical.",
                        "respuesta_resultado": "Deduces las palabras correctas por puro razonamiento sintáctico lógico.",
                        "puntaje": {INT_LOGICAL: 2}
                    },
                    {
                        "texto": "Hacer sonar las cuerdas de una pequeña lira que cuelga al lado del atril para inspirar una melodía métrica.",
                        "respuesta_resultado": "La resonancia de la lira te guía acústicamente al compás del poema y este se abre.",
                        "puntaje": {INT_MUSICAL: 2}
                    }
                ]
            },
            {
                "narrativa": "Una puerta circular tiene un relieve de piedra con piezas móviles desordenadas que forman un grabado de simetría radial. La puerta está bloqueada.",
                "inteligencia_evaluada": INT_SPATIAL,
                "opciones": [
                    {
                        "texto": "Rotar y ordenar las piezas en tu mente antes de moverlas para restaurar la perfecta simetría del dibujo.",
                        "respuesta_resultado": "El grabado encaja con un clic y la puerta rota sobre su eje central.",
                        "puntaje": {INT_SPATIAL: 2}
                    },
                    {
                        "texto": "Cerrar los ojos y meditar en la paz interior del equilibrio para sentir qué movimientos hacer de forma intuitiva.",
                        "respuesta_resultado": "Tu templanza intrapersonal te guía sin cometer errores de impulsividad.",
                        "puntaje": {INT_INTRAPERSONAL: 2}
                    },
                    {
                        "texto": "Mover las piezas con movimientos corporales veloces, experimentando combinaciones de engranajes físicamente.",
                        "respuesta_resultado": "Tu velocidad manual cenestésica resuelve el puzzle por tanteo dinámico.",
                        "puntaje": {INT_KINESTHETIC: 2}
                    }
                ]
            },
            {
                "narrativa": "Llegas a una gran bóveda de ecos. Al fondo hay un portón con una gárgola. Si haces un sonido, la cueva te devuelve un eco alterado y debes responderle al guardián.",
                "inteligencia_evaluada": INT_MUSICAL,
                "opciones": [
                    {
                        "texto": "Silbar una melodía corta y escuchar cómo el eco de la cueva completa la secuencia musical.",
                        "respuesta_resultado": "La gárgola asiente y abre el portón alabando tu oído musical.",
                        "puntaje": {INT_MUSICAL: 2}
                    },
                    {
                        "texto": "Tratar de negociar diplomáticamente con la gárgola explicándole la empatía de tu viaje.",
                        "respuesta_resultado": "Tus palabras comprensivas convencen al guardián y te deja pasar pacíficamente.",
                        "puntaje": {INT_INTERPERSONAL: 2}
                    },
                    {
                        "texto": "Analizar la acústica de la sala y calcular las distancias en base a la velocidad del sonido del eco.",
                        "respuesta_resultado": "Tu cálculo del retardo de la onda sonora te revela el patrón y pasas.",
                        "puntaje": {INT_LOGICAL: 2}
                    }
                ]
            }
        ]
        
        # Copia para no repetir salas en una partida
        self.available_fallback_rooms = list(self.fallback_rooms)

        # Base de datos de trivia offline para el enemigo
        self.offline_enemy_trivia = [
            {
                "pregunta": "Tengo ciudades pero no casas, bosques pero no árboles, ríos pero no agua. ¿Qué soy?",
                "opciones": ["Un mapa", "Un espejo", "Un desierto"],
                "correcta_idx": 0
            },
            {
                "pregunta": "El padre de Clara tiene 5 hijas: Lala, Lela, Lila, Lola y... ¿cómo se llama la quinta?",
                "opciones": ["Lula", "Clara", "Leila"],
                "correcta_idx": 1
            },
            {
                "pregunta": "Si un tren eléctrico viaja hacia el norte a 100 km/h y el viento sopla hacia el sur a 20 km/h, ¿hacia dónde va el humo?",
                "opciones": ["Hacia el sur", "Hacia ninguna parte", "Hacia el este"],
                "correcta_idx": 1
            },
            {
                "pregunta": "Dos personas juegan al ajedrez. Juegan 5 partidas completas y cada una gana 3. ¿Cómo es posible?",
                "opciones": ["Hicieron trampa", "No jugaban entre sí", "Empataron una partida"],
                "correcta_idx": 1
            },
            {
                "pregunta": "¿Qué número sigue en la secuencia lógica: 2, 6, 12, 20, 30...?",
                "opciones": ["40", "42", "45"],
                "correcta_idx": 1
            },
            {
                "pregunta": "Cuanto más le quitas, más grande se vuelve. ¿Qué es?",
                "opciones": ["Un agujero", "Una deuda", "Una sombra"],
                "correcta_idx": 0
            },
            {
                "pregunta": "¿Cuál es el metal más abundante en la corteza terrestre?",
                "opciones": ["Hierro", "Aluminio", "Cobre"],
                "correcta_idx": 1
            },
            {
                "pregunta": "Doy vueltas pero no me muevo, y albergo tesoros que no puedo ver. ¿Qué soy?",
                "opciones": ["Una cerradura", "Un remolino", "Un reloj"],
                "correcta_idx": 0
            },
            {
                "pregunta": "Si me guardas, soy algo; si me compartes, ya no soy nada. ¿Qué soy?",
                "opciones": ["Un secreto", "Una mentira", "Un pensamiento"],
                "correcta_idx": 0
            },
            {
                "pregunta": "Tengo llaves pero no abro cerraduras. Tengo espacio pero no habitaciones. Puedes entrar pero no puedes salir. ¿Qué soy?",
                "opciones": ["Un teclado", "Un libro", "Una celda"],
                "correcta_idx": 0
            },
            {
                "pregunta": "¿Qué corre pero nunca camina, tiene boca pero nunca habla, tiene un lecho pero nunca duerme?",
                "opciones": ["Un río", "La arena", "El viento"],
                "correcta_idx": 0
            },
            {
                "pregunta": "¿Qué objeto puede viajar alrededor del mundo mientras permanece en un rincón?",
                "opciones": ["Un espejo", "Una carta", "Un sello postal"],
                "correcta_idx": 2
            },
            {
                "pregunta": "Un caballero cruza un río congelado arrastrando su caballo sin mojarse. ¿Cómo lo hizo?",
                "opciones": ["Usó un puente oculto", "El río estaba congelado", "El caballo voló"],
                "correcta_idx": 1
            },
            {
                "pregunta": "Tengo un cuello pero no tengo cabeza. ¿Qué soy?",
                "opciones": ["Una botella", "Una bufanda", "Una armadura"],
                "correcta_idx": 0
            },
            {
                "pregunta": "¿Qué número, si lo multiplicas por cualquier otro, da siempre el mismo resultado?",
                "opciones": ["El uno", "El cero", "El diez"],
                "correcta_idx": 1
            },
            {
                "pregunta": "Soy ligero como una pluma, pero el hombre más fuerte no puede sostenerme por mucho tiempo. ¿Qué soy?",
                "opciones": ["Una piedra pómez", "El humo", "La respiración"],
                "correcta_idx": 2
            },
            {
                "pregunta": "¿Qué sube en la vida de un caballero pero nunca baja?",
                "opciones": ["La altura del salto", "La edad", "La fatiga"],
                "correcta_idx": 1
            },
            {
                "pregunta": "¿Qué tiene dientes de acero pero nunca puede morder?",
                "opciones": ["Un peine", "Una sierra", "Un tenedor"],
                "correcta_idx": 0
            },
            {
                "pregunta": "Si un monje nacido en España viaja a Roma, ¿dónde debe ser enterrado al morir?",
                "opciones": ["En España", "En Roma", "En ningún lado, está vivo"],
                "correcta_idx": 2
            },
            {
                "pregunta": "Tengo ramas de madera pero no tengo hojas, flores ni frutos. ¿Qué soy?",
                "opciones": ["Un candelabro", "Un ciervo (sus astas)", "Un arbusto seco"],
                "correcta_idx": 1
            },
            {
                "pregunta": "Tengo un solo ojo de metal pero no puedo ver nada. ¿Qué soy?",
                "opciones": ["Una aguja", "Una llave", "Una tormenta"],
                "correcta_idx": 0
            },
            {
                "pregunta": "¿Qué se moja y humedece mientras más secas tu cuerpo?",
                "opciones": ["La lluvia", "La arena", "Una toalla"],
                "correcta_idx": 2
            },
            {
                "pregunta": "Aparezco una vez en un minuto, dos en un momento, pero nunca en cien años. ¿Qué soy?",
                "opciones": ["Un pestañeo", "La letra M", "El viento"],
                "correcta_idx": 1
            },
            {
                "pregunta": "El herrero lo hace pero no lo necesita; el rey lo compra pero no lo usa; el difunto lo usa pero no lo sabe. ¿Qué es?",
                "opciones": ["Un ataúd", "Un escudo", "Un trono"],
                "correcta_idx": 0
            },
            {
                "pregunta": "Tengo un corazón de manzana pero no late. ¿Qué soy?",
                "opciones": ["Un árbol", "Una piedra", "Una manzana"],
                "correcta_idx": 2
            }
        ]

    def check_connection(self):
        """Intenta verificar si el servidor de Ollama está encendido pidiendo información básica."""
        req = urllib.request.Request(
            OLLAMA_URL.replace("/generate", ""),
            method="GET"
        )
        try:
            with urllib.request.urlopen(req, timeout=1.5) as _:
                self.offline_mode = False
        except Exception:
            self.offline_mode = True

    def generate_room(self, player_history):
        """Genera un desafío en tiempo real usando Ollama o la base de datos de contingencia."""
        self.check_connection()
        
        if self.offline_mode:
            # Fallback offline
            if not self.available_fallback_rooms:
                self.available_fallback_rooms = list(self.fallback_rooms)
            room = random.choice(self.available_fallback_rooms)
            self.available_fallback_rooms.remove(room)
            return room

        # Si Ollama está disponible, creamos un prompt robusto
        # Rotamos las inteligencias basándonos en el tamaño del historial para testear todas
        idx = len(player_history) % len(INTELLIGENCES)
        target_intelligence = INTELLIGENCES[idx]
        
        # Variación aleatoria para desafíos únicos y variados en cada generación
        ambient = random.choice([
            "una cripta polvorienta con antorchas mortecinas",
            "una biblioteca abandonada llena de pergaminos prohibidos",
            "una forja abandonada con carbones aún calientes",
            "un laboratorio de alquimia con frascos burbujeantes",
            "un foso de piedra húmedo con líquenes luminosos",
            "un santuario de runas antiguas talladas en las paredes",
            "una celda con rejas oxidadas y restos de armaduras",
            "una bóveda acorazada con grabados astronómicos"
        ])
        
        guardian = random.choice([
            "un espectro flotante con ojos de fuego",
            "un duendecillo prisionero que guarda un secreto",
            "un autómata de engranajes oxidado que chirría",
            "una gárgola de piedra inmóvil pero vigilante",
            "una proyección mágica flotante de un hechicero antiguo",
            "una bestia encadenada sedienta de libertad",
            "una inscripción parlante tallada en una losa gigante",
            "una voz incorpórea que resuena desde las paredes"
        ])
        
        prompt = f"""
Genera una sala de calabozo medieval de fantasía. El entorno es '{ambient}' y hay '{guardian}'. El jugador es un caballero.
Esta sala debe evaluar específicamente la inteligencia de tipo: '{target_intelligence}' según la teoría de inteligencias múltiples de Howard Gardner.
Debes devolver estrictamente un objeto JSON en español con la estructura que se indica abajo. No agregues texto explicativo fuera del JSON.

Estructura JSON requerida:
{{
  "narrativa": "Una descripción narrativa inmersiva y corta de la sala, su peligro o su acertijo (máximo 3 frases).",
  "inteligencia_evaluada": "{target_intelligence}",
  "opciones": [
    {{
      "texto": "Opción A: Una acción que demuestre o use fuertemente la inteligencia '{target_intelligence}'.",
      "respuesta_resultado": "Qué sucede después de tomar esta acción (máximo 2 frases).",
      "puntaje": {{"{target_intelligence}": 2}}
    }},
    {{
      "texto": "Opción B: Una acción alternativa basada en otra inteligencia lógica o verbal (ej. {INT_LOGICAL} o {INT_LINGUISTIC}).",
      "respuesta_resultado": "Qué sucede al tomar esta acción alternativa (máximo 2 frases).",
      "puntaje": {{"{INT_LOGICAL if target_intelligence != INT_LOGICAL else INT_LINGUISTIC}": 2}}
    }},
    {{
      "texto": "Opción C: Una acción física o de instinto (ej. {INT_KINESTHETIC} o {INT_NATURALIST}).",
      "respuesta_resultado": "Qué sucede al tomar esta acción física (máximo 2 frases).",
      "puntaje": {{"{INT_KINESTHETIC if target_intelligence != INT_KINESTHETIC else INT_NATURALIST}": 2}}
    }}
  ]
}}
"""
        try:
            payload = {
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "format": "json",
                "stream": False,
                "options": {
                    "temperature": 0.7
                }
            }
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                OLLAMA_URL, 
                data=data, 
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=4.5) as response:
                res = json.loads(response.read().decode('utf-8'))
                room_data = json.loads(res.get("response", ""))
                
                # Validación básica de campos del JSON
                if "narrativa" in room_data and "opciones" in room_data and len(room_data["opciones"]) >= 3:
                    return room_data
        except Exception:
            pass
            
        # Fallback si falla el JSON del LLM
        if not self.available_fallback_rooms:
            self.available_fallback_rooms = list(self.fallback_rooms)
        room = random.choice(self.available_fallback_rooms)
        self.available_fallback_rooms.remove(room)
        return room

    def evaluate_custom_response(self, room_narrative, target_intelligence, user_text):
        """Procesa una respuesta libre escrita por el usuario."""
        self.check_connection()
        
        if self.offline_mode:
            # Fallback local
            # Evaluamos heurísticamente en base a palabras clave básicas en español
            user_text_lower = user_text.lower()
            detected_int = INT_KINESTHETIC # Defecto físico
            
            if any(w in user_text_lower for w in ["piensa", "calculo", "logica", "numero", "analizo", "patron"]):
                detected_int = INT_LOGICAL
            elif any(w in user_text_lower for w in ["hablo", "dijo", "poema", "grito", "escribo", "palabra"]):
                detected_int = INT_LINGUISTIC
            elif any(w in user_text_lower for w in ["miro", "observo", "mapa", "perspectiva", "espacio"]):
                detected_int = INT_SPATIAL
            elif any(w in user_text_lower for w in ["canto", "tarareo", "escucho", "sonido", "nota", "campana"]):
                detected_int = INT_MUSICAL
            elif any(w in user_text_lower for w in ["planta", "musgo", "animal", "agua", "entorno", "hongo"]):
                detected_int = INT_NATURALIST
            elif any(w in user_text_lower for w in ["ayudo", "hablo", "negocio", "trato", "ofrezco", "amigo"]):
                detected_int = INT_INTERPERSONAL
            elif any(w in user_text_lower for w in ["siento", "medito", "miedo", "calma", "conozco"]):
                detected_int = INT_INTRAPERSONAL

            return {
                "respuesta_resultado": f"Reaccionas escribiendo: '{user_text}'. Adaptas tu instinto en la sala, lo cual resuena con tu inteligencia de tipo {detected_int}.",
                "puntaje": {detected_int: 2}
            }

        # Con Ollama activo, le pedimos analizar la respuesta y clasificarla
        prompt = f"""
El caballero está en una sala con el siguiente desafío: '{room_narrative}'
El usuario escribió esta respuesta libre: '{user_text}'
Clasifica cuál de las 8 Inteligencias Múltiples de Howard Gardner describe mejor su respuesta.
Devuelve un JSON estricto con el resultado y una consecuencia narrativa.

Estructura JSON requerida:
{{
  "respuesta_resultado": "Qué sucede después de tomar esta acción libre escrita por el jugador (máximo 2 frases).",
  "inteligencia_detectada": "Una de las 8 inteligencias múltiples (ej. {INT_LOGICAL}, {INT_LINGUISTIC}, etc.)",
  "puntaje": {{"Nombre_Inteligencia_Detectada": 2}}
}}
"""
        try:
            payload = {
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "format": "json",
                "stream": False,
                "options": {
                    "temperature": 0.4
                }
            }
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                OLLAMA_URL, 
                data=data, 
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=4.0) as response:
                res = json.loads(response.read().decode('utf-8'))
                res_data = json.loads(res.get("response", ""))
                
                # Limpiar y normalizar puntajes
                detected = res_data.get("inteligencia_detectada", target_intelligence)
                if detected not in INTELLIGENCES:
                    detected = target_intelligence
                
                return {
                    "respuesta_resultado": res_data.get("respuesta_resultado", "Cruzas la sala con éxito aplicando tu ingenio."),
                    "puntaje": {detected: 2}
                }
        except Exception:
            pass

        # Fallback local de último recurso
        return {
            "respuesta_resultado": f"Decides actuar de forma personalizada. Tu resolución se adapta a la sala desafiante.",
            "puntaje": {target_intelligence: 2}
        }

    def generate_enemy_quiz(self):
        """Genera 3 preguntas de trivia de las sombras usando Ollama o fallback local."""
        self.check_connection()
        
        if self.offline_mode:
            return random.sample(self.offline_enemy_trivia, 3)
            
        prompt = """
Genera exactamente 3 preguntas de acertijos o trivia de lógica, ciencia o mitología medieval en español para un encuentro con un espectro de sombras en un calabozo.
Cada pregunta debe tener exactamente 3 opciones de respuesta y un campo que indique el índice correcto (0, 1 o 2).
Debes devolver estrictamente un objeto JSON en español con la estructura que se indica abajo. No agregues texto explicativo fuera del JSON.

Estructura JSON requerida:
{
  "cuestionario": [
    {
      "pregunta": "El acertijo o pregunta corta (máximo 1 frase).",
      "opciones": ["Opción A", "Opción B", "Opción C"],
      "correcta_idx": 0
    },
    {
      "pregunta": "Otro acertijo de lógica o matemática (máximo 1 frase).",
      "opciones": ["Opción A", "Opción B", "Opción C"],
      "correcta_idx": 1
    },
    {
      "pregunta": "Otro acertijo conceptual o mitológico (máximo 1 frase).",
      "opciones": ["Opción A", "Opción B", "Opción C"],
      "correcta_idx": 2
    }
  ]
}
"""
        try:
            payload = {
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "format": "json",
                "stream": False,
                "options": {
                    "temperature": 0.6
                }
            }
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                OLLAMA_URL, 
                data=data, 
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=5.0) as response:
                res = json.loads(response.read().decode('utf-8'))
                quiz_data = json.loads(res.get("response", ""))
                if "cuestionario" in quiz_data and len(quiz_data["cuestionario"]) == 3:
                    return quiz_data["cuestionario"]
        except Exception:
            pass
            
        # Fallback local
        return random.sample(self.offline_enemy_trivia, 3)

    def generate_personality_report(self, scores):
        """Genera un reporte de personalidad basado en los puntajes y MBTI usando Ollama o Fallback local."""
        self.check_connection()
        
        # Calcular el tipo MBTI aproximado mediante los puntajes para guiar la clasificación
        score_logical = scores.get(INT_LOGICAL, 0)
        score_linguistic = scores.get(INT_LINGUISTIC, 0)
        score_spatial = scores.get(INT_SPATIAL, 0)
        score_musical = scores.get(INT_MUSICAL, 0)
        score_kinesthetic = scores.get(INT_KINESTHETIC, 0)
        score_naturalist = scores.get(INT_NATURALIST, 0)
        score_inter = scores.get(INT_INTERPERSONAL, 0)
        score_intra = scores.get(INT_INTRAPERSONAL, 0)
        
        # Determinación de MBTI local heurística:
        ie = "I" if score_intra >= score_inter else "E"
        ns = "N" if (score_linguistic + score_musical + score_spatial) >= (score_kinesthetic + score_naturalist) else "S"
        ft = "F" if (score_inter + score_intra) >= (score_logical + score_spatial) else "T"
        jp = "J" if score_logical >= score_spatial else "P"
        
        mbti_local = ie + ns + ft + jp
        
        mbti_titles = {
            "INTJ": "El Arquitecto", "INTP": "El Lógico", "ENTJ": "El Comandante", "ENTP": "El Innovador",
            "INFJ": "El Abogado", "INFP": "El Mediador", "ENFJ": "El Protagonista", "ENFP": "El Activista",
            "ISTJ": "El Logista", "ISFJ": "El Defensor", "ESTJ": "El Ejecutivo", "ESFJ": "El Cónsul",
            "ISTP": "El Virtuoso", "ISFP": "El Aventurero", "ESTP": "El Emprendedor", "ESFP": "El Animador"
        }
        title_local = mbti_titles.get(mbti_local, "El Viajero del Calabozo")
        
        if self.offline_mode:
            # Fallback offline
            resumen_local = f"Eres un aventurero del tipo **{mbti_local} ({title_local})**.\n\n"
            resumen_local += "Tu paso por esta mazmorra revela cómo utilizas tus talentos. "
            
            # Resaltar la inteligencia principal
            max_int = max(scores, key=scores.get)
            resumen_local += f"Tu mayor fuerte es tu inteligencia **{max_int}** (puntaje: {scores[max_int]}). "
            
            if max_int == INT_LOGICAL:
                resumen_local += "Abordas los problemas descomponiéndolos en variables analíticas y deduciendo patrones abstractos con frialdad y rigor."
            elif max_int == INT_LINGUISTIC:
                resumen_local += "Utilizas el poder del lenguaje, la diplomacia y la retórica para abrirte paso y convencer a los guardianes sin violencia."
            elif max_int == INT_SPATIAL:
                resumen_local += "Posees una gran orientación espacial y percepción tridimensional, lo cual te permite navegar laberintos y alinear perspectivas ocultas."
            elif max_int == INT_MUSICAL:
                resumen_local += "Sintonizas con el entorno a través de patrones acústicos, ritmos y armonías, detectando vibraciones ocultas."
            elif max_int == INT_KINESTHETIC:
                resumen_local += "Confías en tu instinto motor, agilidad y fuerza de placas metálicas para reaccionar a peligros veloces."
            elif max_int == INT_NATURALIST:
                resumen_local += "Entiendes la naturaleza del calabozo: plantas espinosas, bestias y elementos naturales que doblas a tu favor."
            elif max_int == INT_INTERPERSONAL:
                resumen_local += "Eres altamente empático. Buscas la cooperación, la negociación y el bienestar mutuo con las criaturas que encuentras."
            elif max_int == INT_INTRAPERSONAL:
                resumen_local += "Destacas en la reflexión interna, autocontrol y aceptación emocional de tus dudas, dándote una templanza inquebrantable."

            resumen_local += "\n\nTu perfil MBTI denota un balance donde combinas esta inteligencia con tus capacidades cognitivas para forjar un carácter único en el calabozo."
            
            return {
                "mbti": mbti_local,
                "titulo": title_local,
                "resumen": resumen_local
            }

        # Con Ollama activo, le pedimos redactar el análisis de personalidad completo
        scores_str = ", ".join([f"{k}: {v} pts" for k, v in scores.items()])
        prompt = f"""
Un jugador completó un calabozo interactivo donde se evaluaron sus Inteligencias Múltiples de Howard Gardner.
Puntajes obtenidos en el laberinto: {scores_str}
Calcula qué tipo de personalidad MBTI de las 16 descritas en 16Personalities (ej. INFP, INTJ, ESTP, etc.) encaja mejor con este perfil de inteligencias.
Devuelve estrictamente un objeto JSON en español con la estructura que se indica abajo.

Estructura JSON requerida:
{{
  "mbti": "Las 4 letras del tipo MBTI sugerido (ej. INFP)",
  "titulo": "El título en español del tipo de personalidad (ej. El Mediador)",
  "resumen": "Un análisis completo y profundo de personalidad (3 párrafos cortos) que explique cómo su perfil de inteligencias múltiples se conecta con su tipo MBTI y su estilo para afrontar retos."
}}
"""
        try:
            payload = {
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "format": "json",
                "stream": False,
                "options": {
                    "temperature": 0.5
                }
            }
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                OLLAMA_URL, 
                data=data, 
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=8.0) as response:
                res = json.loads(response.read().decode('utf-8'))
                report_data = json.loads(res.get("response", ""))
                if "mbti" in report_data and "titulo" in report_data and "resumen" in report_data:
                    return report_data
        except Exception:
            pass

        # Fallback local final si falla Ollama
        return {
            "mbti": mbti_local,
            "titulo": title_local,
            "resumen": f"Eres del tipo {mbti_local} ({title_local}). Tu templanza y tu inteligencia máxima te han permitido cruzar el calabozo de inteligencias múltiples con honores."
        }
