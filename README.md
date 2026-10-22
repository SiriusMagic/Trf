# ATLAS-RF — laboratorio científico de antenas

ATLAS-RF es un proyecto reproducible para estudiar antenas de radiofrecuencia, comenzando con un parche microstrip rectangular y ampliándose posteriormente a arrays, mapas de campo, análisis espectral y optimización.

## Estado científico

- **Frecuencia de referencia:** 5.00 GHz provisional; debe confirmarse.
- **Geometría:** parche rectangular microstrip.
- **Sustrato inicial:** Rogers RO4350B, permitividad relativa nominal aproximada 3.48.
- **Espesor dieléctrico:** 0.762 mm.
- **Cobre:** 35 µm provisional.
- **Puerto de referencia:** 50 ohmios.
- **Dirección frontal de visualización:** +Y.
- **Elementos:** 1.

> Este prototipo calcula estimaciones analíticas y visualizaciones ilustrativas. No es un solucionador electromagnético completo, no predice con precisión S11 ni eficiencia, y no debe usarse como única base para fabricar. La compatibilidad con Starlink no está establecida: primero hay que identificar el modelo de terminal y sus bandas de operación.

## Instalación

Requiere Python 3.10 o superior.

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell:
# .venv\\Scripts\\Activate.ps1

pip install -r requirements.txt
python -m src.atlas_rf --config config/default.json
```

Los gráficos se guardan en `results/`.

## Estructura

- `config/default.json`: parámetros editables.
- `src/atlas_rf/`: ecuaciones y visualizaciones.
- `tests/`: pruebas unitarias de los cálculos.
- `docs/EQUATIONS.md`: ecuaciones, supuestos y límites.
- `docs/VALIDATION_PLAN.md`: plan de validación.
- `results/`: salidas generadas localmente; no contiene mediciones de fábrica.

## Roadmap

1. Confirmar frecuencia objetivo y datos de fabricación.
2. Validar cálculo inicial del parche.
3. Incorporar simulación EM externa (por ejemplo, openEMS o un solucionador comercial).
4. Añadir curvas S11/VSWR solo a partir de simulación EM o mediciones.
5. Extender a arrays y fase/amplitud por elemento.
6. Añadir optimización con límites físicos y métricas de validación.
7. Comparar predicciones con VNA y mediciones de patrón, cuando haya equipo disponible.

## Licencia

Por decidir antes de publicar el repositorio.
