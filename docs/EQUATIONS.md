# Ecuaciones y niveles de validez

## Longitud de onda

`lambda0 = c0 / f`, donde `c0 = 299792458 m/s` y `f` está en Hz.

## Estimación de parche rectangular

El ancho inicial usa `W = c0/(2f) * sqrt(2/(eps_r + 1))`. Se estima la permitividad efectiva con una aproximación de microcinta y la longitud efectiva `Leff = c0/(2 f sqrt(eps_eff))`; luego se resta la extensión de borde en ambos extremos. Son aproximaciones de primer orden y no resuelven el campo completo.

## Factor de arreglo planar

Para centros `(x_n,z_n)`, `theta` desde el eje frontal +Y y `phi` en el plano X-Z:

`AF = sum(a_n * exp(j * (k*(x_n*sin(theta)*cos(phi) + z_n*sin(theta)*sin(phi)) + phase_n)))`

Se normaliza por la suma de amplitudes. El dashboard presenta `10 log10(|AF_norm|^2)`. Es solo el factor de arreglo ideal; el campo completo requiere patrón de elemento, alimentación, polarización, pérdidas y acoplamiento.

## No calculado en este prototipo

- S11 e impedancia: requieren solver EM o medición con VNA.
- Ganancia realizada y eficiencia: requieren pérdidas y potencia aceptada/radiada.
- F/B real: requiere el patrón completo de la antena.
- Campo a distancia finita: requiere un modelo de campo válido y normalización física.

No sustituir métricas no disponibles por puntuaciones ficticias.
