arreglar los colores q esten en tailwind config.js
tambien eso del <script src="https://cdn.tailwindcss.com"></script>
arreglar colores

- [ ] frutero
- [x] sqlite en development
- [x] fecha de cuando se actualizo (historial quizas)
- [x] comandos: mover de seccion (cambiar de nombre a lugar)
- [x] cmd: cambiar de emoji
- [x] cmd eliminar alimento, secciones, pero con confirmación.

- [x] ver optimizar esto?
  - [x] Cómo funciona el cache de tabs:
Ambos tabs están en el DOM pero solo uno visible
Primera vez que cambias al tab "Ver":
HTMX carga el contenido
Se marca como loaded: true
Siguientes veces que cambias al tab "Ver":
Solo se muestra/oculta (toggle hidden class)
NO se vuelve a cargar desde el servidor
El lazy loading se mantiene intacto
Refresca tu navegador (Ctrl+Shift+R) y prueba:
Click en "Ver" → Spinner → Carga items
Click en "Procesar" → Cambia instantáneamente
Click en "Ver" nuevamente → Cambia instantáneamente SIN spinner, mostrando los items ya cargados
¿Funciona ahora?

- [ ] permitir mover de sitio
- [ ] lazy load inteligiente de historial: solo actualizar del nuevo, si es q ya esta cargado. tambien de items...
- [ ] cambiar unidad, ver si se pasa a contexto
- [ ] cambiar de emoji y nombre de seccion
- [ ] eliminar seccion solo si esta vacio, muevelos!
- [ ] acelerar el query y esto
- [ ] optimizar con cacheado el filtrado segun seccion
- [ ] no depender en ms dealy en lazy loads quizas, q sea sequencial
- [ ] al borrar q muestre confirmación
- [ ] poder borrar tras mover todo en el mismo proceso
- [ ] quisas optimizar prompt con tree selection para ahorrar tokens