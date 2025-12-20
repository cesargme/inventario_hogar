arreglar los colores q esten en tailwind config.js
tambien eso del <script src="https://cdn.tailwindcss.com"></script>
arreglar colores

- [ ] frutero
- [ ] sqlite en development
- [ ] fecha de cuando se actualizo (historial quizas)
- [ ] comandos: mover de seccion (cambiar de nombre a lugar)
- [ ] cmd: cambiar de emoji
- [ ] cmd eliminar alimento, secciones, pero con confirmación.

- [ ] ver optimizar esto?
  - [ ] Cómo funciona el cache de tabs:
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
- [ ] cambiar de emoji y nombre de seccion
- [ ] eliminar seccion solo si esta vacio, muevelos!
- [ ] acelerar el query y esto
- 