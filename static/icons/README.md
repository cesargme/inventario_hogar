# Logo Assets - Inventario Alimentos

## Logo Design
- **Concepto**: Canasta rústica con alimentos (manzana, zanahoria, pan)
- **Estilo**: Moderno, minimalista, rústico
- **Colores**:
  - Beige background: `#F5F5DC`
  - Marrón principal: `#8B4513`
  - Verde oliva (hojas): `#6B8E23`
  - Tonos tierra: `#D2691E`, `#A0522D`, `#D2B48C`

## Archivos
- `logo.svg` - Vector source (512x512)
- `icon-192.png` - PWA icon (generado desde SVG)
- `icon-512.png` - PWA icon (generado desde SVG)
- `favicon.ico` - Browser favicon

## Generar PNGs desde SVG

### Opción 1: Usando Python (cairosvg)
```bash
pip install cairosvg
python -c "
import cairosvg
cairosvg.svg2png(url='logo.svg', write_to='icon-512.png', output_width=512, output_height=512)
cairosvg.svg2png(url='logo.svg', write_to='icon-192.png', output_width=192, output_height=192)
"
```

### Opción 2: Online
1. Ir a https://cloudconvert.com/svg-to-png
2. Upload `logo.svg`
3. Set width/height: 512x512 y 192x192
4. Download y renombrar

### Opción 3: Inkscape CLI
```bash
inkscape logo.svg --export-type=png --export-width=512 --export-filename=icon-512.png
inkscape logo.svg --export-type=png --export-width=192 --export-filename=icon-192.png
```

### Generar Favicon
```bash
# Con ImageMagick
convert icon-192.png -resize 32x32 favicon.ico
```

## Uso en PWA
Los iconos se referencian en `config/manifest.py`:
```python
"icons": [
    {
        "src": "/static/icons/icon-192.png",
        "sizes": "192x192",
        "type": "image/png",
        "purpose": "any maskable"
    },
    {
        "src": "/static/icons/icon-512.png",
        "sizes": "512x512",
        "type": "image/png",
        "purpose": "any maskable"
    }
]
```
