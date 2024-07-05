import pandas as pd
from treelib import Tree
from django.contrib.staticfiles import finders

from documents.models import Chunk
from documents.retrieval_methods.knn_retrieval import retrieve
from documents.retrieval_models.routing import EmbeddingModel
from qa.generative_models.routing import GET_RESPONSE

def is_starting_rule(message):
    return message.startswith("Extract") or message.startswith("Concat") or message.startswith("Instantiate") or message.startswith("Compose") or message.startswith("Refine") or message.startswith("NoInfo")

def is_ending_final_answer(message):
    return message.endswith("Es respuesta final") or message.endswith("No es respuesta final")

def create_answer(message, model, temperature=0):
    system_prompt, messages, references = derivation_prompt(message)
    res = GET_RESPONSE[model](system_prompt, messages, model, temp=temperature)

    steps_text = [e for e in res.split("\n\n") if not e.startswith("Nueva hipótesis:")]
    steps_text_fixed = []

    for i in range(len(steps_text)):
        if len(steps_text_fixed) > 0 and is_ending_final_answer(steps_text_fixed[-1]) and not is_starting_rule(steps_text[i]):
            continue
        if is_starting_rule(steps_text[i]):
            steps_text_fixed.append(steps_text[i])
        elif len(steps_text_fixed) > 0:
            steps_text_fixed[-1] += "\n\n" + steps_text[i]
    steps_text = steps_text_fixed

    steps = []

    for step_text in steps_text:
        parts = step_text.split("|")
        if len(parts) >= 3:
            steps.append({"rule": parts[0].strip(), "hipotesis": parts[1].strip(), "conclusion": parts[2].strip()})
        else:
            steps.append({"rule": None, "hipotesis": None, "conclusion": "|".join(parts).strip()})

    if len(steps) == 0:
        return res, [{"rule": "NoInfo", "hipotesis": "-1", "conclusion": res}]
    return steps[-1]["conclusion"], references, get_tree(steps, references)

def derivation_prompt(message):
    # Load Few-Shot examples
    df = pd.read_csv(finders.find("ejemplosv2.csv"))

    examples = []

    for index, row in df.iterrows():
        example = row['derivación']
        examples.append(example)
    
    system = """### Descripción de la tarea:
El objetivo es llegar a la respuesta de una pregunta, partiendo de un conjunto de extractos que son información correcta (que llamaremos hipótesis). Para ello, se debe aplicar reglas sobre las hipótesis que permiten transformarlas y/o combinarlas para generar una conclusión, que a su vez podría usarse como hipótesis, hasta llegar finalmente a la respuesta esperada.

### Reglas:
1. Extract:
Descripción: Dada una hipótesis compleja, esta regla genera una conclusión que es una parte específica de la hipótesis.
Datos relevantes: - Solo puede tomar una (1) hipótesis. Si se quiere aplicar a muchas hipótesis, se debe aplicar en varios pasos de forma secuencial. - Solo puede generar una conclusión. Si se quiere generar múltiples conclusiones se debe aplicar en varios pasos de forma secuencial.
Ejemplo: Si la hipótesis es "Hoy jugué al fútbol con unos amigos en la playa y estuvo muy divertido", la regla Extract podría generar la conclusión "Hoy jugué al fútbol".

2. Concat:
Descripción: Combina dos hipótesis independientes para generar una nueva conclusión.
Datos relevantes: Debe tomar dos (2) o más hipótesis. - Solo puede generar una conclusión. Si se quiere generar múltiples conclusiones se debe aplicar en varios pasos de forma secuencial.
Ejemplo: Si tenemos las hipótesis "La deforestación afecta la biodiversidad" y "El cambio climático es un problema global", la regla Concat podría generar la conclusión "La deforestación afecta la biodiversidad. Además, el cambio climático es un problema global".

3. Instantiate:
Descripción: Genera una conclusión al instanciar una hipótesis genérica en un caso particular.
Datos relevantes: Solo puede tomar una (1) hipótesis. Si se quiere aplicar a muchas hipótesis, se debe aplicar en varios pasos de forma secuencial. - Solo puede generar una conclusión. Si se quiere generar múltiples conclusiones se debe aplicar en varios pasos de forma secuencial.
Ejemplo: Si la hipótesis genérica es "Los árboles son beneficiosos para el medio ambiente", Instantiate podría generar la conclusión "Los pinos son beneficiosos para el medio ambiente".

4. Compose:
Descripción: Combina dos hipótesis que comparten un elemento en común para generar una nueva conclusión.
Datos relevantes: Solo puede tomar dos (2) hipótesis. Si se quiere aplicar a más de dos hipótesis, se debe aplicar en varios pasos de forma secuencial. - Solo puede generar una conclusión. Si se quiere generar múltiples conclusiones se debe aplicar en varios pasos de forma secuencial.
Ejemplo: Si tenemos las hipótesis "La deforestación afecta la biodiversidad" y "La biodiversidad es esencial para la salud del planeta", la regla Compose podría generar la conclusión "La deforestación afecta la salud del planeta".

5. Refine:
Descripción: Adapta ligeramente la respuesta para que se ajuste mejor a la pregunta, sin modificar la semántica ni el contenido de la hipótesis.
Datos relevantes: Solo puede tomar una (1) hipótesis. Si se quiere aplicar a muchas hipótesis, se debe aplicar en varios pasos de forma secuencial. - Solo puede generar una conclusión. Si se quiere generar múltiples conclusiones se debe aplicar en varios pasos de forma secuencial.
Ejemplo: Si la respuesta es "Las abejas desempeñan un papel crucial en la polinización", la regla Refine podría adaptarla a "Las abejas desempeñan un papel crucial en la polinización de las flores".

6. NoInfo:
Descripción: Se utiliza esta regla cuando ninguna de las hipótesis brinda información para responder la pregunta (o parte de la pregunta).
Datos relevantes: No toma hipótesis. - Solo puede generar una conclusión. Si se quiere generar múltiples conclusiones se debe aplicar en varios pasos de forma secuencial.
Ejemplo: Si tenemos las hipótesis "La deforestación afecta la biodiversidad" y "La biodiversidad es esencial para la salud del planeta", pero la pregunta es "¿Qué es la biodiversidad?", no se cuenta con información en las hipótesis para responder a la pregunta por lo que se debe aplicar la regla NoInfo.
Importante: Como no lleva hipótesis, agregar como hipótesis: -1."""

    examples_msgs = []
    chunks = Chunk.objects.all()
    for i in range(len(df)):
        example_text = "Hipótesis:"
        j = 1
        for reference in df["extractos"].iloc[i].split():
            example_text += f"\n\n{j}. {chunks[int(reference)].chunk}"
            j += 1
        example_text += f"\n\nPregunta de usuario:\n\n{df['pregunta'].iloc[i]}"
        examples_msgs.append({"role":"user", "content":example_text})
        examples_msgs.append({"role":"assistant", "content":examples[i]})

    references = retrieve(EmbeddingModel.OPENAI_3_SMALL.value, message)

    # Create hypothesis string
    hipotesis = ""
    for i in range(len(references)):
        hipotesis += f"{str(i+1)}. {references[i].chunk.strip()}\n\n"

    user_msg = f'''Hipótesis:

{hipotesis.strip()}

Pregunta de usuario:

{message}'''

    messages = examples_msgs + [
        {"role": "user", "content":user_msg}
    ]

    return system, messages, references

# FUNCTIONS TO PARSE THE DERIVATION STEPS
def to_json(tree):
    """Returns the tree in json format with this structure:
    {
        "text": <node text>,
        "rule": <rule>,
        "children": [
            <child1>,
            <child2>,
            ...
        ]
    }
    """
    def get_children(tree, nid):
        children = tree.children(nid)
        if not children:
            return None
        return [{"text": child.tag, "rule": child.data, "children": get_children(tree, child.identifier)} for child in children]

    root = tree.root
    return {
        "text": tree[root].tag,
        "rule": tree[root].data,
        "children": get_children(tree, root)
    }

def get_hips(hip_str):
    if hip_str.strip() == "" or hip_str.strip() == "-":
        return []
    elems = hip_str.split(",")
    elems = [elem for elem in elems if elem != "NoInfo"]
    try:
        return [int(elem.strip()) if ord(elem.strip()[-1]) < ord("a") else ord(elem.strip())-ord("a")+4 for elem in elems]
    except Exception as e:
        raise Exception(f"Error al parsear hipótesis: {hip_str}") from e

def reference_to_html(reference: Chunk):
    return f"<a href='{reference.document.url}' target='_blank'>{reference.document.title}</a>"

def get_tree(steps, refs):
    def createTree(steps, hip_list):
        if "-1" not in steps[-1]["hipotesis"]:
            for hip in get_hips(steps[-1]["hipotesis"]):
                if hip <= len(hip_list):
                    tree.create_node(
                        reference_to_html(hip_list[hip-1]),
                        "Extracto " + str(len(steps)) + str(hip),
                        parent = len(steps) + len(hip_list)
                    )
                else:
                    id = hip - len(hip_list)
                    tree.create_node(
                        steps[id-1]["conclusion"],
                        hip,
                        parent = len(steps) + len(hip_list),
                        data = f"[{steps[id-1]['rule']}]"
                    )
                    createTree(steps[:id], hip_list)
    
    tree = Tree()
    tree.create_node(
        steps[-1]["conclusion"],
        len(steps) + len(refs),
        data = f"[{steps[-1]['rule']}]")
    createTree(steps, refs)
    
    return to_json(tree)