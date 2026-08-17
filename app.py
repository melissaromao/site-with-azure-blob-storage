import io
from PIL import Image
import streamlit as st
from azure.storage.blob import BlobServiceClient

AZURE_CONNECTION_STRING = "CONNECTION_STRING"
CONTAINER_NAME = "NAME"

st.set_page_config(page_title="Galeria Azure Blob", layout="wide")

st.markdown("""
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    div[data-testid="stImage"] img { border-radius: 8px; object-fit: cover; }
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_container_client():
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
    
    if not container_client.exists():
        container_client.create_container()
        
    return container_client

try:
    container_client = get_container_client()
except Exception as e:
    st.error(f"Erro ao conectar ao Azure Blob Storage: {e}")
    st.stop()

st.title("Galeria Blob Storage")
st.caption("Upload, listagem e download de imagens no Azure")
st.divider()

st.subheader("1. Fazer Upload de Imagem")
uploaded_file = st.file_uploader("Escolha uma imagem (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    if st.button("Enviar para o Azure", type="primary"):
        with st.spinner("Enviando..."):
            blob_client = container_client.get_blob_client(uploaded_file.name)
            blob_client.upload_blob(uploaded_file.getvalue(), overwrite=True)
            st.success(f"Imagem '{uploaded_file.name}' enviada com sucesso!")
            st.rerun()

st.divider()

st.subheader("2. Galeria de Imagens")

try:
    blobs = list(container_client.list_blobs())

    if not blobs:
        st.info("Nenhuma imagem encontrada no container.")
    else:
        cols = st.columns(4)
        
        for index, blob in enumerate(blobs):
            col = cols[index % 4]
            
            blob_client = container_client.get_blob_client(blob.name)
            image_data = blob_client.download_blob().readall()
            
            with col:
                image = Image.open(io.BytesIO(image_data))
                st.image(image, use_container_width=True)
                st.caption(f"**{blob.name}**")
                
                st.download_button(
                    label="⬇ Baixar",
                    data=image_data,
                    file_name=blob.name,
                    mime=f"image/{blob.name.split('.')[-1]}",
                    key=f"dl_{blob.name}_{index}"
                )
                st.write("")

except Exception as e:
    st.error(f"Erro ao listar arquivos: {e}")