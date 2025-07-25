#!/usr/bin/env python3
"""
📊 Data Processor - LegalGPT Fine-Tuning

Procesador de datos para generar ejemplos de entrenamiento
de alta calidad para el fine-tuning de modelos legales.
"""

import asyncio
from typing import Dict, Any, List, Optional
from pathlib import Path

class DataProcessor:
    """Procesador de datos de entrenamiento"""
    
    def __init__(self):
        self.legal_categories = {
            "civil": "Derecho civil y personal",
            "comercial": "Derecho comercial y empresarial", 
            "laboral": "Derecho laboral y empleo",
            "tributario": "Derecho tributario y fiscal"
        }
    
    def get_base_examples(self) -> List[Dict[str, Any]]:
        """Obtiene ejemplos base de alta calidad"""
        
        return [
            {
                "messages": [
                    {"role": "system", "content": "Eres un experto en derecho colombiano especializado en asesoría legal para PyMEs."},
                    {"role": "user", "content": "¿Cómo constituyo una SAS en Colombia?"},
                    {"role": "assistant", "content": "Para constituir una SAS (Sociedad por Acciones Simplificada) en Colombia:\n\n1. **Documento privado**: Se constituye mediante documento privado autenticado ante notario o cámara de comercio\n2. **Registro mercantil**: Inscripción en el registro mercantil de la cámara de comercio\n3. **Capital mínimo**: No requiere capital mínimo\n4. **Socios**: Puede tener de 1 a 200 accionistas\n5. **Responsabilidad**: Los socios responden hasta el monto de sus aportes\n\n**Documentos necesarios**:\n- Documento de constitución\n- Estatutos sociales\n- Formulario RUES\n- Pago de derechos de matrícula\n\nLa SAS es ideal para PyMEs por su flexibilidad y facilidad de constitución."}
                ],
                "category": "comercial",
                "confidence": 0.95,
                "complexity": "medium"
            },
            {
                "messages": [
                    {"role": "system", "content": "Eres un experto en derecho colombiano especializado en asesoría legal para PyMEs."},
                    {"role": "user", "content": "¿Cuáles son las obligaciones laborales básicas de una microempresa?"},
                    {"role": "assistant", "content": "Las obligaciones laborales básicas para una microempresa en Colombia incluyen:\n\n**1. Contratos de trabajo**:\n- Contrato escrito dentro de los primeros 15 días\n- Periodo de prueba máximo 2 meses\n- Especificar funciones, salario y jornada\n\n**2. Prestaciones sociales**:\n- Prima de servicios (junio y diciembre)\n- Cesantías e intereses sobre cesantías\n- Vacaciones (15 días hábiles por año)\n\n**3. Seguridad social**:\n- Afiliación a EPS (salud)\n- Afiliación a AFP (pensión)\n- ARL (riesgos laborales)\n\n**4. Parafiscales**:\n- SENA (2%)\n- ICBF (3%)\n- Cajas de compensación (4%)\n\n**Para microempresas**: Algunos beneficios y tarifas diferenciales según la Ley de Formalización Empresarial."}
                ],
                "category": "laboral",
                "confidence": 0.98,
                "complexity": "high"
            }
        ]
    
    def get_static_examples(self) -> List[Dict[str, Any]]:
        """Obtiene ejemplos estáticos cuando RAG no está disponible"""
        
        return [
            {
                "messages": [
                    {"role": "system", "content": "Eres un experto en derecho colombiano especializado en asesoría legal para PyMEs."},
                    {"role": "user", "content": "¿Qué régimen tributario me conviene para mi pequeña empresa?"},
                    {"role": "assistant", "content": "Para elegir el régimen tributario adecuado considera:\n\n**Régimen Simple de Tributación (RST)**:\n- Para ingresos hasta 50.000 UVT\n- Tarifa única del 19%\n- Incluye IVA e impuesto de renta\n- Ideal para pequeñas empresas\n\n**Régimen Ordinario**:\n- Para ingresos superiores a 50.000 UVT\n- Tarifa del 35% sobre utilidades\n- Mayor control tributario\n- Más beneficios deducibles\n\n**Recomendación**: Para PyMEs nuevas, el RST suele ser más conveniente por su simplicidad administrativa y menor carga fiscal inicial."}
                ],
                "category": "tributario",
                "confidence": 0.92,
                "complexity": "medium"
            }
        ]
    
    async def generate_rag_examples(self, rag_service, interactive: bool = False) -> List[Dict[str, Any]]:
        """
        Genera ejemplos usando el servicio RAG actual
        
        Args:
            rag_service: Servicio RAG inicializado
            interactive: Si permite revisión manual
            
        Returns:
            Lista de ejemplos generados
        """
        questions = [
            "¿Cómo protejo mi marca comercial?",
            "¿Qué pasos seguir para despedir un empleado?",
            "¿Cómo declaro mis impuestos como persona jurídica?",
            "¿Qué seguros son obligatorios para mi empresa?",
            "¿Cómo redacto un contrato de servicios?",
            "¿Cuáles son mis derechos como empleador?",
            "¿Cómo manejar una demanda laboral?",
            "¿Qué obligaciones tengo con el medio ambiente?"
        ]
        
        examples = []
        
        for question in questions:
            try:
                print(f"🤖 Generando respuesta para: {question}")
                
                # Generar respuesta usando RAG
                result = await rag_service.query(
                    question=question,
                    context="",
                    user_info={"company_type": "pequeña"},
                    user_documents=[]
                )
                
                response = result.get("answer", "")
                
                if interactive:
                    print(f"\nPregunta: {question}")
                    print(f"Respuesta generada: {response[:200]}...")
                    edit = input("¿Editar respuesta? (s/N): ").lower()
                    if edit == 's':
                        response = input("Nueva respuesta: ")
                
                example = {
                    "messages": [
                        {"role": "system", "content": "Eres un experto en derecho colombiano especializado en asesoría legal para PyMEs."},
                        {"role": "user", "content": question},
                        {"role": "assistant", "content": response}
                    ],
                    "category": self._classify_question(question),
                    "confidence": result.get("confidence", 0.8),
                    "complexity": "medium"
                }
                
                examples.append(example)
                
            except Exception as e:
                print(f"❌ Error generando ejemplo para '{question}': {e}")
                continue
        
        return examples
    
    def get_category_examples(self, category: str, count: int) -> List[Dict[str, Any]]:
        """
        Genera ejemplos para una categoría específica
        
        Args:
            category: Categoría legal
            count: Número de ejemplos
            
        Returns:
            Lista de ejemplos de la categoría
        """
        category_questions = {
            "civil": [
                "¿Cómo redacto un contrato de arrendamiento?",
                "¿Qué hago si no me pagan una deuda?",
                "¿Cómo protejo mis datos personales?",
                "¿Qué derechos tengo como consumidor?",
                "¿Cómo demando por daños y perjuicios?"
            ],
            "comercial": [
                "¿Cómo registro mi empresa?",
                "¿Qué tipo de sociedad me conviene?",
                "¿Cómo protejo mi propiedad intelectual?",
                "¿Qué obligaciones tengo como comerciante?",
                "¿Cómo manejar competencia desleal?"
            ],
            "laboral": [
                "¿Cómo contratar empleados?",
                "¿Qué prestaciones sociales debo pagar?",
                "¿Cómo manejar una licencia médica?",
                "¿Qué hacer ante un accidente laboral?",
                "¿Cómo implementar trabajo remoto?"
            ],
            "tributario": [
                "¿Cómo calcular mis impuestos?",
                "¿Qué deducciones puedo aplicar?",
                "¿Cómo presentar declaración de renta?",
                "¿Qué hacer ante una auditoría?",
                "¿Cómo optimizar mi carga tributaria?"
            ]
        }
        
        questions = category_questions.get(category, [])[:count]
        examples = []
        
        for question in questions:
            # Generar respuesta básica (en implementación real, usar RAG)
            example = {
                "messages": [
                    {"role": "system", "content": "Eres un experto en derecho colombiano especializado en asesoría legal para PyMEs."},
                    {"role": "user", "content": question},
                    {"role": "assistant", "content": f"Respuesta especializada en {category} para: {question}"}
                ],
                "category": category,
                "confidence": 0.85,
                "complexity": "medium"
            }
            examples.append(example)
        
        return examples
    
    def _classify_question(self, question: str) -> str:
        """Clasifica una pregunta en una categoría legal"""
        
        keywords = {
            "civil": ["contrato", "arrendamiento", "deuda", "consumidor", "daños"],
            "comercial": ["empresa", "sociedad", "marca", "comerciante", "competencia"],
            "laboral": ["empleado", "trabajo", "prestaciones", "licencia", "accidente"],
            "tributario": ["impuesto", "declaración", "deducción", "auditoría", "renta"]
        }
        
        question_lower = question.lower()
        
        for category, terms in keywords.items():
            if any(term in question_lower for term in terms):
                return category
        
        return "general" 