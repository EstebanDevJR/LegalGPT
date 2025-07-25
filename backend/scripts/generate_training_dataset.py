#!/usr/bin/env python3
"""
🎯 Script para Generar Dataset de Fine-Tuning LegalGPT

Este script genera un dataset completo de alta calidad para entrenar
un modelo GPT-4o-mini especializado en asesoría legal para PyMEs colombianas.

Uso:
    python backend/scripts/generate_training_dataset.py [--complete] [--interactive]
    
Opciones:
    --complete: Genera respuestas automáticamente usando el RAG actual
    --interactive: Permite revisar y editar cada respuesta manualmente
"""

import os
import sys
import json
import asyncio
import argparse
from pathlib import Path
from typing import Dict, Any, List

# Agregar backend al path
sys.path.append(str(Path(__file__).parent.parent))

# Importar solo lo necesario (sin auth_service que tiene problemas de dependencias)
from services.fine_tuning_service import FineTuningService

class DatasetGenerator:
    """Generador de datasets de entrenamiento de alta calidad"""
    
    def __init__(self):
        self.output_dir = Path("backend/data/fine_tuning")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.fine_tuning_service = FineTuningService()
        
        # Inicializar RAG service manualmente para evitar problemas de imports
        try:
            from services.rag_service import RAGService
            self.rag_service = RAGService()
            print("✅ RAG service inicializado correctamente")
        except Exception as e:
            print(f"⚠️ RAG service no disponible: {e}")
            self.rag_service = None
        
    def get_additional_examples(self) -> List[Dict[str, Any]]:
        """Ejemplos adicionales específicos y de alta calidad"""
        
        additional_examples = [
            # === CASOS ESPECÍFICOS DE PYMES ===
            {
                "messages": [
                    {"role": "system", "content": self.fine_tuning_service.system_prompt},
                    {"role": "user", "content": "Soy una microempresa de desarrollo de software, ¿qué régimen tributario me conviene más?"},
                    {"role": "assistant", "content": """**RESPUESTA DIRECTA:**
Como microempresa de desarrollo de software, el Régimen Simple de Tributación es tu mejor opción si facturas menos de $61M anuales, ya que reduces cargas tributarias y simplifica cumplimiento.

**BASE LEGAL:**
- Estatuto Tributario, Art. 908 y ss.
- Decreto 2201 de 2016
- Resolución DIAN 000013 de 2019

**ANÁLISIS PARA SOFTWARE:**

**RÉGIMEN SIMPLE (Recomendado si calificas):**
- Tarifa progresiva: 0% a 9% según ingresos
- Una declaración anual (marzo del año siguiente)
- No retenciones en la fuente como proveedor
- Servicios de software exentos de IVA
- Contabilidad simplificada

**VENTAJAS ESPECÍFICAS PARA SOFTWARE:**
- Exportación de servicios: 0% IVA
- Deducciones por innovación y tecnología
- Régimen de ZoMaC si aplica
- Beneficios Ley 1819 para software

**REQUISITOS A VERIFICAR:**
- Ingresos <1.700 UVT anuales ($61M COP aprox)
- Patrimonio <4.500 UVT
- Máximo 10 empleados
- Una actividad económica principal

**PASOS PRÁCTICOS:**
1. Verificar cumplimiento de requisitos en DIAN
2. Solicitar inclusión en Régimen Simple antes 31 de enero
3. Configurar facturación electrónica
4. Implementar contabilidad simplificada

**ORGANISMOS RELEVANTES:**
- DIAN: Inscripción y seguimiento tributario
- MinTIC: Beneficios sector software"""}
                ]
            },
            
            {
                "messages": [
                    {"role": "system", "content": self.fine_tuning_service.system_prompt},
                    {"role": "user", "content": "¿Puedo contratar empleados remotos desde mi PyME y qué implicaciones laborales tiene?"},
                    {"role": "assistant", "content": """**RESPUESTA DIRECTA:**
Sí puedes contratar empleados remotos desde tu PyME. Aplican las mismas obligaciones laborales que el trabajo presencial, con algunas consideraciones especiales para teletrabajo.

**BASE LEGAL:**
- Ley 1221 de 2008 (Teletrabajo)
- Decreto 884 de 2012
- Ley 2088 de 2021 (Trabajo en casa)
- Código Sustantivo del Trabajo

**MODALIDADES DISPONIBLES:**

**1. TELETRABAJO:**
- Contrato específico de teletrabajo
- Mínimo 50% del tiempo fuera de la empresa
- Auxilios de conectividad obligatorios
- Derecho a desconexión laboral

**2. TRABAJO EN CASA:**
- Modalidad ocasional o temporal
- Mismo contrato laboral vigente
- No requiere auxilios especiales
- Mismas condiciones salariales

**OBLIGACIONES DEL EMPLEADOR:**
- Pagar todas las prestaciones sociales normales
- Afiliar a seguridad social (EPS, ARL, Pensión)
- Proporcionar herramientas de trabajo
- Auxilios de conectividad (teletrabajo)
- Garantizar seguridad y salud en el trabajo

**CONSIDERACIONES ESPECIALES:**
- ARL debe cubrir accidentes en domicilio
- Horarios flexibles permitidos con acuerdo
- Políticas de protección de datos estrictas
- Derecho a capacitación tecnológica

**PASOS PRÁCTICOS:**
1. Definir modalidad (teletrabajo vs trabajo en casa)
2. Modificar contrato o crear anexo específico
3. Establecer auxilios de conectividad
4. Configurar herramientas de comunicación
5. Implementar políticas de seguridad digital

**ORGANISMOS RELEVANTES:**
- MinTrabajo: Regulación de teletrabajo
- ARL: Cobertura en domicilio del trabajador"""}
                ]
            },

            # === COMERCIO ELECTRÓNICO ===
            {
                "messages": [
                    {"role": "system", "content": self.fine_tuning_service.system_prompt},
                    {"role": "user", "content": "Tengo una tienda online como PyME, ¿qué obligaciones legales tengo con mis clientes?"},
                    {"role": "assistant", "content": """**RESPUESTA DIRECTA:**
Como tienda online debes cumplir obligaciones de comercio electrónico, protección al consumidor, tratamiento de datos personales y facturación electrónica obligatoria.

**BASE LEGAL:**
- Ley 527 de 1999 (Comercio electrónico)
- Ley 1480 de 2011 (Estatuto del Consumidor)
- Ley 1581 de 2012 (Protección de datos)
- Decreto 1625 de 2016 (Facturación electrónica)

**OBLIGACIONES PRINCIPALES:**

**1. INFORMACIÓN AL CONSUMIDOR:**
- Datos completos de la empresa (NIT, dirección)
- Descripción clara de productos/servicios
- Precios finales incluyendo impuestos
- Condiciones de entrega y garantías
- Políticas de devolución (5 días hábiles)

**2. FACTURACIÓN ELECTRÓNICA:**
- Obligatoria para todas las ventas
- Sistema validado por DIAN
- Conservación por 5 años
- Envío inmediato al cliente

**3. PROTECCIÓN DE DATOS:**
- Política de tratamiento visible
- Autorización previa para datos personales
- Seguridad en medios de pago
- Derecho de los titulares garantizado

**4. DERECHO DE RETRACTO:**
- 5 días hábiles sin justificación
- Devolución completa del dinero
- Cliente asume costos de devolución
- Excepciones para productos personalizados

**CONSIDERACIONES ESPECIALES:**
- Términos y condiciones claros y visibles
- Medios de pago seguros (PCI DSS)
- Servicio al cliente efectivo
- Registro ante Cámara de Comercio

**PASOS PRÁCTICOS:**
1. Registrar actividad de comercio electrónico
2. Implementar facturación electrónica
3. Crear políticas de tratamiento de datos
4. Establecer proceso de devoluciones
5. Configurar términos y condiciones

**ORGANISMOS RELEVANTES:**
- SIC: Protección al consumidor y competencia
- DIAN: Facturación electrónica y tributario
- Cámara de Comercio: Registro mercantil"""}
                ]
            },

            # === RESTAURANTE PEQUEÑO ===
            {
                "messages": [
                    {"role": "system", "content": self.fine_tuning_service.system_prompt},
                    {"role": "user", "content": "Tengo un restaurante pequeño, ¿qué permisos y licencias necesito para operar legalmente?"},
                    {"role": "assistant", "content": """**RESPUESTA DIRECTA:**
Tu restaurante necesita: registro mercantil, licencia de funcionamiento, concepto sanitario, uso del suelo, bomberos, música (SAYCO), y cumplir normas laborales y tributarias.

**BASE LEGAL:**
- Decreto 1879 de 2008 (Licencias de funcionamiento)
- Resolución 2674 de 2013 (BPM alimentos)
- Ley 232 de 1995 (Funcionamiento establecimientos)
- Código Nacional de Policía

**PERMISOS OBLIGATORIOS:**

**1. REGISTRO MERCANTIL:**
- Cámara de Comercio de tu jurisdicción
- Actividad: Expendio de alimentos
- Renovación anual antes 31 de marzo

**2. LICENCIA DE FUNCIONAMIENTO:**
- Alcaldía local correspondiente
- Incluye concepto de bomberos
- Verificación de uso del suelo
- Vigencia según normativa local

**3. CONCEPTO SANITARIO:**
- Secretaría de Salud del municipio
- Inspección de cocina y área de servicio
- Certificado de manipulación de alimentos
- Renovación anual

**4. PERMISOS ADICIONALES:**
- SAYCO/ACINPRO: Si reproduces música
- Bomberos: Concepto de seguridad
- Planeación: Uso del suelo compatible
- Ambiental: Si genera residuos especiales

**OBLIGACIONES OPERATIVAS:**
- Personal con carnet de manipulación
- Buenas prácticas de manufactura (BPM)
- Control de plagas certificado
- Libro de inspecciones sanitarias

**CONSIDERACIONES ESPECIALES:**
- Zona rosa o centro histórico: permisos adicionales
- Venta de licor: licencia especial de la gobernación
- Terraza o espacio público: permiso de ocupación
- Delivery: registro de domiciliarios en ARL

**PASOS PRÁCTICOS:**
1. Verificar uso del suelo permitido
2. Registrar empresa en Cámara de Comercio
3. Solicitar concepto sanitario
4. Tramitar licencia de funcionamiento
5. Obtener permisos complementarios

**ORGANISMOS RELEVANTES:**
- Alcaldía Local: Licencia de funcionamiento
- Secretaría de Salud: Concepto sanitario
- Cámara de Comercio: Registro mercantil"""}
                ]
            },

            # === EXPORTACIÓN PARA PYMES ===
            {
                "messages": [
                    {"role": "system", "content": self.fine_tuning_service.system_prompt},
                    {"role": "user", "content": "Mi PyME quiere empezar a exportar, ¿qué requisitos legales debo cumplir?"},
                    {"role": "assistant", "content": """**RESPUESTA DIRECTA:**
Para exportar necesitas: registro como exportador ante DIAN, RUT actualizado, certificados de origen, cumplir normas del país destino y obtener incentivos tributarios disponibles.

**BASE LEGAL:**
- Decreto 2685 de 1999 (Régimen de Aduanas)
- Estatuto Tributario (Incentivos exportadores)
- Decreto 390 de 2016 (Procedimientos aduaneros)
- Ley 1876 de 2017 (Sistema Nacional de Innovación Agropecuaria)

**REQUISITOS BÁSICOS:**

**1. REGISTRO COMO EXPORTADOR:**
- Actualizar RUT en DIAN incluyendo actividad exportadora
- Inscribirse en el Registro Nacional de Exportadores
- No requiere autorización previa para la mayoría de productos
- Verificar si el producto requiere licencias especiales

**2. DOCUMENTACIÓN ESENCIAL:**
- Factura comercial en inglés
- Lista de empaque (packing list)
- Certificado de origen (si aplica TLC)
- Declaración de exportación (DEX)
- Documentos específicos según producto

**3. BENEFICIOS TRIBUTARIOS:**
- Exención de IVA en ventas de exportación
- Plan Vallejo: Suspensión aranceles materias primas
- Certificado de reembolso tributario (CERT) si aplica
- Deducción especial del 200% en inversión en activos

**PROCEDIMIENTO DE EXPORTACIÓN:**
1. Contactar agente de aduanas o SIA
2. Preparar mercancía según normas destino
3. Generar documentos de exportación
4. Presentar declaración ante DIAN
5. Coordinar logística de transporte

**CONSIDERACIONES ESPECIALES:**
- Productos agrícolas: ICA certification
- Productos industriales: INVIMA si aplica
- TLC vigentes: Colombia-USA, UE, Pacífico, etc.
- Zona Franca: beneficios adicionales

**ORGANISMOS DE APOYO:**
- ProColombia: Promoción y asesoría
- Bancoldex: Financiamiento exportador
- DIAN: Trámites aduaneros y tributarios
- Cámaras de Comercio: Certificados origen

**PASOS INMEDIATOS:**
1. Actualizar RUT con actividad exportadora
2. Identificar mercados objetivo y TLC aplicables
3. Contactar ProColombia para asesoría
4. Evaluar certificaciones requeridas
5. Establecer alianza con agente de aduanas

**INCENTIVOS DISPONIBLES:**
- Exención IVA (0% en exportaciones)
- CERT: 2.5% del valor FOB en algunos sectores
- Zonas Francas: tarifa especial renta (20%)"""}
                ]
            },

            # === 9 EJEMPLOS ADICIONALES PARA LLEGAR A 50 ===
            
            # 1. FACTURACIÓN ELECTRÓNICA
            {
                "messages": [
                    {"role": "system", "content": self.fine_tuning_service.system_prompt},
                    {"role": "user", "content": "¿Cómo implemento facturación electrónica en mi PyME y es obligatoria?"},
                    {"role": "assistant", "content": """**RESPUESTA DIRECTA:**
La facturación electrónica es obligatoria para todas las empresas en Colombia desde 2019. Debes obtener autorización de DIAN, implementar un sistema certificado y emitir facturas digitales con firma electrónica.

**BASE LEGAL:**
- Decreto 1625 de 2016 (Facturación electrónica)
- Resolución 000042 de 2020 (Implementación)
- Estatuto Tributario, Art. 616-1

**REQUISITOS OBLIGATORIOS:**

**1. AUTORIZACIÓN DIAN:**
- Solicitar habilitación para facturación electrónica
- Presentar certificados de pruebas técnicas
- Cumplir estándares técnicos UBL 2.1
- Obtener numeración autorizada

**2. SISTEMA CERTIFICADO:**
- Software que cumpla anexo técnico DIAN
- Firma digital válida
- Validación en tiempo real
- Conservación por 5 años

**PASOS DE IMPLEMENTACIÓN:**
1. Obtener certificado de firma digital
2. Seleccionar proveedor tecnológico autorizado
3. Realizar pruebas con DIAN (ambiente habilitación)
4. Solicitar autorización de producción
5. Iniciar facturación electrónica obligatoria

**CONSIDERACIONES ESPECIALES:**
- Backup obligatorio de facturas físicas por 6 meses
- Contingencia en caso de fallas técnicas
- Capacitación al personal contable
- Integración con software contable existente

**SANCIONES POR INCUMPLIMIENTO:**
- Multas desde 1% hasta 200% del tributo
- Cierre temporal del establecimiento
- Pérdida de beneficios tributarios

**ORGANISMOS RELEVANTES:**
- DIAN: Autorización y seguimiento
- Proveedores tecnológicos autorizados"""}
                ]
            },

            # 2. PROPIEDAD INTELECTUAL
            {
                "messages": [
                    {"role": "system", "content": self.fine_tuning_service.system_prompt},
                    {"role": "user", "content": "¿Cómo registro mi marca comercial y cuánto cuesta para mi PyME?"},
                    {"role": "assistant", "content": """**RESPUESTA DIRECTA:**
Para registrar tu marca debes presentar solicitud ante la SIC, pagar tasas ($642,000 aprox), superar examen de registrabilidad y obtener registro válido por 10 años renovables.

**BASE LEGAL:**
- Decisión Andina 486 de 2000 (Régimen Común sobre Propiedad Industrial)
- Ley 1648 de 2013 (Protección efectiva de derechos)
- Código de Comercio, Arts. 583-587

**PROCESO DE REGISTRO:**

**1. BÚSQUEDA DE ANTECEDENTES:**
- Verificar marcas similares existentes
- Consulta gratuita en base SIC
- Análisis de riesgo de oposición
- Definir clase internacional (Niza)

**2. PRESENTACIÓN DE SOLICITUD:**
- Formulario oficial SIC
- Poder si usa abogado
- Comprobante de pago de tasas
- Logo en formato específico

**COSTOS DETALLADOS (2024):**
- Solicitud de registro: $642,000 COP
- Búsqueda de antecedentes: $40,000 COP
- Publicación Gaceta: Incluida
- Certificado de registro: $30,000 COP

**PLAZOS DEL PROCESO:**
- Examen formal: 1 mes
- Examen de registrabilidad: 4-6 meses
- Publicación para oposiciones: 30 días
- Registro definitivo: 8-12 meses total

**CONSIDERACIONES ESPECIALES:**
- Vigencia: 10 años renovables
- Uso obligatorio para mantener derechos
- Posible oposición de terceros
- Protección territorial (solo Colombia)

**PASOS PRÁCTICOS:**
1. Realizar búsqueda de antecedentes
2. Preparar documentación completa
3. Presentar solicitud en línea (SIC)
4. Seguimiento durante examen
5. Responder observaciones si las hay

**ORGANISMOS RELEVANTES:**
- SIC: Superintendencia de Industria y Comercio
- Abogados especializados en PI"""}
                ]
            },

            # 3. SEGUROS EMPRESARIALES
            {
                "messages": [
                    {"role": "system", "content": self.fine_tuning_service.system_prompt},
                    {"role": "user", "content": "¿Qué seguros son obligatorios para mi PyME y cuáles son recomendados?"},
                    {"role": "assistant", "content": """**RESPUESTA DIRECTA:**
Los seguros obligatorios son ARL (si tienes empleados) y SOAT (vehículos). Los recomendados incluyen responsabilidad civil, incendio y sustracción, y pólizas profesionales según tu actividad.

**BASE LEGAL:**
- Ley 1562 de 2012 (Sistema de Riesgos Laborales)
- Ley 769 de 2002 (Código Nacional de Tránsito)
- Código de Comercio, Arts. 1036-1194

**SEGUROS OBLIGATORIOS:**

**1. ARL (RIESGOS LABORALES):**
- Obligatorio si tienes empleados
- Cobertura accidentes de trabajo
- Tarifas según clase de riesgo (0.348% a 8.7%)
- Afiliación antes de iniciar labores

**2. SOAT (VEHÍCULOS):**
- Obligatorio para todos los vehículos
- Cobertura lesiones y muerte
- Vigencia anual
- Multas por no tenerlo al día

**SEGUROS RECOMENDADOS:**

**1. RESPONSABILIDAD CIVIL:**
- Protege contra reclamaciones de terceros
- Cubre daños por productos o servicios
- Prima según facturación anual
- Especialmente importante para servicios

**2. INCENDIO Y SUSTRACCIÓN:**
- Protege instalaciones y equipos
- Cubre pérdidas por robo o siniestros
- Suma asegurada según inventario
- Incluye lucro cesante

**3. PÓLIZAS PROFESIONALES:**
- Médicos: Responsabilidad médica
- Ingenieros: Responsabilidad profesional
- Software: Errores y omisiones
- Consultores: Responsabilidad civil profesional

**CONSIDERACIONES ESPECIALES:**
- Evaluar riesgos específicos del sector
- Revisar exclusiones y deducibles
- Actualizar sumas aseguradas anualmente
- Mantener pólizas vigentes

**PASOS PRÁCTICOS:**
1. Evaluar riesgos de tu actividad
2. Cotizar con múltiples aseguradoras
3. Leer condiciones generales
4. Mantener pólizas al día
5. Reportar siniestros oportunamente

**ORGANISMOS RELEVANTES:**
- Fasecolda: Regulación seguros
- ARL: Prevención riesgos laborales
- Superfinanciera: Vigilancia seguros"""}
                ]
            },

            # 4. CRÉDITO EMPRESARIAL
            {
                "messages": [
                    {"role": "system", "content": self.fine_tuning_service.system_prompt},
                    {"role": "user", "content": "¿Cómo accedo a créditos para mi PyME y qué documentos necesito?"},
                    {"role": "assistant", "content": """**RESPUESTA DIRECTA:**
Para acceder a créditos PyME necesitas: estados financieros, flujo de caja proyectado, garantías, RUT y cámara de comercio vigentes. Las tasas van desde DTF+5% hasta 25% EA según el riesgo.

**BASE LEGAL:**
- Ley 1314 de 2009 (Normas contables)
- Ley 590 de 2000 (PyMEs)
- Circular Externa 100 de 1995 (Superfinanciera)

**DOCUMENTOS REQUERIDOS:**

**1. INFORMACIÓN FINANCIERA:**
- Estados financieros últimos 2 años
- Flujo de caja proyectado 12 meses
- Declaración de renta empresarial
- Balance de prueba actualizado
- Relación de deudas existentes

**2. DOCUMENTOS LEGALES:**
- RUT actualizado
- Cámara de comercio vigente
- Cédula representante legal
- Autorización de centrales de riesgo
- Referencias comerciales

**TIPOS DE CRÉDITO DISPONIBLES:**

**1. CAPITAL DE TRABAJO:**
- Financiación operación diaria
- Plazo: 12-36 meses
- Tasa: DTF+8% a 18% EA
- Garantía: Fiduciaria o real

**2. INVERSIÓN (ACTIVOS):**
- Compra de maquinaria/equipos
- Plazo: hasta 10 años
- Tasa: DTF+5% a 15% EA
- Garantía: Hipotecaria sobre bien

**3. MICROCRÉDITO:**
- Montos hasta $350 millones
- Requisitos flexibles
- Tasa: hasta 25% EA
- Garantías: Personales o grupales

**ENTIDADES DISPONIBLES:**
- Bancos comerciales tradicionales
- Bancoldex (redescuento)
- Finagro (sector agro)
- Cooperativas financieras
- Fondo Nacional de Garantías

**CONSEJOS PARA APROBACIÓN:**
- Mantener centrales de riesgo limpias
- Presentar proyecciones realistas
- Tener garantías suficientes
- Demostrar experiencia sector
- Capacidad de pago comprobada

**PASOS PRÁCTICOS:**
1. Preparar documentación completa
2. Cotizar en múltiples entidades
3. Evaluar tasas y condiciones
4. Negociar términos favorables
5. Mantener buena relación bancaria

**ORGANISMOS RELEVANTES:**
- Bancoldex: Financiamiento empresarial
- FNG: Garantías para PyMEs
- Superfinanciera: Vigilancia sector"""}
                ]
            },

            # 5. CONTRATACIÓN CON EL ESTADO
            {
                "messages": [
                    {"role": "system", "content": self.fine_tuning_service.system_prompt},
                    {"role": "user", "content": "¿Cómo puede mi PyME participar en contratación pública del Estado?"},
                    {"role": "assistant", "content": """**RESPUESTA DIRECTA:**
Tu PyME puede contratar con el Estado registrándose en SECOP II, cumpliendo requisitos habilitantes, presentando ofertas en licitaciones y obteniendo el RUP (Registro Único de Proponentes).

**BASE LEGAL:**
- Ley 80 de 1993 (Estatuto General de Contratación)
- Ley 1150 de 2007 (Eficiencia y transparencia)
- Decreto 1082 de 2015 (Decreto Único Reglamentario)

**PROCESO DE HABILITACIÓN:**

**1. REGISTRO ÚNICO DE PROPONENTES (RUP):**
- Inscripción en Cámara de Comercio
- Clasificación por actividades UNSPSC
- Actualización anual obligatoria
- Vigencia: 1 año

**2. REGISTRO SECOP II:**
- Plataforma única de contratación
- Usuario y contraseña personal
- Validación de información RUP
- Alertas de oportunidades

**REQUISITOS HABILITANTES:**

**1. CAPACIDAD JURÍDICA:**
- Empresa legalmente constituida
- Representante legal facultado
- No estar en inhabilidades legales
- Autorización para actividad específica

**2. CAPACIDAD FINANCIERA:**
- Liquidez mínima requerida
- Nivel de endeudamiento aceptable
- Rentabilidad del patrimonio
- Capital de trabajo positivo

**3. CAPACIDAD ORGANIZACIONAL:**
- Experiencia en actividades similares
- Personal técnico calificado
- Equipos y recursos necesarios
- Certificaciones si se requieren

**BENEFICIOS PARA PYMES:**
- Incentivos hasta 20% en evaluación
- Pago de anticipos hasta 50%
- Posibilidad de consorcio/unión temporal
- Programas especiales de acompañamiento

**MODALIDADES DE CONTRATACIÓN:**
- Licitación pública (>$1.000M)
- Selección abreviada ($200M-$1.000M)
- Concurso de méritos (consultoría)
- Contratación directa (casos específicos)

**PASOS PARA PARTICIPAR:**
1. Obtener RUP en Cámara de Comercio
2. Registrarse en SECOP II
3. Buscar oportunidades por sector
4. Preparar propuesta técnica y económica
5. Presentar oferta dentro del plazo

**ORGANISMOS RELEVANTES:**
- Colombia Compra Eficiente: Regulación
- SECOP II: Plataforma de contratación
- Cámaras de Comercio: Expiden RUP"""}
                ]
            },

            # 6. LAVADO DE ACTIVOS (SARLAFT)
            {
                "messages": [
                    {"role": "system", "content": self.fine_tuning_service.system_prompt},
                    {"role": "user", "content": "¿Mi PyME debe implementar sistema SARLAFT y qué obligaciones tengo?"},
                    {"role": "assistant", "content": """**RESPUESTA DIRECTA:**
Si tu PyME maneja transacciones en efectivo superiores a $10 millones mensuales o pertenece a sectores vigilados, debes implementar SARLAFT (prevención lavado de activos) con políticas, procedimientos y reporte de operaciones sospechosas.

**BASE LEGAL:**
- Ley 526 de 1999 (Lavado de activos)
- Decreto 1674 de 2016 (SARLAFT)
- Circular Externa 100 de 1995 (Superfinanciera)

**OBLIGACIONES SEGÚN SECTOR:**

**1. SECTORES OBLIGATORIOS:**
- Entidades financieras (todas)
- Inmobiliarias (transacciones >$3.000M)
- Concesionarios de vehículos
- Casas de cambio y remesas
- Notarios y casinos

**2. EMPRESAS VIGILADAS:**
- Transacciones efectivo >$10M mensuales
- Operaciones internacionales frecuentes
- Sectores de alto riesgo (minería, construcción)
- Manejo de recursos públicos

**COMPONENTES DEL SISTEMA:**

**1. POLÍTICAS Y PROCEDIMIENTOS:**
- Manual de políticas SARLAFT
- Procedimientos conocimiento del cliente
- Señales de alerta definidas
- Capacitación al personal

**2. DEBIDA DILIGENCIA:**
- Identificación plena de clientes
- Verificación de información
- Monitoreo transacciones inusuales
- Actualización periódica de datos

**3. REPORTE DE OPERACIONES:**
- ROS: Operaciones sospechosas
- ROI: Operaciones inusuales
- Reportes a UIAF (Unidad de Información)
- Plazos máximos establecidos

**SANCIONES POR INCUMPLIMIENTO:**
- Multas hasta 200 SMMLV
- Suspensión de actividades
- Revocatoria de autorizaciones
- Responsabilidad penal personal

**PASOS DE IMPLEMENTACIÓN:**
1. Evaluar si aplica la obligación
2. Designar oficial de cumplimiento
3. Desarrollar manual de políticas
4. Capacitar todo el personal
5. Implementar sistema de monitoreo

**CONSIDERACIONES ESPECIALES:**
- Conservar documentación 5 años
- Actualizar el sistema anualmente
- Reportar dentro de plazos legales
- Mantener confidencialidad absoluta

**ORGANISMOS RELEVANTES:**
- UIAF: Recibe reportes de operaciones
- Superfinanciera: Vigilancia y control
- Fiscalía: Investigación penal"""}
                ]
            },

            # 7. COMERCIO INTERNACIONAL
            {
                "messages": [
                    {"role": "system", "content": self.fine_tuning_service.system_prompt},
                    {"role": "user", "content": "¿Puedo importar productos para revender y qué trámites debo hacer?"},
                    {"role": "assistant", "content": """**RESPUESTA DIRECTA:**
Sí puedes importar para revender registrándote como importador ante DIAN, obteniendo licencias si aplica, cumpliendo normas técnicas del producto y pagando aranceles e IVA correspondientes.

**BASE LEGAL:**
- Decreto 390 de 2016 (Procedimientos aduaneros)
- Arancel de Aduanas (Decreto 2153 de 2016)
- Resolución 9861 de 2020 (MUISCA)

**PROCESO DE IMPORTACIÓN:**

**1. REGISTRO COMO IMPORTADOR:**
- Actualizar RUT incluyendo actividad importadora
- No requiere autorización previa para mayoría de productos
- Clasificar productos según arancel
- Verificar restricciones o prohibiciones

**2. DOCUMENTOS REQUERIDOS:**
- Factura comercial del exterior
- Lista de empaque (packing list)
- Documento de transporte (BL/AWB)
- Póliza de seguro de transporte
- Certificados exigidos según producto

**COSTOS DE IMPORTACIÓN:**

**1. TRIBUTOS ADUANEROS:**
- Arancel: 0% a 35% según producto
- IVA: 19% sobre base gravable
- ICA: Según municipio de destino
- Sobretasa arancelaria si aplica

**2. GASTOS ADICIONALES:**
- Flete internacional
- Seguro de transporte (mínimo 1.1%)
- Gastos portuarios y almacenaje
- Agente de aduanas
- Inspección física si se requiere

**RESTRICCIONES COMUNES:**
- Registro Sanitario INVIMA (alimentos, cosméticos)
- Licencia de importación (algunos productos)
- Normas técnicas ICONTEC
- Vistos buenos de entidades (ICA, ANLA)

**PROCEDIMIENTO EN PUERTO:**
1. Llegada de mercancía
2. Presentar declaración de importación
3. Pago de tributos aduaneros
4. Inspección física si se ordena
5. Retiro de mercancía nacionalizada

**CONSIDERACIONES ESPECIALES:**
- TLC pueden reducir aranceles
- Origen de mercancía afecta tributación
- Regímenes especiales (Plan Vallejo)
- Control cambiario para pagos

**PASOS PRÁCTICOS:**
1. Identificar proveedor internacional confiable
2. Clasificar arancelaria del producto
3. Calcular costos totales de importación
4. Contactar agente de aduanas
5. Coordinar logística y documentos

**ORGANISMOS RELEVANTES:**
- DIAN: Control aduanero y tributario
- INVIMA: Registro sanitario productos
- ICA: Productos agropecuarios
- Agentes de aduanas autorizados"""}
                ]
            },

            # 8. FRANQUICIAS
            {
                "messages": [
                    {"role": "system", "content": self.fine_tuning_service.system_prompt},
                    {"role": "user", "content": "¿Puedo abrir una franquicia como PyME y qué obligaciones legales tengo?"},
                    {"role": "assistant", "content": """**RESPUESTA DIRECTA:**
Sí puedes operar una franquicia como PyME. Debes firmar contrato de franquicia, cumplir estándares del franquiciador, pagar regalías establecidas y mantener la operación según el modelo de negocio acordado.

**BASE LEGAL:**
- Código de Comercio (contratos mercantiles)
- Ley 256 de 1996 (Competencia desleal)
- SIC: Regulación marcas y competencia

**ELEMENTOS DEL CONTRATO:**

**1. DERECHOS DEL FRANQUICIADO:**
- Uso de marca y know-how
- Territorio exclusivo o compartido
- Capacitación inicial y permanente
- Asistencia técnica y comercial
- Manuales de operación

**2. OBLIGACIONES DEL FRANQUICIADO:**
- Pago de canon inicial (fee)
- Regalías mensuales (3%-15% ventas)
- Inversión inicial según estándares
- Cumplimiento de protocolos
- Confidencialidad información

**ASPECTOS LEGALES IMPORTANTES:**

**1. ANÁLISIS DEL CONTRATO:**
- Duración y renovación
- Causales de terminación
- Cláusulas de no competencia
- Territorio de operación
- Transferencia de derechos

**2. PROTECCIÓN LEGAL:**
- Revisar estados financieros del franquiciador
- Verificar registro de marca vigente
- Evaluar experiencia y trayectoria
- Consultar otros franquiciados
- Asesoría jurídica especializada

**CONSIDERACIONES FINANCIERAS:**
- Canon inicial: $50M - $500M COP
- Regalías: 3% - 15% ventas netas
- Fondo publicidad: 1% - 3% ventas
- Inversión total: Según sector
- ROI esperado: 15% - 25% anual

**SECTORES POPULARES:**
- Comidas rápidas y restaurantes
- Retail y tiendas especializadas
- Servicios de belleza y salud
- Educación y capacitación
- Servicios empresariales

**PASOS ANTES DE DECIDIR:**
1. Evaluar capacidad financiera
2. Investigar el franquiciador a fondo
3. Hablar con otros franquiciados
4. Analizar el mercado local
5. Revisar contrato con abogado

**ALERTAS DE RIESGO:**
- Promesas de ganancias garantizadas
- Presión para firmar rápidamente
- Falta de información financiera
- No permitir hablar con otros franquiciados
- Términos contractuales muy rígidos

**ORGANISMOS RELEVANTES:**
- SIC: Protección al consumidor
- Cámaras de Comercio: Registro empresarial
- Asociación Colombiana de Franquicias"""}
                ]
            },

            # 9. MANEJO DE RESIDUOS
            {
                "messages": [
                    {"role": "system", "content": self.fine_tuning_service.system_prompt},
                    {"role": "user", "content": "¿Qué obligaciones ambientales tiene mi PyME con el manejo de residuos?"},
                    {"role": "assistant", "content": """**RESPUESTA DIRECTA:**
Tu PyME debe clasificar residuos (ordinarios, reciclables, peligrosos), contratar empresa gestora autorizada, llevar registro de generación, implementar programa de gestión integral y obtener permisos según el tipo de residuos.

**BASE LEGAL:**
- Decreto 1076 de 2015 (Sector Ambiente)
- Resolución 0472 de 2017 (Gestión integral de residuos sólidos)
- Ley 1252 de 2008 (Residuos peligrosos)

**CLASIFICACIÓN DE RESIDUOS:**

**1. RESIDUOS ORDINARIOS:**
- Residuos de oficina no reciclables
- Restos de comida y orgánicos
- Disposición con empresa de aseo
- Facturación en servicios públicos

**2. RESIDUOS RECICLABLES:**
- Papel, cartón, plástico, vidrio, metal
- Separación en la fuente obligatoria
- Entrega a recicladores autorizados
- Reporte de aprovechamiento

**3. RESIDUOS PELIGROSOS (RESPEL):**
- Químicos, baterías, aceites usados
- Registro como generador ante autoridad
- Gestión con empresas especializadas
- Manifiestos de entrega obligatorios

**OBLIGACIONES SEGÚN GENERACIÓN:**

**1. PEQUEÑOS GENERADORES (<100 kg/año):**
- Separación básica en la fuente
- Entrega al sistema público de aseo
- Programas de devolución post-consumo
- Sin registro especial requerido

**2. MEDIANOS GENERADORES (100-1000 kg/año):**
- Registro ante autoridad ambiental
- Plan de gestión integral de residuos
- Contratos con gestores autorizados
- Reportes anuales de generación

**PROGRAMA DE GESTIÓN INTEGRAL:**
1. Diagnóstico inicial de generación
2. Minimización y aprovechamiento
3. Separación en la fuente
4. Almacenamiento temporal adecuado
5. Entrega a gestores autorizados

**RESIDUOS ESPECIALES COMUNES:**
- Equipos electrónicos (RAEE)
- Llantas usadas
- Aceites de cocina
- Medicamentos vencidos
- Envases de agroquímicos

**SANCIONES POR INCUMPLIMIENTO:**
- Multas hasta 5.000 SMLDV
- Cierre temporal o definitivo
- Decomiso de productos
- Revocatoria de licencias

**PASOS PRÁCTICOS:**
1. Identificar tipos de residuos generados
2. Calcular cantidades mensuales/anuales
3. Implementar separación en la fuente
4. Contratar gestores autorizados
5. Llevar registros y reportes

**BENEFICIOS DE BUEN MANEJO:**
- Reducción de costos operativos
- Imagen corporativa positiva
- Cumplimiento normativo
- Posibles ingresos por reciclaje

**ORGANISMOS RELEVANTES:**
- ANLA: Licencias ambientales nacionales
- CAR: Autoridades ambientales regionales
- Secretarías de Ambiente municipales"""}
                ]
            }
        ]
        
        return additional_examples

    async def generate_rag_responses(self, questions: List[str]) -> List[Dict[str, Any]]:
        """Generar respuestas usando el sistema RAG actual"""
        examples = []
        
        if not self.rag_service:
            print("⚠️ RAG service no disponible, saltando generación automática")
            return examples
        
        print(f"🤖 Generando respuestas automáticamente para {len(questions)} preguntas...")
        
        for i, question in enumerate(questions, 1):
            print(f"   Procesando {i}/{len(questions)}: {question[:50]}...")
            
            try:
                # Usar el RAG service para generar respuesta
                result = await self.rag_service.query(question)
                
                if result.get("confidence", 0) >= 0.80:  # Umbral más permisivo
                    example = {
                        "messages": [
                            {"role": "system", "content": self.fine_tuning_service.system_prompt},
                            {"role": "user", "content": question},
                            {"role": "assistant", "content": result["answer"]}
                        ]
                    }
                    examples.append(example)
                    print(f"   ✅ Generado (confianza: {result.get('confidence', 0):.2f})")
                else:
                    print(f"   ⚠️ Descartado (baja confianza: {result.get('confidence', 0):.2f})")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
                
        return examples

    def interactive_review(self, examples: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Revisión interactiva de ejemplos"""
        print("\n🔍 MODO INTERACTIVO - Revisión de ejemplos")
        print("Comandos: (a)ceptar, (e)ditar, (s)altar, (q)uit")
        print("-" * 60)
        
        reviewed_examples = []
        
        for i, example in enumerate(examples, 1):
            print(f"\n📄 EJEMPLO {i}/{len(examples)}")
            print(f"❓ PREGUNTA: {example['messages'][1]['content']}")
            print(f"🤖 RESPUESTA: {example['messages'][2]['content'][:200]}...")
            
            while True:
                action = input("\n¿Qué hacer? (a/e/s/q): ").strip().lower()
                
                if action == 'a':  # Aceptar
                    reviewed_examples.append(example)
                    print("✅ Ejemplo aceptado")
                    break
                elif action == 'e':  # Editar
                    print("\n📝 EDITANDO RESPUESTA:")
                    new_response = input("Nueva respuesta (Enter para mantener): ").strip()
                    if new_response:
                        example['messages'][2]['content'] = new_response
                        reviewed_examples.append(example)
                        print("✅ Ejemplo editado y aceptado")
                    else:
                        reviewed_examples.append(example)
                        print("✅ Ejemplo mantenido")
                    break
                elif action == 's':  # Saltar
                    print("⏭️ Ejemplo saltado")
                    break
                elif action == 'q':  # Quit
                    print("🛑 Finalizando revisión interactiva")
                    return reviewed_examples
                else:
                    print("❌ Comando inválido. Usa: a, e, s, o q")
        
        return reviewed_examples

    async def generate_complete_dataset(self, args) -> str:
        """Generar dataset completo con todas las opciones"""
        
        print("🎯 GENERANDO DATASET COMPLETO DE FINE-TUNING")
        print("=" * 60)
        
        all_examples = []
        
        # 1. Ejemplos base curados manualmente
        print("📚 1. Cargando ejemplos base de alta calidad...")
        base_examples = self.fine_tuning_service.generate_training_examples()
        all_examples.extend(base_examples)
        print(f"   ✅ {len(base_examples)} ejemplos base cargados")
        
        # 2. Ejemplos específicos adicionales
        print("🎯 2. Cargando ejemplos específicos de PyMEs...")
        specific_examples = self.get_additional_examples()
        all_examples.extend(specific_examples)
        print(f"   ✅ {len(specific_examples)} ejemplos específicos cargados")
        
        # 3. Generar respuestas automáticamente si se solicita
        if args.complete:
            print("🤖 3. Generando ejemplos automáticamente...")
            template_examples = self.fine_tuning_service.generate_extended_examples()
            
            # Extraer TODAS las preguntas de las plantillas
            questions = [ex['messages'][1]['content'] for ex in template_examples]
            
            print(f"   📝 Encontradas {len(questions)} plantillas para completar...")
            
            # Limitar a las primeras 30 para evitar costos excesivos en la demo
            questions_to_process = questions[:30]  
            
            auto_examples = await self.generate_rag_responses(questions_to_process)
            all_examples.extend(auto_examples)
            print(f"   ✅ {len(auto_examples)} ejemplos generados automáticamente")
        
        # 4. Revisión interactiva si se solicita
        if args.interactive:
            all_examples = self.interactive_review(all_examples)
        
        # 5. Guardar dataset final
        print(f"\n💾 Preparando dataset final con {len(all_examples)} ejemplos...")
        
        filename = f"legalgpt_dataset_{len(all_examples)}_ejemplos.jsonl"
        
        file_path, count = self.fine_tuning_service.prepare_training_dataset(
            all_examples, filename
        )
        
        # 6. Estadísticas finales
        print("\n📊 ESTADÍSTICAS DEL DATASET:")
        print(f"   📁 Archivo: {file_path}")
        print(f"   📊 Total ejemplos: {count}")
        print(f"   🎯 Ejemplos base: {len(base_examples)}")
        print(f"   🔥 Ejemplos específicos: {len(specific_examples)}")
        
        if args.complete:
            print(f"   🤖 Ejemplos auto-generados: {len(auto_examples) if 'auto_examples' in locals() else 0}")
        
        # Calcular distribución por categorías
        categories = {}
        for example in all_examples:
            content = example['messages'][1]['content'].lower()
            if 'sas' in content or 'constituir' in content:
                categories['Constitución'] = categories.get('Constitución', 0) + 1
            elif 'laboral' in content or 'empleado' in content:
                categories['Laboral'] = categories.get('Laboral', 0) + 1
            elif 'tributario' in content or 'impuesto' in content:
                categories['Tributario'] = categories.get('Tributario', 0) + 1
            elif 'contrato' in content:
                categories['Contractual'] = categories.get('Contractual', 0) + 1
            else:
                categories['General'] = categories.get('General', 0) + 1
        
        print(f"\n📈 DISTRIBUCIÓN POR CATEGORÍAS:")
        for category, count in categories.items():
            print(f"   {category}: {count} ejemplos")
        
        print(f"\n💰 COSTO ESTIMADO: $3-8 USD")
        print(f"🚀 MEJORA ESPERADA: 20-30% en precisión legal")
        
        return file_path

async def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Generar dataset de fine-tuning para LegalGPT')
    parser.add_argument('--complete', action='store_true', 
                       help='Generar respuestas automáticamente usando RAG')
    parser.add_argument('--interactive', action='store_true',
                       help='Revisión interactiva de ejemplos')
    
    args = parser.parse_args()
    
    print("🎯 GENERADOR DE DATASET FINE-TUNING - LegalGPT")
    print("Especializado en PyMEs colombianas")
    print("=" * 60)
    
    generator = DatasetGenerator()
    
    try:
        file_path = await generator.generate_complete_dataset(args)
        
        print(f"\n✨ DATASET GENERADO EXITOSAMENTE!")
        print(f"📁 Ubicación: {file_path}")
        
        print(f"\n🔥 PRÓXIMOS PASOS:")
        print(f"1. POST /fine-tuning/start")
        print(f"2. Monitorear con /fine-tuning/status/{{job_id}}")
        print(f"3. Integrar modelo entrenado al RAG")
        print(f"4. ¡Disfrutar mejores respuestas legales!")
        
    except Exception as e:
        print(f"❌ Error generando dataset: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 