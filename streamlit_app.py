import streamlit as st
import pandas as pd
import csv
from datetime import date
import os

# Configurações da Página
st.set_page_config(page_title="Relatório Diário do Gerente", page_icon="📋", layout="centered")

PERGUNTAS_FILE = "perguntas.csv"
RESPOSTAS_FILE = "respostas.csv"

def carregar_perguntas():
    if os.path.exists(PERGUNTAS_FILE):
        return pd.read_csv(PERGUNTAS_FILE)
    else:
        # Fallback caso o arquivo não exista
        return pd.DataFrame([{"id": "0", "pergunta": "Exemplo: Como foi o movimento?", "tipo": "texto"}])

def salvar_resposta(respostas):
    hoje = date.today().isoformat()
    dados = {"Data": hoje}
    dados.update(respostas)
    
    arquivo_existe = os.path.exists(RESPOSTAS_FILE)
    
    # Nota: Em ambientes de nuvem (como Streamlit Cloud), arquivos salvos localmente são temporários.
    # Para persistência real, recomenda-se usar uma base de dados ou Google Sheets.
    with open(RESPOSTAS_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=dados.keys())
        if not arquivo_existe:
            writer.writeheader()
        writer.writerow(dados)

def gerar_texto_whatsapp(respostas):
    hoje = date.today().strftime("%d/%m/%Y")
    texto = f"*📋 Relatório Diário – {hoje}*\n\n"
    for chave, valor in respostas.items():
        if valor: # Só adiciona se houver resposta
            texto += f"• *{chave}:* {valor}\n"
    return texto

# --- Interface ---

st.header("📋 Relatório Diário do Gerente")
st.write("Preencha as informações abaixo para gerar o relatório do dia.")

df_perguntas = carregar_perguntas()
respostas_form = {}

with st.form("relatorio_form"):
    for _, row in df_perguntas.iterrows():
        pergunta = row['pergunta']
        tipo = row.get('tipo', 'texto')
        
        if tipo == 'numero':
            respostas_form[pergunta] = st.number_input(pergunta, min_value=0, step=1)
        else:
            respostas_form[pergunta] = st.text_area(pergunta, placeholder="Digite sua resposta aqui...")
    
    submit = st.form_submit_button("Gerar Relatório e Salvar")

if submit:
    try:
        # Salva no CSV local
        salvar_respostas_dict = {p: r for p, r in respostas_form.items()}
        salvar_resposta(salvar_respostas_dict)
        
        # Gera texto para WhatsApp
        texto_wa = gerar_texto_whatsapp(respostas_form)
        
        st.success("✅ Relatório salvo com sucesso!")
        
        st.subheader("📱 Texto para WhatsApp")
        st.info("Copie o texto abaixo e cole no WhatsApp do grupo.")
        st.code(texto_wa, language="markdown")
        
        # Botão para facilitar cópia (Streamlit tem ícone de cópia no bloco de código acima)
        st.balloons()
        
    except Exception as e:
        st.error(f"Erro ao processar relatório: {e}")

# Rodapé ou Informações Adicionais
st.markdown("---")
st.caption("Desenvolvido para Relatório de Gestão - Acesso Remoto")
