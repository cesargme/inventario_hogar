# Plan de Migración a JinjaX

## Decisiones Clave
- ✅ Migrar TODO a `catalog.render()` y envolver en HTMLResponse para simplificar
- ✅ Incluir 2-3 tests de ejemplo
- ✅ Migración paso a paso, validando cada fase
- ✅ Sin documentación adicional
- ✅ Sobre código actual, simplificando cuando sea posible
- ✅ Mantener Tailwind CSS global (sin cambios)

---

## Fase 0: Preparación (15 min)

### Acciones:
1. **Instalar JinjaX**
```bash
pip install jinjax
```

2. **Actualizar requirements.txt**
```txt
jinjax==0.44.0  # o versión más reciente
```

3. **Modificar app.py**
```python
import jinjax
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Integrar JinjaX con el entorno Jinja de FastAPI
templates.env.add_extension(jinjax.JinjaX)
catalog = jinjax.Catalog(jinja_env=templates.env)
catalog.add_folder("components")

# Exponer catalog como global
templates.env.globals["catalog"] = catalog
```

4. **Crear estructura de carpetas**
```
├── components/           🆕
│   ├── layout/
│   ├── ui/
│   └── features/
```

### Validación:
- [ ] JinjaX instalado sin errores
- [ ] Servidor FastAPI arranca sin errores
- [ ] Carpeta `components/` creada

---

## Fase 1: Componentes Base (30 min)

### 1.1 InfiniteScroll Component

**`components/ui/InfiniteScroll.jinja`**
```jinja
{#def url, skeleton_count=2, label="" #}
{#-- LAZY_LOADING_SYSTEM: Infinite Scroll Component --#}

<div class="lazy-scroll-trigger"
     data-lazy-type="infinite-scroll"
     data-lazy-url="{{ url }}"
     data-lazy-label="{{ label }}"
     hx-get="{{ url }}"
     hx-trigger="intersect once threshold:0.5"
     hx-swap="outerHTML"
     {{ attrs.render(class="space-y-3") }}>
    {% for _ in range(skeleton_count) %}
        {{ content("skeleton") }}
    {% endfor %}
</div>
```

### 1.2 BackgroundLoader Component

**`components/ui/BackgroundLoader.jinja`**
```jinja
{#def url, delay="1s", label="" #}
{#-- LAZY_LOADING_SYSTEM: Background Preloader --#}

<div class="lazy-preloader hidden"
     data-lazy-type="background-preload"
     data-lazy-url="{{ url }}"
     data-lazy-label="{{ label }}"
     hx-get="{{ url }}"
     hx-trigger="load delay:{{ delay }}"
     hx-swap="none">
</div>
```

### 1.3 Utility Components

**`components/ui/EmptyState.jinja`**
```jinja
{#def message, submessage="" #}

<div {{ attrs.render(class="text-center p-8 text-gray-500") }}>
    <p class="text-lg">{{ message }}</p>
    {% if submessage %}
    <p class="text-sm mt-2">{{ submessage }}</p>
    {% endif %}
</div>
```

**`components/ui/LoadingSpinner.jinja`**
```jinja
<div {{ attrs.render(class="flex justify-center items-center p-8") }}>
    <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
</div>
```

**`components/ui/ItemSkeleton.jinja`**
```jinja
<div class="bg-gray-200 rounded-lg p-4 mb-3 animate-pulse">
    <div class="flex items-center gap-3 mb-2">
        <div class="w-8 h-8 bg-gray-300 rounded"></div>
        <div class="flex-1">
            <div class="h-4 bg-gray-300 rounded w-3/4 mb-2"></div>
            <div class="h-3 bg-gray-300 rounded w-1/2"></div>
        </div>
    </div>
</div>
```

**`components/ui/HistorySkeleton.jinja`**
```jinja
<div class="bg-gray-200 rounded-lg p-3 mb-2 animate-pulse">
    <div class="h-4 bg-gray-300 rounded w-1/3 mb-2"></div>
    <div class="h-6 bg-gray-300 rounded w-2/3"></div>
</div>
```

### Validación:
- [ ] Todos los componentes creados sin errores de sintaxis
- [ ] Probar render simple: `catalog.render("ui/LoadingSpinner")`

---

## Fase 2: Feature Components (45 min)

### 2.1 ItemRow Component

**`components/features/ItemRow.jinja`**
```jinja
{#def item #}
{#-- LAZY_LOADING_SYSTEM: Item with background history preload --#}

<div {{ attrs.render(class="bg-white rounded-lg p-4 shadow-sm border-l-4 " +
    ("border-red-500" if item.is_below_threshold else "border-secondary")) }}>

    <div class="flex items-start justify-between">
        <div class="flex-1">
            <div class="flex items-center gap-2 mb-1">
                <span class="text-2xl">{{ item.emoji }}</span>
                <h3 class="text-lg font-semibold">{{ item.name|title }}</h3>
                {% if item.is_below_threshold %}
                <span class="text-red-500 text-sm font-bold">⚠️ BAJO</span>
                {% endif %}
            </div>

            <div class="text-sm text-gray-600 space-y-1">
                <p class="font-medium text-lg">
                    {{ item.quantity }} {{ item.unit }}
                </p>
                <p class="flex items-center gap-1">
                    <span class="text-gray-500">{{ item.section_emoji }}</span>
                    <span>{{ item.section_name }}</span>
                </p>
                <p class="text-xs text-gray-400">
                    Actualizado {{ item.updated_at_human }}
                </p>
            </div>
        </div>
    </div>

    <button onclick="openHistoryModal({{ item.id }})"
            class="text-sm text-blue-600 hover:text-blue-800 mt-2 underline">
        Ver historial
    </button>

    {#-- Preload history in background --#}
    <BackgroundLoader
        url="/inventory/api/item/{{ item.id }}/history?offset=0"
        delay="1s"
        label="history-item-{{ item.id }}" />
</div>
```

### 2.2 ItemsList Component

**`components/features/ItemsList.jinja`**
```jinja
{#def items, offset, section_id=None, has_more=False #}

{% for item in items %}
    <ItemRow :item="item" />
{% endfor %}

{% if has_more %}
    <InfiniteScroll
        url="/inventory/api/items?offset={{ offset }}{% if section_id %}&section_id={{ section_id }}{% endif %}"
        skeleton_count=2
        label="items-pagination">
        {#-- Named slot for skeleton --#}
        {% if _slot == "skeleton" %}
            <ItemSkeleton />
        {% endif %}
    </InfiniteScroll>
{% endif %}

{% if items|length == 0 %}
    <EmptyState
        message="No hay items en tu inventario"
        submessage="Usa el tab 'Procesar' para agregar items" />
{% endif %}
```

### 2.3 History Components

**`components/features/HistoryRecord.jinja`**
```jinja
{#def record #}

<div class="bg-gray-50 rounded-lg p-3 mb-2">
    <div class="flex items-center justify-between">
        <div>
            <p class="text-sm text-gray-600">{{ record.date_human }}</p>
            <p class="text-lg font-semibold">
                <span class="text-gray-500">{{ record.before }}</span>
                <span class="text-blue-600 mx-2">→</span>
                <span class="text-gray-900">{{ record.after }}</span>
            </p>
        </div>
        {% if record.after > record.before %}
        <span class="text-green-600 text-2xl">↑</span>
        {% elif record.after < record.before %}
        <span class="text-red-600 text-2xl">↓</span>
        {% endif %}
    </div>
</div>
```

**`components/features/HistoryList.jinja`**
```jinja
{#def history, item_id, offset, has_more=False #}

{% for record in history %}
    <HistoryRecord :record="record" />
{% endfor %}

{% if has_more %}
    <InfiniteScroll
        url="/inventory/api/item/{{ item_id }}/history?offset={{ offset }}"
        skeleton_count=2
        label="history-pagination-{{ item_id }}">
        {#-- Named slot for skeleton --#}
        {% if _slot == "skeleton" %}
            <HistorySkeleton />
        {% endif %}
    </InfiniteScroll>
{% endif %}

{% if not history and not has_more %}
    <EmptyState message="No hay historial disponible" />
{% endif %}
```

**`components/features/HistoryView.jinja`**
```jinja
{#def item, history, offset, has_more=False #}
{#-- Modal de historial completo --#}

<div class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-end"
     data-item-id="{{ item.id }}">
    <div class="bg-white w-full h-5/6 rounded-t-2xl overflow-hidden flex flex-col">
        <!-- Header -->
        <div class="bg-blue-600 text-white p-4 flex items-center justify-between">
            <div class="flex items-center gap-2">
                <span class="text-2xl">{{ item.emoji }}</span>
                <div>
                    <h2 class="text-lg font-semibold">{{ item.name|title }}</h2>
                    <p class="text-sm opacity-90">Historial de cambios</p>
                </div>
            </div>
            <button onclick="closeHistoryModal()"
                    class="text-white text-2xl font-bold">
                ✕
            </button>
        </div>

        <!-- Content con scroll -->
        <div class="flex-1 overflow-y-auto p-4">
            <HistoryList
                :history="history"
                :item_id="item.id"
                :offset="offset"
                :has_more="has_more" />
        </div>
    </div>
</div>
```

### Validación:
- [ ] Componentes renderizan sin errores
- [ ] Test: `catalog.render("features/ItemRow", item=mock_item)`
- [ ] Test: `catalog.render("features/HistoryView", item=mock_item, history=[], offset=0, has_more=False)`

---

## Fase 3: Layout Components (30 min)

### 3.1 Base Layout

**`components/layout/Base.jinja`**
```jinja
{#def title="Inventario Alimentos" #}

<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <link rel="stylesheet" href="/static/css/output.css">
</head>
<body class="min-h-screen bg-white">
    {{ content }}
    <script src="/static/js/htmx.min.js"></script>
    <script src="/static/js/lazy-loading.js"></script>
</body>
</html>
```

### 3.2 AppShell Layout

**`components/layout/AppShell.jinja`**
```jinja
{#def title="Inventario Alimentos" #}

<Base :title="title">
    <div class="flex-1 pb-16">
        <header class="bg-gray-50 text-gray-900 p-4 shadow-md">
            <h1 class="text-2xl font-bold text-center">🥘 {{ title }}</h1>
        </header>

        <main class="p-4 bg-white">
            {{ content }}
        </main>
    </div>

    <!-- Incluir tabs como componente si existe, sino placeholder -->
    {{ content("tabs") }}

    <div id="modal-container"></div>
</Base>
```

### Validación:
- [ ] Layout renderiza correctamente
- [ ] CSS y JS se cargan
- [ ] Test: `catalog.render("layout/Base", title="Test")`

---

## Fase 4: JavaScript Centralizado (20 min)

**`static/js/lazy-loading.js`**
```javascript
/**
 * LAZY_LOADING_SYSTEM: Sistema centralizado de lazy loading
 * Busca "LAZY_LOADING_SYSTEM" en el código para encontrar implementaciones
 */

// LAZY_LOADING_SYSTEM: Modal Cache Manager
const ModalCache = {
    cache: {},

    save(modalId, html) {
        console.log(`[MODAL_CACHE] Saving: ${modalId}`);
        const temp = document.createElement('div');
        temp.innerHTML = html;
        temp.querySelectorAll('[hx-trigger*="intersect"]').forEach(el => el.remove());
        this.cache[modalId] = temp.innerHTML;
    },

    get(modalId) {
        const cached = this.cache[modalId];
        console.log(`[MODAL_CACHE] ${cached ? 'Hit' : 'Miss'}: ${modalId}`);
        return cached;
    },

    invalidate(modalId) {
        console.log(`[MODAL_CACHE] Invalidating: ${modalId}`);
        delete this.cache[modalId];
    },

    clear() {
        console.log(`[MODAL_CACHE] Clearing all`);
        this.cache = {};
    }
};

// LAZY_LOADING_SYSTEM: History Modal Management
function openHistoryModal(itemId) {
    const cached = ModalCache.get(`history-${itemId}`);
    if (cached) {
        document.getElementById('modal-container').innerHTML = cached;
    } else {
        htmx.ajax('GET', `/inventory/item/${itemId}/history-view`, {
            target: '#modal-container',
            swap: 'innerHTML'
        });
    }
}

function closeHistoryModal() {
    const modal = document.getElementById('modal-container');
    const itemIdMatch = modal.innerHTML.match(/data-item-id="(\d+)"/);
    if (itemIdMatch) {
        ModalCache.save(`history-${itemIdMatch[1]}`, modal.innerHTML);
    }
    modal.innerHTML = '';
}

// LAZY_LOADING_SYSTEM: Cache invalidation on inventory update
document.body.addEventListener('inventoryUpdated', function() {
    console.log('[LAZY_LOADING_SYSTEM] Inventory updated, clearing cache');
    ModalCache.clear();
});

// Debug helper
window.debugLazyLoading = function() {
    console.log('=== LAZY LOADING DEBUG ===');
    console.log('Background preloaders:',
        document.querySelectorAll('[data-lazy-type="background-preload"]').length);
    console.log('Infinite scrolls:',
        document.querySelectorAll('[data-lazy-type="infinite-scroll"]').length);
    console.log('Cached modals:', Object.keys(ModalCache.cache));
};
```

### Validación:
- [ ] Archivo creado
- [ ] Funciones disponibles en consola del navegador
- [ ] `debugLazyLoading()` funciona

---

## Fase 5: Actualizar Routes (15 min)

### Ejemplo: Modificar endpoint de historial

**`routes/inventory.py`**
```python
@router.get("/item/{item_id}/history-view", response_class=HTMLResponse)
async def get_item_history_view(
    request: Request,
    item_id: int,
    user: User = Depends(verify_credentials),
    session: Session = Depends(get_session),
):
    """Vista completa de historial con infinite scroll"""
    item = session.get(Item, item_id)
    if not item:
        return HTMLResponse("Item no encontrado", status_code=404)

    # ... lógica de historial (mantener actual) ...
    all_history = session.exec(
        select(ItemHistory)
        .where(ItemHistory.item_id == item_id)
        .order_by(ItemHistory.changed_at.desc())
    ).all()

    limit = HISTORY_RECORDS_PER_ITEM
    history = all_history[0:limit]

    history_data = []
    for i, record in enumerate(history):
        before = all_history[i + 1].quantity if i + 1 < len(all_history) else 0
        after = record.quantity
        history_data.append({
            "before": before,
            "after": after,
            "changed_at": record.changed_at,
            "date_human": humanize_time(record.changed_at)
        })

    has_more = limit < len(all_history)

    # 🆕 Usar componente JinjaX
    return HTMLResponse(
        catalog.render(
            "features/HistoryView",
            item=item,
            history=history_data,
            offset=limit,
            has_more=has_more
        )
    )
```

### Ejemplo: Modificar endpoint de items list

**`routes/inventory.py`**
```python
@router.get("/api/items", response_class=HTMLResponse)
async def get_items_paginated(
    request: Request,
    offset: int = Query(0),
    limit: int = Query(ITEMS_PER_PAGE),
    section_id: int | None = Query(None),
    user: User = Depends(verify_credentials),
    session: Session = Depends(get_session),
):
    """Retorna items paginados para infinite scroll"""
    stmt = select(Item).order_by(Item.updated_at.desc())

    if section_id:
        stmt = stmt.where(Item.section_id == section_id)

    stmt = stmt.offset(offset).limit(limit)
    items = session.exec(stmt).all()

    items_data = serialize_items_for_template(items)
    has_more = len(items) == limit

    # 🆕 Usar componente JinjaX
    return HTMLResponse(
        catalog.render(
            "features/ItemsList",
            items=items_data,
            offset=offset + limit,
            section_id=section_id,
            has_more=has_more
        )
    )
```

### Validación:
- [ ] Endpoints modificados funcionan
- [ ] Lazy loading funciona
- [ ] Infinite scroll funciona
- [ ] Background preload funciona
- [ ] Modal cache funciona

---

## Fase 6: Limpieza (10 min)

### Archivos a eliminar:
```
templates/components/
├── item_row.html           ❌ (reemplazado por components/features/ItemRow.jinja)
├── items_list.html         ❌ (reemplazado por components/features/ItemsList.jinja)
├── item_skeleton.html      ❌ (reemplazado por components/ui/ItemSkeleton.jinja)
├── history_list.html       ❌ (reemplazado por components/features/HistoryList.jinja)
├── history_view.html       ❌ (reemplazado por components/features/HistoryView.jinja)
├── history_skeleton.html   ❌ (inline, ahora en components/ui/HistorySkeleton.jinja)
└── loading_spinner.html    ❌ (reemplazado por components/ui/LoadingSpinner.jinja)
```

### Mantener (si existen):
```
templates/
├── base.html               ✅ (mantener temporalmente)
├── index.html              ✅ (mantener temporalmente)
└── components/
    ├── process_view.html   ✅ (migrar después)
    ├── tabs.html           ✅ (migrar después)
    └── ...otros...         ✅ (migrar gradualmente)
```

### Validación:
- [ ] Archivos legacy eliminados
- [ ] Aplicación funciona sin errores
- [ ] No hay referencias rotas a templates eliminados

---

## Tests de Ejemplo

**`tests/test_components.py`** (crear si no existe)
```python
import pytest
from datetime import datetime
from app import catalog

def test_loading_spinner_renders():
    """Test que LoadingSpinner renderiza correctamente"""
    html = catalog.render("ui/LoadingSpinner")
    assert "animate-spin" in html
    assert "border-blue-600" in html

def test_empty_state_with_submessage():
    """Test EmptyState con mensaje secundario"""
    html = catalog.render(
        "ui/EmptyState",
        message="No hay datos",
        submessage="Intenta agregar algunos"
    )
    assert "No hay datos" in html
    assert "Intenta agregar algunos" in html

def test_item_row_renders():
    """Test ItemRow con mock item"""
    mock_item = {
        "id": 1,
        "name": "leche",
        "emoji": "🥛",
        "quantity": 2,
        "unit": "L",
        "section_emoji": "❄️",
        "section_name": "Refrigerador",
        "updated_at_human": "hace 2h",
        "is_below_threshold": False
    }

    html = catalog.render("features/ItemRow", item=mock_item)
    assert "leche" in html.lower()
    assert "🥛" in html
    assert "Ver historial" in html
```

### Validación:
- [ ] Tests pasan: `pytest tests/test_components.py`

---

## Estructura Final

```
inventario_hogar/
├── app.py                  # JinjaX catalog configurado
├── components/             🆕 Todos los componentes JinjaX
│   ├── layout/
│   │   ├── Base.jinja
│   │   └── AppShell.jinja
│   ├── ui/
│   │   ├── InfiniteScroll.jinja
│   │   ├── BackgroundLoader.jinja
│   │   ├── EmptyState.jinja
│   │   ├── LoadingSpinner.jinja
│   │   ├── ItemSkeleton.jinja
│   │   └── HistorySkeleton.jinja
│   └── features/
│       ├── ItemRow.jinja
│       ├── ItemsList.jinja
│       ├── HistoryRecord.jinja
│       ├── HistoryList.jinja
│       └── HistoryView.jinja
├── static/
│   ├── css/
│   │   ├── input.css
│   │   └── output.css      # Tailwind global (sin cambios)
│   └── js/
│       ├── htmx.min.js
│       └── lazy-loading.js  🆕
├── routes/
├── templates/              (migrar gradualmente)
└── tests/
    └── test_components.py  🆕
```

---

## Cómo Rastrear Lazy Loading

### En el código:
```bash
# Buscar todos los lazy loading
grep -r "LAZY_LOADING_SYSTEM" components/

# Buscar background preloaders
grep -r "BackgroundLoader" components/

# Buscar infinite scrolls
grep -r "InfiniteScroll" components/
```

### En el navegador:
```javascript
// Ver estado de lazy loading
debugLazyLoading()

// Ver elementos activos
document.querySelectorAll('[data-lazy-type]')
```

---

## Beneficios Esperados

- ✅ **-60% código duplicado** (~120 líneas eliminadas)
- ✅ **Componentes reutilizables** tipo React/Vue
- ✅ **HTMX encapsulado** en componentes
- ✅ **Testing unitario** de componentes
- ✅ **Rastreabilidad** con marcadores
- ✅ **Mantiene Tailwind** sin cambios
- ✅ **Fácil expansión** futura
