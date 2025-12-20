# Plan de Optimización: Lazy Loading + Caching + Nuevas Funcionalidades

## Configuración (Variables ajustables)

```python
# config/settings.py
ITEMS_PER_PAGE = 5  # X = cantidad de items por página en lazy load
HISTORY_RECORDS_PER_ITEM = 10  # Y = cantidad de registros de historial por item
```

---

## Fase 1: Preparación de Base de Datos

### 1.1 Crear tabla de historial
```python
# database/models.py
class ItemHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    item_id: int = Field(foreign_key="item.id")
    quantity: float
    changed_at: datetime = Field(default_factory=datetime.utcnow)

    item: Item = Relationship(back_populates="history")

# Actualizar modelo Item
class Item(SQLModel, table=True):
    # ... campos existentes ...
    history: list["ItemHistory"] = Relationship(back_populates="item")
```

### 1.2 Modificar lógica de actualización de items
- En `routes/process.py`, cada vez que se modifique `item.quantity`:
  ```python
  # Guardar en historial
  history_entry = ItemHistory(item_id=item.id, quantity=new_quantity)
  session.add(history_entry)
  ```

---

## Fase 2: API Endpoints para Lazy Loading

### 2.1 Endpoint: Cargar contexto completo (Tab "Procesar")
```python
# routes/inventory.py
@router.get("/api/context", response_class=HTMLResponse)
async def get_context(session: Session = Depends(get_session)):
    """
    Retorna <script> con contexto completo para el LLM
    Se carga asíncronamente al entrar a la app
    """
    sections = session.exec(select(Section)).all()
    items = session.exec(select(Item)).all()

    context_data = {
        "sections": [{"id": s.id, "name": s.name, "emoji": s.emoji} for s in sections],
        "items": [{"id": i.id, "name": i.name, "section_id": i.section_id} for i in items]
    }

    return f"""
    <script>
        window.inventoryContext = {json.dumps(context_data)};
        window.contextLoaded = true;
    </script>
    """
```

### 2.2 Endpoint: Lazy load items (Tab "Ver")
```python
@router.get("/api/items")
async def get_items_paginated(
    offset: int = 0,
    limit: int = ITEMS_PER_PAGE,
    section_id: int | None = None,
    session: Session = Depends(get_session),
):
    """
    Retorna items paginados para infinite scroll
    """
    stmt = select(Item).order_by(Item.updated_at.desc())
    if section_id:
        stmt = stmt.where(Item.section_id == section_id)

    stmt = stmt.offset(offset).limit(limit)
    items = session.exec(stmt).all()

    # Preparar data para template
    items_data = [...]  # Similar a app_inventory_view actual

    return templates.TemplateResponse(
        "components/items_list.html",
        {"request": request, "items": items_data, "offset": offset + limit}
    )
```

### 2.3 Endpoint: Cargar historial de item
```python
@router.get("/api/item/{item_id}/history")
async def get_item_history(
    item_id: int,
    limit: int = HISTORY_RECORDS_PER_ITEM,
    session: Session = Depends(get_session),
):
    """
    Retorna historial de un item con before/after calculado
    """
    history = session.exec(
        select(ItemHistory)
        .where(ItemHistory.item_id == item_id)
        .order_by(ItemHistory.changed_at.desc())
        .limit(limit)
    ).all()

    # Calcular before/after
    history_data = []
    for i, record in enumerate(history):
        before = history[i+1].quantity if i+1 < len(history) else 0
        after = record.quantity
        history_data.append({
            "before": before,
            "after": after,
            "changed_at": record.changed_at,
            "date_human": humanize_time(record.changed_at)
        })

    return templates.TemplateResponse(
        "components/item_history.html",
        {"request": request, "history": history_data}
    )
```

---

## Fase 3: Frontend - Tab "Procesar" con Contexto Asíncrono

### 3.1 Modificar `templates/components/process_view.html`
```html
<!-- Cargar contexto asíncronamente al renderizar el tab -->
<div hx-get="/api/context"
     hx-trigger="load"
     hx-swap="beforeend">
</div>

<form hx-post="/process/text" ...>
    <textarea name="text" ...></textarea>

    <!-- Campo hidden para incluir contexto -->
    <input type="hidden" name="context" id="context-input">

    <button type="submit" id="process-btn">
        🎤 Procesar Texto
    </button>
</form>

<script>
    // Esperar a que el contexto esté cargado antes de enviar
    document.querySelector('form').addEventListener('submit', function(e) {
        if (!window.contextLoaded) {
            e.preventDefault();
            alert('Cargando contexto, espera un momento...');
            return;
        }
        // Inyectar contexto en campo hidden
        document.getElementById('context-input').value = JSON.stringify(window.inventoryContext);
    });
</script>
```

### 3.2 Modificar `routes/process.py` para usar contexto
```python
@router.post("/process/text")
async def process_text(
    request: Request,
    text: str = Form(...),
    context: str = Form(...),  # Recibir contexto del cliente
    session: Session = Depends(get_session),
    user: User = Depends(verify_credentials),
):
    # Parsear contexto
    inventory_context = json.loads(context)

    # Incluir contexto en el prompt al LLM
    llm_input = f"""
    Contexto actual del inventario:
    Secciones disponibles: {inventory_context['sections']}
    Items existentes: {inventory_context['items']}

    Usuario dice: {text}

    {SYSTEM_PROMPT}
    """

    # ... resto de la lógica
```

---

## Fase 4: Frontend - Tab "Ver" con Lazy Loading

### 4.1 Crear componente de spinner reutilizable
```html
<!-- templates/components/loading_spinner.html -->
<div class="flex justify-center items-center p-8">
    <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
</div>
```

### 4.2 Crear skeleton de tarjeta item
```html
<!-- templates/components/item_skeleton.html -->
<div class="bg-gray-200 rounded-lg p-4 animate-pulse">
    <div class="h-4 bg-gray-300 rounded w-3/4 mb-2"></div>
    <div class="h-4 bg-gray-300 rounded w-1/2"></div>
</div>
```

### 4.3 Modificar `templates/components/inventory_view.html`
```html
<div class="max-w-2xl mx-auto">
    <h2 class="text-xl font-semibold mb-4 text-blue-600">Tu Inventario</h2>

    <!-- Filtros de sección -->
    {% include 'components/section_filters.html' %}

    <!-- Lista de items con lazy loading -->
    <div id="items-container">
        <!-- Carga inicial con HTMX -->
        <div hx-get="/api/items?offset=0&limit=5"
             hx-trigger="load"
             hx-swap="outerHTML">
            {% include 'components/loading_spinner.html' %}
        </div>
    </div>
</div>
```

### 4.4 Crear `templates/components/items_list.html`
```html
<!-- Renderiza los items paginados -->
{% for item in items %}
    {% include 'components/item_row.html' %}
{% endfor %}

<!-- Trigger para infinite scroll -->
{% if items|length >= 5 %}
<div hx-get="/api/items?offset={{ offset }}&limit=5"
     hx-trigger="intersect once"
     hx-swap="outerHTML">
    {% include 'components/item_skeleton.html' %}
    {% include 'components/item_skeleton.html' %}
</div>
{% endif %}
```

### 4.5 Modificar `templates/components/item_row.html` para historial
```html
<div class="bg-white rounded-lg p-4 mb-3 shadow-sm border border-gray-200">
    <!-- Contenido actual del item ... -->

    <!-- Botón para expandir historial -->
    <button
        hx-get="/api/item/{{ item.id }}/history"
        hx-target="#history-{{ item.id }}"
        hx-swap="innerHTML"
        class="text-sm text-blue-600 mt-2">
        Ver historial
    </button>

    <!-- Contenedor del historial (se carga al hacer click) -->
    <div id="history-{{ item.id }}" class="mt-2"></div>
</div>
```

### 4.6 Crear `templates/components/item_history.html`
```html
<!-- Historial de cambios de un item -->
<div class="bg-gray-50 rounded p-3 mt-2">
    <h4 class="font-semibold mb-2">Historial de cambios</h4>
    <div class="space-y-2">
        {% for record in history %}
        <div class="text-sm">
            <span class="text-gray-600">{{ record.date_human }}</span>:
            <span class="font-medium">{{ record.before }} → {{ record.after }}</span>
        </div>
        {% endfor %}
    </div>
</div>
```

---

## Fase 5: Nuevas Funcionalidades del LLM

### 5.1 Actualizar SYSTEM_PROMPT en `routes/process.py`
Agregar nuevas acciones al prompt:

```python
SYSTEM_PROMPT = """
...acciones existentes...

5. "move_item": Mover item a otra sección
   Ejemplo: {
     "action": "move_item",
     "item": "tomates",
     "to_section": "Refrigerador"
   }

6. "change_emoji": Cambiar emoji de item o sección
   Ejemplo item: {
     "action": "change_emoji",
     "target_type": "item",
     "target_name": "tomates",
     "emoji": "🍅"
   }
   Ejemplo sección: {
     "action": "change_emoji",
     "target_type": "section",
     "target_name": "Almacén 1",
     "emoji": "🏪"
   }

7. "delete_item": Eliminar item (requiere confirmación)
   Ejemplo: {
     "action": "delete_item",
     "item": "tomates",
     "requires_confirmation": true
   }

8. "delete_section": Eliminar sección (requiere confirmación)
   Ejemplo: {
     "action": "delete_section",
     "section": "Almacén 2",
     "requires_confirmation": true
   }
"""
```

### 5.2 Implementar handlers para nuevas acciones
```python
# En routes/process.py, dentro de process_text()

elif action == "move_item":
    item = find_item_by_name(session, cmd["item"])
    section = find_section_by_name(session, cmd["to_section"])
    if item and section:
        old_section = item.section.name
        item.section_id = section.id
        item.updated_at = datetime.utcnow()
        changes.append(f"Movido: {item.emoji} {item.name} de {old_section} a {section.name}")
    else:
        warnings.append(f"No se pudo mover '{cmd['item']}' a '{cmd['to_section']}'")

elif action == "change_emoji":
    if cmd["target_type"] == "item":
        item = find_item_by_name(session, cmd["target_name"])
        if item:
            old_emoji = item.emoji
            item.emoji = cmd["emoji"]
            item.updated_at = datetime.utcnow()
            changes.append(f"Emoji cambiado: {cmd['target_name']} {old_emoji} → {cmd['emoji']}")
    elif cmd["target_type"] == "section":
        section = find_section_by_name(session, cmd["target_name"])
        if section:
            old_emoji = section.emoji
            section.emoji = cmd["emoji"]
            changes.append(f"Emoji de sección cambiado: {cmd['target_name']} {old_emoji} → {cmd['emoji']}")

elif action == "delete_item":
    if cmd.get("requires_confirmation"):
        # Devolver HTML con botón de confirmación
        item = find_item_by_name(session, cmd["item"])
        return templates.TemplateResponse(
            "components/delete_confirmation.html",
            {
                "request": request,
                "item_id": item.id,
                "item_name": item.name,
                "type": "item"
            }
        )
    # Si ya fue confirmado (viene de un segundo request):
    # else: eliminar item

elif action == "delete_section":
    section = find_section_by_name(session, cmd["section"])
    if section:
        # Verificar si tiene items
        items_in_section = session.exec(
            select(Item).where(Item.section_id == section.id)
        ).all()
        if items_in_section:
            item_names = ", ".join([i.name for i in items_in_section])
            warnings.append(
                f"No puedes eliminar '{section.name}'. "
                f"Primero mueve estos alimentos: {item_names}"
            )
        elif cmd.get("requires_confirmation"):
            # Mostrar confirmación
            return templates.TemplateResponse(...)
```

### 5.3 Crear template de confirmación
```html
<!-- templates/components/delete_confirmation.html -->
<div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
    <p class="text-yellow-800 mb-3">
        ⚠️ ¿Seguro que quieres eliminar <strong>{{ item_name }}</strong>?
    </p>
    <div class="flex gap-2">
        <button
            hx-post="/process/delete/{{ type }}/{{ item_id }}/confirm"
            hx-target="#feedback"
            class="bg-red-600 text-white px-4 py-2 rounded">
            Sí, eliminar
        </button>
        <button
            onclick="this.parentElement.parentElement.remove()"
            class="bg-gray-300 px-4 py-2 rounded">
            Cancelar
        </button>
    </div>
</div>
```

### 5.4 Endpoint de confirmación de eliminación
```python
@router.post("/process/delete/{type}/{id}/confirm")
async def confirm_delete(
    type: str,  # "item" o "section"
    id: int,
    session: Session = Depends(get_session),
):
    if type == "item":
        item = session.get(Item, id)
        session.delete(item)
        session.commit()
        return templates.TemplateResponse(
            "components/feedback.html",
            {"changes": [f"✓ {item.name} eliminado"]}
        )
    # Similar para section...
```

---

## Fase 6: Invalidación de Cache

### 6.1 Evento HTMX después de procesar exitosamente
```python
# En routes/process.py, al final de process_text()
response = templates.TemplateResponse(
    "components/feedback.html",
    {"request": request, "changes": changes, "warnings": warnings}
)

# Agregar header para disparar evento HTMX
response.headers["HX-Trigger"] = "inventoryUpdated"
return response
```

### 6.2 Escuchar evento en Tab "Ver"
```html
<!-- templates/components/inventory_view.html -->
<div class="max-w-2xl mx-auto"
     hx-trigger="inventoryUpdated from:body"
     hx-get="/api/items?offset=0&limit=5"
     hx-target="#items-container"
     hx-swap="innerHTML">
    <!-- contenido ... -->
</div>
```

---

## Fase 7: Cargar Historiales en Background (Prioridad Baja)

**Ejecutar después de implementar Fases 1-6**

### 7.1 Precargar historiales al cargar items
```html
<!-- templates/components/item_row.html -->
<div class="bg-white rounded-lg p-4 mb-3">
    <!-- Contenido del item ... -->

    <!-- Precargar historial en background (no bloquea UI) -->
    <div hx-get="/api/item/{{ item.id }}/history"
         hx-trigger="load delay:1s"
         hx-swap="none">
    </div>
</div>
```

Esto cachea el historial en el navegador sin mostrarlo. Cuando el usuario haga click, carga instantáneamente.

---

## Ideas Futuras (No implementar ahora)

### 1. Optimización de invalidación de cache
- En lugar de refrescar todo el tab "Ver", solo actualizar los items modificados
- Requerir: Retornar IDs de items modificados en la respuesta de `/process/text`

### 2. Predicción de duración de alimentos
- Analizar historial: detectar cuando un item llega a 0
- Calcular promedio de días entre "compra" (aumento grande de cantidad) y "fin" (cantidad = 0)
- Mostrar en UI: "Tomates: 5 unidades (duran ~3 días más)"
- Requerir:
  - Tabla adicional `ItemDurationPattern` con estadísticas
  - Algoritmo de detección de patrones
  - Cronjob o trigger DB para calcular predicciones

### 3. Flags de tipo de cambio en historial
- Agregar campo `change_type` a `ItemHistory`: "purchase", "consumption", "adjustment"
- Detectar automáticamente: si quantity aumenta mucho = "purchase"
- Mostrar en historial con iconos: 🛒 Compra, 🍽️ Consumo, ✏️ Ajuste

---

## Resumen de Prioridades

1. ✅ **Fase 1-2**: DB + API endpoints (base para todo)
2. ✅ **Fase 3**: Tab "Procesar" con contexto asíncrono
3. ✅ **Fase 4**: Tab "Ver" con lazy loading
4. ✅ **Fase 5**: Nuevas funcionalidades LLM (mover, cambiar emoji, eliminar)
5. ✅ **Fase 6**: Invalidación de cache
6. 🔄 **Fase 7**: Precargar historiales (prioridad baja, hacer después)
7. 💡 **Ideas futuras**: Documentadas para referencia

---

## Variables Configurables

Recordatorio: Todas las variables están centralizadas en `config/settings.py`:

```python
# Lazy loading
ITEMS_PER_PAGE = 5  # Fácilmente ajustable para pruebas
HISTORY_RECORDS_PER_ITEM = 10

# Futuros
PRELOAD_HISTORY_DELAY_MS = 1000  # Delay antes de precargar historiales
```
