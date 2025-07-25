import os
import sys
import glob
from typing import List, Dict
import hashlib
import re
import openai
from time import sleep

# Agregar el directorio parent al path para importar config
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import PINECONE_API_KEY, PINECONE_INDEX_NAME, OPENAI_API_KEY, validate_config
from services.pdf_parser import LegalPDFParser

# Validar configuración antes de continuar
validate_config()

# Inicializar clientes - híbrido: API directa para admin, LangChain para vectorstore
try:
    from pinecone import Pinecone, ServerlessSpec
    from langchain_pinecone import PineconeVectorStore
    from langchain_openai import OpenAIEmbeddings
    
    # Cliente directo para operaciones administrativas
    pc = Pinecone(api_key=PINECONE_API_KEY)
    print("✅ Pinecone (híbrido) inicializado correctamente")
except ImportError as e:
    print(f"⚠️ No se pudo importar Pinecone: {e}")
    print("🔄 Funciones de vectorstore deshabilitadas")
    pc = None
openai.api_key = OPENAI_API_KEY

index_name = PINECONE_INDEX_NAME

# Crear índice regular (no automático)  - Necesita API directa
if pc and pc.has_index(index_name):
    # Verificar y recrear índice si tiene dimensiones incorrectas
    try:
        index_stats = pc.describe_index(index_name)
        if index_stats.dimension != 1536:
            print(f"🗑️ Eliminando índice existente con dimensión incorrecta ({index_stats.dimension})")
            pc.delete_index(index_name)
            sleep(5)  # Esperar a que se elimine completamente
            
            pc.create_index(
                name=index_name,
                dimension=1536,  # Dimensión para text-embedding-3-small
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
            print(f"✅ Índice '{index_name}' recreado con dimensión correcta")
        else:
            print(f"✅ Usando índice existente '{index_name}' con dimensión correcta")
    except Exception as e:
        print(f"Error verificando índice: {e}")
        print(f"✅ Usando índice existente '{index_name}'")
elif pc:
    pc.create_index(
        name=index_name,
        dimension=1536,  # Dimensión para text-embedding-3-small
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )
    print(f"✅ Índice '{index_name}' creado exitosamente")

# Configurar index - híbrido
if pc:
    # Esperar a que el índice esté listo
    sleep(2)
    index = pc.Index(index_name)  # Para operaciones administrativas
else:
    index = None
    print("⚠️ API directa de Pinecone no disponible")


def get_vectorstore():
    """Crear vectorstore usando langchain-pinecone"""
    try:
        embeddings = OpenAIEmbeddings(
            openai_api_key=OPENAI_API_KEY,
            model="text-embedding-3-small"
        )
        
        vectorstore = PineconeVectorStore(
            index_name=index_name,
            embedding=embeddings,
            pinecone_api_key=PINECONE_API_KEY,
            text_key="chunk_text"  # Los datos están en el campo chunk_text, no text
        )
        return vectorstore
    except Exception as e:
        print(f"Error creando vectorstore: {e}")
        return None


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Divide el texto en chunks con overlap para mantener contexto.
    Trata de cortar en puntos naturales como puntos finales.
    """
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Si no es el último chunk, trata de encontrar un punto final cercano
        if end < len(text):
            # Busca el último punto final en los últimos 200 caracteres del chunk
            search_start = max(start + chunk_size - 200, start)
            last_period = text.rfind('.', search_start, end)
            
            if last_period > start:
                end = last_period + 1
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Siguiente chunk comienza con overlap
        start = end - overlap
        
        # Evita chunks muy pequeños al final
        if start >= len(text) - overlap:
            break
    
    return chunks


def read_legal_files() -> Dict[str, str]:
    """Lee todos los archivos de texto y PDF de la carpeta data"""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    files_content = {}
    
    # Procesar archivos TXT
    txt_files = glob.glob(os.path.join(data_dir, "*.txt"))
    for file_path in txt_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                filename = os.path.basename(file_path)
                files_content[filename] = content
                print(f"✓ Leído TXT {filename}: {len(content)} caracteres")
        except Exception as e:
            print(f"✗ Error leyendo {file_path}: {e}")
    
    # Procesar archivos PDF
    pdf_files = glob.glob(os.path.join(data_dir, "*.pdf"))
    if pdf_files:
        print(f"\n🔄 Procesando {len(pdf_files)} archivos PDF...")
        pdf_parser = LegalPDFParser()
        
        for file_path in pdf_files:
            try:
                filename = os.path.basename(file_path)
                print(f"📄 Extrayendo texto de {filename}...")
                
                result = pdf_parser.extract_text_from_pdf(file_path)
                if result['success']:
                    files_content[filename] = result['text']
                    print(f"✓ Extraído PDF {filename}: {result['pages']} páginas, {len(result['text'])} caracteres")
                else:
                    print(f"✗ Error extrayendo {filename}: {result.get('error', 'Error desconocido')}")
            
            except Exception as e:
                print(f"✗ Error procesando PDF {file_path}: {e}")
    
    return files_content


def clean_text(text: str) -> str:
    """Limpia el texto eliminando espacios extra y caracteres problemáticos"""
    # Normalizar espacios en blanco
    text = re.sub(r'\s+', ' ', text)
    # Eliminar líneas vacías múltiples
    text = re.sub(r'\n\s*\n', '\n\n', text)
    return text.strip()


def determine_document_type(filename: str) -> str:
    """Determina el tipo de documento legal basado en el nombre del archivo"""
    filename_lower = filename.lower()
    
    # Códigos principales
    if "civil" in filename_lower:
        return "codigo_civil"
    elif "comercio" in filename_lower:
        return "codigo_comercio"  
    elif "tributario" in filename_lower:
        return "estatuto_tributario"
    elif "trabajo" in filename_lower or "sustantivo" in filename_lower:
        return "codigo_trabajo"
    
    # Leyes específicas
    elif "1480" in filename or ("consumidor" in filename_lower and "proteccion" in filename_lower):
        return "ley_proteccion_consumidor"
    elif "1581" in filename or ("datos" in filename_lower and "personales" in filename_lower):
        return "ley_proteccion_datos"
    
    # Fallback genérico
    else:
        return "legal"


def generate_chunk_id(filename: str, chunk_index: int, chunk_text: str) -> str:
    """Genera un ID único para cada chunk"""
    content_hash = hashlib.md5(chunk_text.encode()).hexdigest()[:8]
    return f"{filename}_{chunk_index}_{content_hash}"


def prepare_chunks_for_upload(files_content: Dict[str, str]) -> List[Dict]:
    """Prepara los chunks con metadatos para subir a Pinecone"""
    all_chunks = []
    
    for filename, content in files_content.items():
        print(f"\n📄 Procesando {filename}...")
        
        # Limpiar el texto
        cleaned_content = clean_text(content)
        
        # Dividir en chunks
        chunks = chunk_text(cleaned_content)
        print(f"   Creados {len(chunks)} chunks")
        
        # Preparar cada chunk con metadatos
        for i, chunk in enumerate(chunks):
            chunk_id = generate_chunk_id(filename, i, chunk)
            
            # Determinar el tipo de documento
            doc_type = determine_document_type(filename)
            
            chunk_data = {
                "id": chunk_id,
                "values": [],  # Se llenará con el embedding
                "metadata": {
                    "chunk_text": chunk,
                    "filename": filename,
                    "chunk_index": i,
                    "document_type": doc_type,
                    "chunk_length": len(chunk)
                }
            }
            all_chunks.append(chunk_data)
    
    return all_chunks


def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """Genera embeddings usando OpenAI"""
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=texts
        )
        return [embedding.embedding for embedding in response.data]
    except Exception as e:
        print(f"Error generando embeddings: {e}")
        return []


def upload_chunks_to_pinecone(chunks: List[Dict], batch_size: int = 50):
    """Sube los chunks a Pinecone usando langchain-pinecone"""
    print(f"\n🚀 Subiendo {len(chunks)} chunks a Pinecone...")
    
    # Crear vectorstore usando langchain-pinecone
    vectorstore = get_vectorstore()
    if not vectorstore:
        print("❌ No se pudo crear el vectorstore")
        return
    
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        
        try:
            # Preparar documentos para langchain
            from langchain_core.documents import Document
            
            documents = []
            ids = []
            
            for chunk in batch:
                # Crear documento LangChain
                doc = Document(
                    page_content=chunk["metadata"]["chunk_text"],
                    metadata={
                        "filename": chunk["metadata"]["filename"],
                        "chunk_index": chunk["metadata"]["chunk_index"],
                        "document_type": chunk["metadata"]["document_type"],
                        "chunk_length": chunk["metadata"]["chunk_length"]
                    }
                )
                documents.append(doc)
                ids.append(chunk["id"])
            
            # Subir usando langchain-pinecone
            print(f"   🔮 Subiendo lote {i//batch_size + 1}...")
            vectorstore.add_documents(documents=documents, ids=ids)
            print(f"   ✓ Lote {i//batch_size + 1}: {len(documents)} chunks subidos")
            
            # Pequeña pausa para evitar rate limits
            sleep(0.1)
            
        except Exception as e:
            print(f"   ✗ Error subiendo lote {i//batch_size + 1}: {e}")
    
    print("\n✅ Upload completado!")


def upload_legal_documents():
    """Función principal para subir todos los documentos legales"""
    print("🔄 Iniciando proceso de upload de documentos legales...\n")
    
    try:
        # 1. Leer archivos
        files_content = read_legal_files()
        if not files_content:
            print("❌ No se encontraron archivos para procesar")
            return
        
        # 2. Preparar chunks
        chunks = prepare_chunks_for_upload(files_content)
        
        # 3. Subir a Pinecone
        upload_chunks_to_pinecone(chunks)
        
        # 4. Mostrar estadísticas
        print(f"\n📊 Estadísticas:")
        print(f"   - Archivos procesados: {len(files_content)}")
        print(f"   - Total de chunks: {len(chunks)}")
        
        # Estadísticas por documento
        for filename in files_content.keys():
            doc_chunks = [c for c in chunks if c["metadata"]["filename"] == filename]
            print(f"   - {filename}: {len(doc_chunks)} chunks")
        
    except Exception as e:
        print(f"❌ Error en el proceso: {e}")


def query_similar_chunks(query: str, top_k: int = 5, document_type: str = None) -> List[Dict]:
    """Busca chunks similares a la consulta usando embeddings de OpenAI"""
    try:
        # Generar embedding para la consulta
        query_embeddings = generate_embeddings([query])
        if not query_embeddings:
            print("Error generando embedding para la consulta")
            return []
        
        # Construir filtros si se especifica tipo de documento
        filter_dict = {}
        if document_type:
            filter_dict["document_type"] = document_type
        
        # Realizar la búsqueda
        results = index.query(
            vector=query_embeddings[0],  # Embedding de la consulta
            top_k=top_k,
            include_metadata=True,
            filter=filter_dict if filter_dict else None
        )
        
        return results.matches
    
    except Exception as e:
        print(f"Error en la consulta: {e}")
        return []


if __name__ == "__main__":
    upload_legal_documents()


