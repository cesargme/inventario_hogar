"""PWA Manifest configuration"""

manifest_data = {
    "name": "Inventario Alimentos",
    "short_name": "InventAlim",
    "description": "Gestiona tu inventario de cocina con comandos de voz",
    "start_url": "/",
    "display": "standalone",
    "background_color": "#F5F5DC",  # Beige claro
    "theme_color": "#8B4513",  # Marrón rústico
    "orientation": "portrait",
    "scope": "/",
    "icons": [
        {
            "src": "/static/icons/icon-192.png",
            "sizes": "192x192",
            "type": "image/png",
            "purpose": "any maskable",
        },
        {
            "src": "/static/icons/icon-512.png",
            "sizes": "512x512",
            "type": "image/png",
            "purpose": "any maskable",
        },
    ],
}
