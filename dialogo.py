import json
import urllib.request
import urllib.error

OLLAMA_URL = "http://localhost:11434/api/chat"

GARDEL = "gardel-carlos"
MERCEDES = "mercedes-sosa"
RONDAS = 5

TEMA = (
    "El tango, la música argentina y las diferencias generacionales: "
    "cómo cambian los estilos, qué une a las generaciones y qué lugar "
    "ocupa la música popular en la identidad argentina."
)

PERSONAJES = {
    GARDEL: (
        "Sos una recreación conversacional respetuosa de Carlos Gardel. "
        "Hablás en español rioplatense, usás voseo y un tono porteño "
        "elegante, cálido, pícaro y nostálgico. Conocés el tango y su "
        "historia. No inventes recuerdos ni afirmes haber vivido hechos "
        "posteriores a 1935. Respondé en 2 a 4 oraciones."
    ),
    MERCEDES: (
        "Sos una recreación conversacional respetuosa de Mercedes Sosa, "
        "inspirada en su trayectoria artística y su vínculo con el folclore "
        "y la música popular argentina y latinoamericana. Hablás en español "
        "natural, cálido y reflexivo. Respetás la diversidad musical y "
        "generacional. No inventes recuerdos privados ni citas reales. "
        "No imites de forma caricaturesca su voz. Respondé en 2 a 4 oraciones."
    ),
}


def consultar_ollama(modelo, historial):
    mensajes = [
        {"role": "system", "content": PERSONAJES[modelo]},
        *historial,
    ]

    datos = json.dumps({
        "model": modelo,
        "messages": mensajes,
        "stream": False,
        "options": {"temperature": 0.7}
    }).encode("utf-8")

    solicitud = urllib.request.Request(
        OLLAMA_URL,
        data=datos,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(solicitud, timeout=300) as respuesta:
        resultado = json.loads(respuesta.read().decode("utf-8"))

    return resultado["message"]["content"].strip()


def main():
    historial = [
        {
            "role": "user",
            "content": (
                f"Tema del diálogo: {TEMA}\n"
                "Iniciá una conversación con Mercedes Sosa. "
                "Saludala con respeto y planteá una reflexión sobre "
                "el tango y la música argentina."
            ),
        }
    ]

    print("\n🎙️ DIÁLOGO: CARLOS GARDEL Y MERCEDES SOSA")
    print(f"Tema: {TEMA}\n")
    print("=" * 65)

    try:
        for ronda in range(1, RONDAS + 1):
            print(f"\n🔹 RONDA {ronda}/{RONDAS}\n")

            # Gardel habla primero en cada ronda.
            respuesta_gardel = consultar_ollama(GARDEL, historial)
            print(f"🎩 CARLOS GARDEL:\n{respuesta_gardel}\n")

            historial.append({
                "role": "assistant",
                "content": respuesta_gardel,
            })

            # Mercedes responde a lo que dijo Gardel.
            historial.append({
                "role": "user",
                "content": (
                    "Mercedes, respondé a las ideas de Gardel. "
                    "Aportá tu propia perspectiva y mantené el tema "
                    "de la conversación. No repitas simplemente lo "
                    "que él dijo."
                ),
            })

            respuesta_mercedes = consultar_ollama(MERCEDES, historial)
            print(f"🎶 MERCEDES SOSA:\n{respuesta_mercedes}\n")

            historial.append({
                "role": "assistant",
                "content": respuesta_mercedes,
            })

            # El siguiente turno vuelve a Gardel.
            historial.append({
                "role": "user",
                "content": (
                    "Gardel, respondé a lo que acaba de plantear Mercedes. "
                    "Continuá el intercambio con naturalidad, sin repetir "
                    "tus ideas anteriores."
                ),
            })

        print("=" * 65)
        print("\n✅ Diálogo terminado: 5 rondas, 10 intervenciones.")

        # Guardar una copia de la conversación.
        with open("dialogo_gardel_mercedes.txt", "w", encoding="utf-8") as f:
            f.write(f"DIÁLOGO: GARDEL Y MERCEDES SOSA\nTema: {TEMA}\n\n")
            for mensaje in historial:
                if mensaje["role"] == "assistant":
                    f.write(mensaje["content"] + "\n\n")

        print("📄 Conversación guardada en dialogo_gardel_mercedes.txt")

    except urllib.error.URLError as error:
        print("\n❌ No se pudo conectar con Ollama.")
        print("Verificá que el servidor esté funcionando en el puerto 11434.")
        print(f"Detalle: {error}")
    except (KeyError, json.JSONDecodeError) as error:
        print(f"\n❌ No se pudo interpretar la respuesta de Ollama: {error}")
    except TimeoutError:
        print("\n❌ Ollama tardó demasiado en responder. Probá nuevamente.")


if __name__ == "__main__":
    main()
