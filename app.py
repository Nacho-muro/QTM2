import streamlit as st
import yfinance as yf
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, Estimator, Session

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
            per_norm = min(max(per, 0), 100) / 100 * np.pi
            eps_norm = min(max(eps, 0), 10) / 10 * np.pi
            theta = per_norm + eps_norm

            # Circuito cuántico con 1 qubit y 1 clásico
            qc = QuantumCircuit(1, 1)
            qc.sx(0)
            qc.rz(theta, 0)
            qc.sx(0)
            qc.measure(0, 0)

            st.info("Enviando datos a IBM Quantum, espera unos segundos...")

            service = QiskitRuntimeService(
                channel="ibm_quantum",
                token=st.secrets["IBM_QUANTUM_TOKEN"]
            )

            st.write("Backends disponibles:")
            for backend in service.backends():
                st.write(backend.name)

            backend = service.backend("ibm_brisbane")

            # Transpila SOLO para el primer qubit físico
            qc = transpile(qc, backend=backend, initial_layout=[0])

            observable = "Z"

            with Session(backend=backend) as session:
                estimator = Estimator(mode=session)
                estimator.options.resilience_level = 1
                estimator.options.default_shots = 1024

                job = estimator.run([(qc, observable, [[]])])
                result = job.result()
                valor_cuantico = result.data.evs[0]

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
