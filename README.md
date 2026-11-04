# ED.02.04---Herramientas-de-visualizacion
---
## Respuestas
---
**Quiero ver si el dólar está más caro o más barato que hace tres años.**
Se responde con la gráfica "g1_serie.png"

**Necesito saber en qué meses del año suele moverse más, para programar nuestras compras.**
Ninguna de las dos gráficas originales responde la pregunta. Se necesitaría mapear los meses

**¿Qué tan común es que el tipo de cambio brinque más de 2 % en un solo día?**
Es raro, solo pasa en aproximadamente 10 casos en los 5 años de rango; la mayoría de los datos se concentran en un rango aprox. de -1.5% a 1.5%.

**Quiero comparar qué tan estable estuvo 2021 contra 2025.**
En el 2025 hubo menos varianza, eso quiere decir que tuvo un valor más estable a lo largo del año que en 2021, aunque si hablamos de precio, en el ciclo 2021-2022 el dolar valía aproximadamente $21 pesos, más que en el 2025-2026 donde acabó con un valor de un poco más de $18.
De hecho me parece raro ver que en la varianza, el ciclo 2025 tiene una mayor estabilidad, pero en la gráfica del valor diario se ve una gran caída de valor.

**Me interesa saber si el tipo de cambio se mueve junto con las tasas de interés.**
Se requiere la serie oficial de las tasas (por ejemplo, TIIE o tasa de referencia de Banxico) para concluir una relación causal. La gráfica "g3_tasa_vs_tipo.png" ofrece una comparación con una referencia de tasas para contexto; en este periodo no aparece un co-movimiento lineal ni automático. El tipo de cambio se mueve mucho más que la tasa y su comportamiento está más ligado a presión de mercado, liquidez y riesgo país que a una relación mecánica con los tipos de interés.

**Dime cuánto va a costar el dólar el mes que entra, para cerrar el presupuesto**
No es posible predecir el valor exacto del siguiente mes, pero sí es posible estimar un rango prudente. La gráfica "g4_proyeccion_dolar.png" muestra un rango plausible para el próximo mes centrado en aproximadamente $18.17 por dólar, con una banda razonable alrededor de $18.1 a $18.8, según el comportamiento reciente del mercado. Esa estimación es útil para presupuestar, pero no reemplaza un pronóstico financiero formal.

**Necesito saber cuánto dinero perdimos el año pasado por el tipo de cambio.**
La pérdida depende del monto que se tenía en dólares y de si la empresa era deudora o acreedora en esa moneda. Con la información disponible, la gráfica "g5_impacto_cambio.png" muestra el impacto sobre una exposición en USD. El promedio de 2025 fue $19.20, mientras que el de 2024 fue $18.33; la diferencia anual fue aproximadamente $0.87 por dólar. Eso significa que, por cada $1,000 USD de exposición, el costo en pesos aumentó cerca de $873; por $10,000 USD, casi $8,732; y por $100,000 USD, alrededor de $87,324. En otras palabras, la pérdida o ganancia se calcula con el monto y la dirección de la exposición, no con el tipo de cambio por sí solo.