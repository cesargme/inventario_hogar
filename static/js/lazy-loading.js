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
