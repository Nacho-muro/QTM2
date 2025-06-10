import streamlit as st
import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, Estimator, Session
from qiskit.quantum_info import SparsePauliOp

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
            try:
                per = float(per)
                eps = float(eps)
            except (TypeError, ValueError):
                st.error("Error al convertir PER o EPS a número. Verifica los datos.")
                st.stop()

            per_norm = min(max(per, 0), 100) / 100 * np.pi
            eps_norm = min(max(eps, 0), 10) / 10 * np.pi
            theta = per_norm + eps_norm

            try:
                service = QiskitRuntimeService(
                    channel="ibm_quantum",
                    token=st.secrets["IBM_QUANTUM_TOKEN"]
                )
            except Exception as e:
                st.error(f"Error al inicializar el servicio IBM Quantum: {e}")
                st.stop()

            st.write("Backends físicos disponibles y su estado:")
            backends_disponibles = []
            for backend in service.backends(simulator=False):
                status = backend.status()
                st.write(f"{backend.name}: {'Disponible' if status.operational and status.status_msg == 'active' else status.status_msg}")
                if status.operational and status.status_msg == 'active':
                    backends_disponibles.append(backend)

            if not backends_disponibles:
                st.error("No hay backends físicos operativos en este momento. Intenta más tarde.")
                st.stop()

            backend = backends_disponibles[0]
            num_qubits = backend.configuration().num_qubits
            physical_qubit = num_qubits - 1

            qc = QuantumCircuit(1)
            qc.sx(0)
            qc.rz(theta, 0)
            qc.sx(0)

            qc = transpile(
                qc,
                backend=backend,
                initial_layout=[physical_qubit],
                optimization_level=3
            )

            observable_str = "I" * physical_qubit + "Z" + "I" * (num_qubits - physical_qubit - 1)
            observable = SparsePauliOp(observable_str)

            st.info(f"Ejecutando en {backend.name} sobre el qubit físico {physical_qubit}...")

            with Session(backend=backend) as session:
                estimator = Estimator(mode=session)
                estimator.options.resilience_level = 1
                estimator.options.default_shots = 1024

                job = estimator.run([(qc, observable, [])])
                result = job.result()
                valor_cuantico = result[0].data.evs[0]

            st.success(f"Resultado cuántico (valor esperado): {valor_cuantico:.3f}")
            if valor_cuantico > 0:
                st.write("**Interpretación:** El análisis cuántico sugiere una perspectiva positiva para la empresa.")
            else:
                st.write("**Interpretación:** El análisis cuántico sugiere cautela o perspectiva negativa para la empresa.")

            # Gráfico de precio histórico
            st.subheader("Precio histórico")
            hist = empresa.history(period="1y")
            if not hist.empty:
                fig, ax = plt.subplots()
                ax.plot(hist.index, hist['Close'])
                ax.set_title(f"Precio histórico de {nombre} ({ticker})")
                ax.set_ylabel("Precio (USD)")
                st.pyplot(fig)
            else:
                st.warning("No hay datos históricos disponibles.")

            # Comparativa con el sector (ejemplo manual)
            st.subheader("Comparativa con el sector (ejemplo)")
            st.write("AAPL: PER=30, EPS=6.5 (valores de ejemplo)")
            st.write("MSFT: PER=35, EPS=9.2 (valores de ejemplo)")
            st.write("GOOGL: PER=28, EPS=5.8 (valores de ejemplo)")
            st.write("Estos valores son solo ilustrativos. Puedes automatizar la comparativa con una API o base de datos.")

            # Simulación de escenarios
            st.subheader("Simulación de escenarios")
            with st.expander("Simula diferentes valores de PER y EPS"):
                per_sim = st.slider("PER simulado", 0.0, 100.0, float(per))
                eps_sim = st.slider("EPS simulado", 0.0, 20.0, float(eps))
                per_norm_sim = min(max(per_sim, 0), 100) / 100 * np.pi
                eps_norm_sim = min(max(eps_sim, 0), 20) / 20 * np.pi
                theta_sim = per_norm_sim + eps_norm_sim
                st.write(f"Valor cuántico simulado: {np.sin(theta_sim):.3f} (solo como ejemplo)")

        st.markdown("---")
        st.write(EXPLICACIONES[algoritmo])

    except Exception as e:
        st.error(f"No se pudo obtener información o ejecutar el análisis cuántico: {e}")
elif calcular:
    st.warning("Por favor, introduce el ticker de la empresa.")

st.caption("Este análisis es experimental y educativo. Los resultados cuánticos dependen del modelo y los datos enviados.")
