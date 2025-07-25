#!/usr/bin/env python3
"""
✅ Quality Validator - LegalGPT Fine-Tuning

Validador de calidad para datasets de entrenamiento legal.
Asegura que los ejemplos cumplan con estándares de calidad.
"""

import re
from typing import Dict, Any, List, Tuple

class QualityValidator:
    """Validador de calidad para datasets de entrenamiento"""
    
    def __init__(self):
        self.min_response_length = 50
        self.max_response_length = 2000
        self.min_confidence = 0.7
        
        # Patrones de calidad
        self.quality_patterns = {
            "legal_terms": ["artículo", "ley", "código", "decreto", "norma", "jurisprudencia"],
            "colombian_context": ["colombia", "colombiano", "pesos", "uvt", "dian", "superintendencia"],
            "pyme_focus": ["pyme", "pequeña empresa", "microempresa", "mediana empresa"],
            "actionable_advice": ["debe", "puede", "recomiendo", "es necesario", "pasos"]
        }
    
    def validate_dataset(self, examples: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Valida y filtra un dataset completo
        
        Args:
            examples: Lista de ejemplos a validar
            
        Returns:
            Lista de ejemplos validados y aprobados
        """
        validated = []
        stats = {
            "total": len(examples),
            "approved": 0,
            "rejected": 0,
            "reasons": {}
        }
        
        print(f"🔍 Validando {len(examples)} ejemplos...")
        
        for i, example in enumerate(examples):
            is_valid, reason = self.validate_example(example)
            
            if is_valid:
                # Aplicar mejoras automáticas
                improved_example = self._improve_example(example)
                validated.append(improved_example)
                stats["approved"] += 1
            else:
                stats["rejected"] += 1
                stats["reasons"][reason] = stats["reasons"].get(reason, 0) + 1
                print(f"❌ Ejemplo {i+1} rechazado: {reason}")
        
        self._print_validation_stats(stats)
        return validated
    
    def validate_example(self, example: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Valida un ejemplo individual
        
        Args:
            example: Ejemplo a validar
            
        Returns:
            Tupla (es_válido, razón_si_inválido)
        """
        # 1. Validar estructura
        if not self._validate_structure(example):
            return False, "Estructura inválida"
        
        # 2. Validar contenido de mensajes
        messages = example.get("messages", [])
        if len(messages) != 3:
            return False, "Debe tener exactamente 3 mensajes (system, user, assistant)"
        
        assistant_message = messages[2].get("content", "")
        
        # 3. Validar longitud de respuesta
        if len(assistant_message) < self.min_response_length:
            return False, f"Respuesta muy corta (<{self.min_response_length} chars)"
        
        if len(assistant_message) > self.max_response_length:
            return False, f"Respuesta muy larga (>{self.max_response_length} chars)"
        
        # 4. Validar confianza mínima
        confidence = example.get("confidence", 0)
        if confidence < self.min_confidence:
            return False, f"Confianza baja ({confidence} < {self.min_confidence})"
        
        # 5. Validar calidad de contenido
        quality_score = self._calculate_quality_score(assistant_message)
        if quality_score < 0.6:
            return False, f"Calidad de contenido baja ({quality_score:.2f})"
        
        # 6. Validar contexto legal
        if not self._has_legal_context(assistant_message):
            return False, "Falta contexto legal apropiado"
        
        return True, ""
    
    def _validate_structure(self, example: Dict[str, Any]) -> bool:
        """Valida la estructura básica del ejemplo"""
        required_fields = ["messages", "category", "confidence"]
        
        for field in required_fields:
            if field not in example:
                return False
        
        messages = example.get("messages", [])
        if not isinstance(messages, list):
            return False
        
        # Validar roles de mensajes
        expected_roles = ["system", "user", "assistant"]
        for i, message in enumerate(messages):
            if i >= len(expected_roles):
                break
            if message.get("role") != expected_roles[i]:
                return False
        
        return True
    
    def _calculate_quality_score(self, text: str) -> float:
        """Calcula un score de calidad basado en patrones"""
        text_lower = text.lower()
        score = 0.0
        total_patterns = 0
        
        for category, patterns in self.quality_patterns.items():
            category_score = 0
            for pattern in patterns:
                if pattern in text_lower:
                    category_score = 1.0
                    break
            
            # Pesos por categoría
            weights = {
                "legal_terms": 0.3,
                "colombian_context": 0.3,
                "pyme_focus": 0.2,
                "actionable_advice": 0.2
            }
            
            score += category_score * weights.get(category, 0.25)
            total_patterns += 1
        
        # Penalizar respuestas muy genéricas
        if len(text.split()) < 30:
            score *= 0.8
        
        # Bonificar estructura organizada
        if any(marker in text for marker in ["1.", "2.", "**", "-", "•"]):
            score *= 1.1
        
        return min(score, 1.0)
    
    def _has_legal_context(self, text: str) -> bool:
        """Verifica que el texto tenga contexto legal apropiado"""
        legal_indicators = [
            "ley", "artículo", "código", "decreto", "norma", "reglamento",
            "derechos", "obligaciones", "tribunal", "juridico", "legal",
            "colombia", "colombiano", "constitución"
        ]
        
        text_lower = text.lower()
        legal_count = sum(1 for indicator in legal_indicators if indicator in text_lower)
        
        return legal_count >= 2
    
    def _improve_example(self, example: Dict[str, Any]) -> Dict[str, Any]:
        """Aplica mejoras automáticas a un ejemplo válido"""
        improved = example.copy()
        
        # Mejorar respuesta del assistant
        messages = improved["messages"]
        assistant_content = messages[2]["content"]
        
        # Asegurar formato profesional
        if not assistant_content.strip().endswith('.'):
            assistant_content += '.'
        
        # Agregar contexto PyME si falta
        if "pyme" not in assistant_content.lower() and "pequeña empresa" not in assistant_content.lower():
            if improved.get("category") != "general":
                assistant_content = f"{assistant_content}\n\n**Nota para PyMEs**: Esta información es especialmente relevante para pequeñas y medianas empresas en Colombia."
        
        messages[2]["content"] = assistant_content
        improved["messages"] = messages
        
        # Agregar metadata de calidad
        improved["quality_score"] = self._calculate_quality_score(assistant_content)
        improved["validated"] = True
        
        return improved
    
    def _print_validation_stats(self, stats: Dict[str, Any]):
        """Imprime estadísticas de validación"""
        print(f"\n📊 Estadísticas de validación:")
        print(f"Total de ejemplos: {stats['total']}")
        print(f"✅ Aprobados: {stats['approved']}")
        print(f"❌ Rechazados: {stats['rejected']}")
        print(f"📈 Tasa de aprobación: {stats['approved']/stats['total']*100:.1f}%")
        
        if stats['reasons']:
            print(f"\n🔍 Razones de rechazo:")
            for reason, count in stats['reasons'].items():
                print(f"  • {reason}: {count}")
        
        print()
    
    def validate_for_openai(self, examples: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validación específica para formato OpenAI
        
        Args:
            examples: Ejemplos en formato OpenAI
            
        Returns:
            Ejemplos validados para OpenAI
        """
        validated = []
        
        for example in examples:
            # Validar que tenga la estructura correcta de OpenAI
            if "messages" not in example:
                continue
            
            messages = example["messages"]
            if len(messages) != 3:
                continue
            
            # Validar tokens aproximados (GPT-4 limit)
            total_chars = sum(len(msg["content"]) for msg in messages)
            if total_chars > 8000:  # Aproximadamente 2000 tokens
                continue
            
            validated.append(example)
        
        return validated 