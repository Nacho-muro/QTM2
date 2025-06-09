import streamlit as st
import yfinance as yf
import numpy as np
from qiskit_ibm_runtime import QiskitRuntimeService, Estimator

# Explicaciones de algoritmos cuánticos
EXPLICACIONES = {
    "Quantum Monte Carlo":
        "Este algoritmo permite simular escenarios de mercado y estimar el valor futuro de la empresa bajo diferentes condiciones económicas.",
    "QAOA":
        "QAOA optimiza la combinación de empresas en una cartera para maximizar el rendimiento y minimizar el riesgo.",
    "Grover's Algorithm":
        "Grover puede buscar, entre miles de empresas, aquellas con mejor potencial de crecimiento según ciertos criterios.",
    "HHL Algorithm":
        "HHL resuelve sistemas complejos de ecuaciones para predecir el comportamiento financiero de la empresa."
}

st.title("Valoración Cuántica de Empresas con IBM Quantum")

ticker = st.text_input(
    "Introduce el ticker de la empresa (ej: AMZN, AAPL, GOOGL, TSLA)"
)
algoritmo = st.selectbox(
    "Selecciona el algoritmo cuántico",
    [
        "Quantum Monte Carlo",
        "QAOA",
        "Grover's Algorithm",
        "HHL Algorithm"
    ]
)
calcular = st.button("Optimizar con IBM Quantum")

st.caption("Esta demo obtiene datos reales y ejecuta un análisis cuántico usando IBM Quantum.")

if calcular and ticker.strip():
    ticker = ticker.strip().upper()
    try:
        empresa = yf.Ticker(ticker)
        info = empresa.info
        nombre = info.get("shortName", ticker)
        per = info.get("trailingPE", None)
        eps = info.get("trailingEps", None)
        precio = info.get("currentPrice", None)
        moneda = info.get("currency", "USD")

        st.subheader(f"{nombre} ({ticker})")
        st.write(f"**Precio actual:** {precio} {moneda}" if precio else "Precio actual: No disponible")
        st.write(f"**PER:** {per if per else 'No disponible'}")
        st.write(f"**EPS:** {eps if eps else 'No disponible'}")

        if per is None or eps is None:
            st.warning("No hay suficientes datos financieros para optimizar cuánticamente esta empresa.")
        else:
            # Normaliza PER y EPS para el circuito cuántico
            per_norm = min(max(per, 0), 100) / 100 * np.pi
            eps_norm = min(max(eps, 0), 10) / 10 * np.pi

            # Circuito cuántico de ejemplo
            from qiskit import QuantumCircuit
            qc = QuantumCircuit(1)
            qc.ry(per_norm + eps_norm, 0)
            qc.measure_all()

            st.info("Enviando datos a IBM Quantum, espera unos segundos...")

            # Inicializa el servicio (requiere tu token en los secretos de Streamlit Cloud)
            service = QiskitRuntimeService(token=st.secrets["9095208ccef470cb0a797f771162c63cceba3be91205776bd8f4bef34d57fded35321dc8327ff5ed21903b1992cf5a0959c18407a3a81d456e7574aa0e770746"])
            backend = service.least_busy(operational=False, simulator=True)
            estimator = Estimator(backend=backend)
            estimator.options.resilience_level = 1
            estimator.options.default_shots = 1024

            job = estimator.run(circuits=[qc], observables=["Z"])
            result = job.result()
            valor_cuantico = result.values[0]

            st.success(f"Resultado cuántico (valor esperado): {valor_cuantico:.3f}")
            if valor_cuantico > 0:
                st.write("Interpretación: El análisis cuántico sugiere una perspectiva positiva para la empresa.")
            else:
                st.write("Interpretación: El análisis cuántico sugiere cautela o perspectiva negativa para la empresa.")

        st.markdown("---")
        st.write(EXPLICACIONES[algoritmo])

    except Exception as e:
        st.error(f"No se pudo obtener información o ejecutar el análisis cuántico: {e}")
elif calcular:
    st.warning("Por favor, introduce el ticker de la empresa.")

st.caption("Este análisis es experimental y educativo. Los resultados cuánticos dependen del modelo y los datos enviados.")
