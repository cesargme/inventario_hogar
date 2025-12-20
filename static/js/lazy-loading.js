/**
 * LAZY_LOADING_SYSTEM: Sistema centralizado de lazy loading
 * Busca "LAZY_LOADING_SYSTEM" en el código para encontrar implementaciones
 */

// LAZY_LOADING_SYSTEM: Modal Cache Manager
const ModalCache = {
    cache: {},

    save(modalId, html) {
        console.log(`[MODAL_CACHE] Saving: ${modalId}`);
        // NO remover triggers de intersect - los necesitamos para infinite scroll del historial
        this.cache[modalId] = html;
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
        console.log(`[MODAL_CACHE] Opening from cache: history-${itemId}`);
        const container = document.getElementById('modal-container');
        container.innerHTML = cached;
        // Reinicializar HTMX en el contenido cacheado para que los triggers funcionen
        htmx.process(container);
    } else {
        console.log(`[MODAL_CACHE] Not in cache, fetching: history-${itemId}`);
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
        const itemId = itemIdMatch[1];
        // Solo cachear si no tiene triggers pendientes (para evitar triggers duplicados)
        const hasPendingTriggers = modal.querySelector('[hx-trigger*="intersect once"]');
        if (!hasPendingTriggers) {
            ModalCache.save(`history-${itemId}`, modal.innerHTML);
        } else {
            console.log(`[MODAL_CACHE] Not caching history-${itemId} - has pending triggers`);
        }
    }
    modal.innerHTML = '';
}

// LAZY_LOADING_SYSTEM: Track preloading to avoid duplicates
const preloadingSet = new Set();

// LAZY_LOADING_SYSTEM: Preload visible item histories (BATCH)
function preloadVisibleHistories() {
    const itemCards = document.querySelectorAll('#items-container .bg-white');
    console.log(`[LAZY_LOADING_SYSTEM] Found ${itemCards.length} item cards to preload`);

    // Recolectar IDs que necesitan precarga
    const idsToPreload = [];
    itemCards.forEach((card) => {
        const button = card.querySelector('button[onclick^="openHistoryModal"]');
        if (button) {
            const match = button.getAttribute('onclick').match(/openHistoryModal\((\d+)\)/);
            if (match) {
                const itemId = match[1];
                // Skip if already cached or currently preloading
                if (!ModalCache.get(`history-${itemId}`) && !preloadingSet.has(itemId)) {
                    idsToPreload.push(itemId);
                    preloadingSet.add(itemId);
                }
            }
        }
    });

    if (idsToPreload.length === 0) {
        console.log('[LAZY_LOADING_SYSTEM] No items to preload');
        return;
    }

    console.log(`[LAZY_LOADING_SYSTEM] Batch preloading ${idsToPreload.length} histories:`, idsToPreload);

    // Hacer una sola llamada batch
    fetch(`/inventory/api/items/batch-history-views?item_ids=${idsToPreload.join(',')}`)
        .then(response => response.json())
        .then(data => {
            console.log(`[LAZY_LOADING_SYSTEM] Batch loaded ${Object.keys(data).length} histories`);
            // Cachear cada historial
            Object.entries(data).forEach(([itemId, html]) => {
                ModalCache.save(`history-${itemId}`, html);
                preloadingSet.delete(itemId);
                console.log(`[LAZY_LOADING_SYSTEM] Cached history-${itemId}`);
            });
        })
        .catch(err => {
            console.error(`[LAZY_LOADING_SYSTEM] Error batch preloading`, err);
            // Limpiar todos los IDs del set en caso de error
            idsToPreload.forEach(id => preloadingSet.delete(id));
        });
}

// LAZY_LOADING_SYSTEM: Preload after infinite scroll
document.body.addEventListener('htmx:afterSwap', function(evt) {
    const target = evt.detail.target;

    // Detect infinite scroll trigger swap by class
    const isInfiniteScroll = target.classList && target.classList.contains('lazy-scroll-trigger');

    if (isInfiniteScroll) {
        console.log('[LAZY_LOADING_SYSTEM] Infinite scroll detected');
        const inventoryTab = document.getElementById('view-inventory');
        if (inventoryTab && !inventoryTab.classList.contains('hidden')) {
            console.log('[LAZY_LOADING_SYSTEM] Inventory tab visible, preloading new items...');
            setTimeout(() => preloadVisibleHistories(), 100);
        }
    }
});

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
