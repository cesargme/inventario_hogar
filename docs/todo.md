arreglar los colores q esten en tailwind config.js
tambien eso del <script src="https://cdn.tailwindcss.com"></script>
arreglar colores

- [x] cambiar contraseña
- [ ] frutero
- [ ] compartir con fam lmfao
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

- [x] CONTINUAR ACA - terminar corregir lazy loading de historial
- [x] permitir mover de sitio
- [ ] ordnear por prioritarios q falten. hacer lista para whatsapp (client side?)
- [ ] arreglar platano vs plátano, y platano de la isla ... tambien cambiar nombre poder. tarros de leche q no este separado de leche.
- [ ] cambiar unidad, ver si se pasa a contexto
- [ ] cambiar de nombre de seccion
- [ ] optimizar menos uso de memoria ver donde se usa mas memoria
- [ ] lazy load inteligiente de historial: solo actualizar del nuevo, si es q ya esta cargado. tambien de items...
- [ ] acelerar el query y esto
- [ ] optimizar con cacheado el filtrado segun seccion
- [ ] al borrar q muestre confirmación
- [ ] poder borrar tras mover todo en el mismo proceso
- [ ] quisas optimizar prompt con tree selection para ahorrar tokens
- [ ] cambiar de unidad... umbral y tmb mostrar umbral
- [x] infinite scrolling a partir de cuanto? htmx del 5 item cargar 10
- [ ] corregir eliminar item por su historial no funciona creo.

- [ ] lazy-loading.js muy complejo, hacerlo mas mantenible.
- [ ] hacer lazy load si cambio en servidor (artutor por ejemplo cambio)
- [ ] context: can i cache serverside the list of items names and sections? to avoid select * what's it called?
- [ ] is my current cache client side? if so is it bad? or the current data is nto that compromising
- [ ] eliminar seccion solo si esta vacio, muevelos!
- [ ] no depender en ms dealy en lazy loads quizas, q sea sequencial