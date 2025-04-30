
from fpdf import FPDF
import streamlit as st
import datetime
import tempfile
import matplotlib.pyplot as plt
import io
import json
from pathlib import Path

# ---------- Autoryzacja ----------
def load_users():
    with open("allowed_users.json") as f:
        return json.load(f)

def check_login(email, password, users):
    for u in users:
        if u["email"] == email and u["password"] == password:
            return u
    return None

if "user" not in st.session_state:
    st.session_state["user"] = None

if not st.session_state["user"]:
    st.title("🔐 Logowanie do aplikacji")
    email = st.text_input("Adres e-mail")
    password = st.text_input("Hasło", type="password")
    if st.button("Zaloguj"):
        users = load_users()
        user = check_login(email, password, users)
        if user:
            st.session_state["user"] = user
            st.success(f"Zalogowano jako {user['name']}")
            st.experimental_rerun()
        else:
            st.error("Nieprawidłowy e-mail lub hasło")
    st.stop()

# ---------- Konfiguracja ----------
st.set_page_config(page_title="Mindful Eco Impact AI", page_icon="🌱", layout="wide")
st.title("🌱 Mindful Eco Impact AI")
st.subheader("Monitorowanie i redukcja śladu węglowego Twojej organizacji")
st.markdown("""
Witaj w aplikacji **Mindful Eco Impact AI**!  
Tutaj możesz analizować dane ESG, monitorować emisje CO₂ i generować raporty zrównoważonego rozwoju.
""")

# ---------- Formularz ----------
st.header("📊 Wprowadź dane ESG swojej organizacji")

with st.form("esg_form"):
    st.subheader("🔌 Zużycie energii")
    electricity_kwh = st.number_input("Zużycie energii elektrycznej (kWh)", min_value=0.0, step=0.1)
    heating_kwh = st.number_input("Zużycie energii cieplnej (kWh)", min_value=0.0, step=0.1)

    st.subheader("🚌 Transport")
    vehicle_km = st.number_input("Liczba przejechanych kilometrów samochodem firmowym (km)", min_value=0.0, step=0.1)
    flights_hours = st.number_input("Godziny lotów służbowych (h)", min_value=0.0, step=0.1)

    st.subheader("📦 Produkcja / odpady")
    waste_kg = st.number_input("Wygenerowane odpady (kg)", min_value=0.0, step=0.1)

    submitted = st.form_submit_button("Oblicz ślad węglowy")

# ---------- Obliczenia ----------
if submitted:
    CO2_FACTORS = {
        "electricity": 0.0006,
        "heating": 0.00025,
        "vehicle": 0.00021,
        "flight": 0.09,
        "waste": 0.00045
    }

    co2_total = (
        electricity_kwh * CO2_FACTORS["electricity"] +
        heating_kwh * CO2_FACTORS["heating"] +
        vehicle_km * CO2_FACTORS["vehicle"] +
        flights_hours * CO2_FACTORS["flight"] +
        waste_kg * CO2_FACTORS["waste"]
    )

    st.success("✅ Obliczono ślad węglowy!")
    st.metric(label="🌍 Całkowita emisja CO₂e", value=f"{co2_total:.2f} ton")
    st.caption("Wartości szacunkowe oparte na uśrednionych wskaźnikach emisyjności.")

    esg_data = {
        "Energia elektryczna": electricity_kwh * CO2_FACTORS["electricity"],
        "Energia cieplna": heating_kwh * CO2_FACTORS["heating"],
        "Samochód firmowy": vehicle_km * CO2_FACTORS["vehicle"],
        "Loty służbowe": flights_hours * CO2_FACTORS["flight"],
        "Odpady": waste_kg * CO2_FACTORS["waste"]
    }

    # ---------- Wykres ----------
    st.subheader("📈 Wykres emisji CO₂e per obszar")
    fig, ax = plt.subplots()
    ax.bar(esg_data.keys(), esg_data.values(), color='skyblue')
    ax.set_title("Emisja CO₂e per obszar")
    ax.set_ylabel("tCO₂e")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    st.pyplot(fig)

    # ---------- PDF ----------
    def generate_pdf_report(data, total_emission):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, txt="Raport śladu węglowego - Mindful Eco Impact AI", ln=True, align="C")
        pdf.set_font("Arial", "", 12)
        pdf.ln(10)
        pdf.cell(200, 10, txt=f"Data wygenerowania: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
        pdf.ln(5)
        for label, value in data.items():
            pdf.cell(200, 10, txt=f"{label}: {value:.2f} tCO₂e", ln=True)
        pdf.ln(10)
        pdf.set_font("Arial", "B", 14)
        pdf.cell(200, 10, txt=f"Całkowita emisja CO₂e: {total_emission:.2f} ton", ln=True)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        pdf.output(temp_file.name)
        return temp_file.name

    if st.button("📄 Pobierz raport PDF"):
        pdf_path = generate_pdf_report(esg_data, co2_total)
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="📥 Kliknij, aby pobrać PDF",
                data=f,
                file_name="raport_co2e.pdf",
                mime="application/pdf"
            )
