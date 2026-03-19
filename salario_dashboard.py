import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="Dashboard RV", layout="wide")

# =========================
# ESTILO
# =========================

st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: 'Segoe UI', sans-serif;
    color: #1F2937;
}

.block-container {
    padding-top: 3rem;
    padding-left: 2rem;
    padding-right: 2rem;
    background-color: #F7F9F8;
}

.header {
    background-color: #00A868;
    padding: 16px;
    border-radius: 8px;
    color: white;
    font-size: 24px;
    font-weight: 600;
    margin-bottom: 25px;
}

section[data-testid="stSidebar"] {
    background-color: #F0F2F1;
}

.section-title {
    font-size: 20px;
    font-weight: 600;
    margin-top: 25px;
    margin-bottom: 10px;
    color: #111827;
}

[data-testid="stMetricValue"] {
    font-size: 26px;
    font-weight: 600;
    color: #111827;
}

[data-testid="stMetricLabel"] {
    color: #6B7280;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header">Hunter | Dashboard de Projeção Salarial</div>', unsafe_allow_html=True)

# =========================
# SIDEBAR
# =========================

st.sidebar.title("Parâmetros")

st.sidebar.markdown("### 💰 Financeiro")
salario = st.sidebar.number_input("Salário", 2000.0, 6000.0, 2000.0)
rv = st.sidebar.number_input("RV", 0.0, 10000.0, 1000.0)

# ✅ NOVO BOTÃO VT
usa_vt = st.sidebar.checkbox("Utiliza Vale Transporte (6%)?", value=True)

st.sidebar.markdown("### 🎯 Metas")
meta_individual = st.sidebar.number_input("Meta Individual %", 0.0, 200.0, 100.0)
meta_mesa = st.sidebar.number_input("Meta Mesa %", 0.0, 200.0, 100.0)
meta_operacao = st.sidebar.number_input("Meta Operação %", 0.0, 200.0, 100.0)

st.sidebar.markdown("### ⚡ Ineficiência")
ineficiencia = st.sidebar.number_input("Ineficiência %", 0.0, 100.0, 30.0)

# =========================
# FUNÇÕES
# =========================

def regua_meta(v):
    if v < 55: return 0
    elif v < 60: return 10
    elif v < 65: return 20
    elif v < 70: return 30
    elif v < 75: return 40
    elif v < 80: return 50
    elif v < 85: return 60
    elif v < 90: return 70
    elif v < 95: return 80
    elif v < 100: return 90
    elif v < 110: return 100
    elif v < 120: return 110
    elif v < 130: return 120
    elif v < 140: return 130
    elif v < 150: return 140
    else: return 150

def regua_inef(e):
    faixas = [0,10,15,20,30,40,50,60,70,80,90,100]
    limites = [80,82,84,86,88,90,92,94,96,98,100]

    for i, limite in enumerate(limites):
        if e < limite:
            return faixas[i], faixas[min(i+1, len(faixas)-1)]
    return 100, 100

# =========================
# CÁLCULOS
# =========================

meta_ind = regua_meta(meta_individual)
meta_mesa_val = regua_meta(meta_mesa)
meta_operacao_val = regua_meta(meta_operacao)

eficiencia = 100 - ineficiencia
bonus, proximo_bonus = regua_inef(eficiencia)

percentual = (
    (meta_ind * 0.5) +
    (meta_mesa_val * 0.3) +
    (meta_operacao_val * 0.1)
) + bonus

percentual = percentual / 100
rv_final = rv * percentual

# =========================
# DESCONTOS
# =========================

inss = salario * 0.14
irpf = (salario - inss) * 0.15 if salario > 2112 else 0

# ✅ VT condicional
vt = salario * 0.06 if usa_vt else 0

salario_liquido = salario - inss - irpf - vt + rv_final

# =========================
# KPIs
# =========================

st.markdown('<div class="section-title">Resumo</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Salário", f"R$ {salario:.2f}")
col2.metric("RV Final", f"R$ {rv_final:.2f}")
col3.metric("% Final", f"{percentual*100:.1f}%")
col4.metric("Salário Líquido", f"R$ {salario_liquido:.2f}")

# =========================
# DESCONTOS
# =========================

st.markdown('<div class="section-title">Descontos</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
col1.metric("INSS", f"R$ {inss:.2f}")
col2.metric("IRPF", f"R$ {irpf:.2f}")
col3.metric("VT", f"R$ {vt:.2f}")

# =========================
# GRÁFICO
# =========================

st.markdown('<div class="section-title">Performance</div>', unsafe_allow_html=True)

fig_bar = go.Figure()

fig_bar.add_trace(go.Bar(
    x=["Individual", "Mesa", "Operação", "Eficiência"],
    y=[meta_ind, meta_mesa_val, meta_operacao_val, bonus],
    marker=dict(color=["#00A868","#3B82F6","#F59E0B","#EF4444"]),
    hovertemplate="<b>%{x}</b><br>%{y}%<extra></extra>"
))

fig_bar.update_layout(
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(color="#111827")
)

st.plotly_chart(fig_bar, use_container_width=True)

# =========================
# PIZZA
# =========================

st.markdown('<div class="section-title">Distribuição Financeira</div>', unsafe_allow_html=True)

fig_pizza = go.Figure(data=[go.Pie(
    labels=["INSS","IRPF","VT","RV"],
    values=[inss, irpf, vt, rv_final],
    hole=0.55
)])

fig_pizza.update_layout(
    paper_bgcolor="white",
    font=dict(color="#111827")
)

st.plotly_chart(fig_pizza, use_container_width=True)

# =========================
# IMPACTO
# =========================

st.markdown('<div class="section-title">Impacto da Ineficiência</div>', unsafe_allow_html=True)

diferenca_bonus = (proximo_bonus - bonus) / 100
perda = rv * diferenca_bonus

if perda > 0:
    st.error(f"Você deixou de ganhar R$ cuidado com sua ineficiência!")
else:
    st.success("Você manteve uma boa meta de ineficiência! Continue assim =D")
