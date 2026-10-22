# Plan de validación

## Nivel 0 — estimación analítica

- Verificar unidades SI, frecuencia positiva y dimensiones de parche positivas.
- Verificar posiciones simétricas y número de elementos.
- Verificar factor de arreglo normalizado igual a 1 en broadside para excitación uniforme.
- Etiquetar las salidas como estimaciones analíticas; no publicar S11, ganancia, eficiencia o F/B como resultados calculados.

## Nivel 1 — solver electromagnético

- Definir sustrato, cobre, plano de masa, alimentación, puertos y contornos.
- Refinar malla y comprobar convergencia.
- Exportar S11, impedancia, patrón 3D, ganancia realizada, eficiencia y polarización.
- Registrar versión del solver, malla, materiales, geometría y configuración.
- Validar un solo elemento antes del arreglo.

## Nivel 2 — arreglo

- Simular 16 elementos con red de alimentación, fases/amplitudes y acoplamiento mutuo.
- Comparar el patrón con el factor analítico para detectar errores de coordenadas y fase.
- No inferir supresión trasera del factor de arreglo aislado.

## Nivel 3 — medición

- Medir S11 con VNA calibrado y plano de referencia documentado.
- Medir patrón en cámara anecoica o instalación adecuada.
- Comparar mediciones y solver con tolerancias documentadas.

## Datos para IA

Cada fila debe incluir estado (`estimate`, `solver`, `measurement`), unidades, geometría/versionado, fuente, incertidumbre y configuración. No mezclar estimaciones y mediciones como etiquetas equivalentes.
