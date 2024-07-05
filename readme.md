### Cargar documentos

Para cargar documentos, es necesario generar primero los chunks y guardarlos en un archivo CSV con las columnas 'chunk', 'source' y 'title', donde 'chunk' es el texto del chunk, 'source' es la URL original del documento y 'title' es el título del documento.

Para cargar los documentos, se debe ejecutar lo siguiente en la terminal:

```bash
> python manage.py shell
> from documents.models import Document, Embedding
> chunks = Document.load_chunks_documents('path/to/csv')
> Embedding.create_embeddings("text-embedding-3-small", chunks)
> exit()
```

### Agregar modelo generativo

Para agregar un modelo generativo (LLM), se deben seguir los siguientes pasos:

1. Si el proveedor es nuevo, crear un archivo en la carpeta `qa/generative_models/` con la implementación de la función con el siguiente cabezal: `get_response(system_prompt, messages, model_id, temp=0.0, max_tok=1000)`.

2. En routing.py:

    1. Importar la función creada en el paso anterior siguiendo la convención de los anteriores (si es un nuevo proveedor).
    2. Agregar los identificadores de los modelos nuevos en el Enum `GenerativeModel`.
    3. Para cada uno de ellos, agregar en el diccionario `GET_RESPONSE` la referencia a la función creada en el paso anterior.

Por ejemplo, si se crea el archivo `qa/generative_models/new_provider.py` con la función `get_response`, se debe agregar en `routing.py`:

```python
...
from qa.generative_models.new_provider import get_response as get_response_new_provider

class GenerativeModel(Enum):
    ...
    NEW_MODEL_1 = "new_model_1"
    NEW_MODEL_2 = "new_model_2"
    ...

GET_RESPONSE = {
    ...
    GenerativeModel.NEW_MODEL_1: get_response_new_provider,
    GenerativeModel.NEW_MODEL_2: get_response_new_provider,
    ...
}
```

**Observación:** Es necesario actualizar el frontend para que permita seleccionar los nuevos modelos generativos.