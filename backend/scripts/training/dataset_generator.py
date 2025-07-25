#!/usr/bin/env python3
"""
🎯 Dataset Generator Core - LegalGPT Fine-Tuning

Clase principal para generar datasets de entrenamiento de alta calidad
para modelos GPT especializados en asesoría legal colombiana.
"""

import os
import sys
import json
import asyncio
import argparse
from pathlib import Path
from typing import Dict, Any, List

# Agregar backend al path
sys.path.append(str(Path(__file__).parent.parent.parent))

from services.legal.fine_tuning_service import FineTuningService
from .data_processor import DataProcessor
from .quality_validator import QualityValidator
from .format_converter import FormatConverter

class DatasetGenerator:
    """Generador principal de datasets de entrenamiento"""
    
    def __init__(self):
        self.output_dir = Path("backend/data/training/datasets")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Inicializar componentes
        self.fine_tuning_service = FineTuningService()
        self.data_processor = DataProcessor()
        self.quality_validator = QualityValidator()
        self.format_converter = FormatConverter()
        
        # Inicializar RAG service
        try:
            from services.legal.rag import RAGCore
            self.rag_service = RAGCore()
            print("✅ RAG service inicializado correctamente")
        except Exception as e:
            print(f"⚠️ RAG service no disponible: {e}")
            self.rag_service = None
    
    async def generate_complete_dataset(self, interactive: bool = False) -> str:
        """
        Genera un dataset completo de entrenamiento
        
        Args:
            interactive: Si permite revisión manual de respuestas
            
        Returns:
            str: Ruta del archivo de dataset generado
        """
        print("🎯 Iniciando generación de dataset completo...")
        
        # 1. Procesar datos base
        base_examples = self.data_processor.get_base_examples()
        
        # 2. Generar ejemplos adicionales
        if self.rag_service:
            additional_examples = await self.data_processor.generate_rag_examples(
                self.rag_service, interactive
            )
        else:
            additional_examples = self.data_processor.get_static_examples()
        
        # 3. Combinar todos los ejemplos
        all_examples = base_examples + additional_examples
        
        # 4. Validar calidad
        validated_examples = self.quality_validator.validate_dataset(all_examples)
        
        # 5. Convertir a formato OpenAI
        formatted_dataset = self.format_converter.to_openai_format(validated_examples)
        
        # 6. Guardar dataset
        output_file = self.output_dir / f"legalgpt_dataset_{len(formatted_dataset)}_ejemplos.jsonl"
        self.format_converter.save_jsonl(formatted_dataset, output_file)
        
        print(f"✅ Dataset generado: {output_file}")
        print(f"📊 Total de ejemplos: {len(formatted_dataset)}")
        
        return str(output_file)
    
    def generate_specific_dataset(self, category: str, count: int = 50) -> str:
        """
        Genera dataset para una categoría específica
        
        Args:
            category: Categoría legal (civil, comercial, laboral, tributario)
            count: Número de ejemplos a generar
            
        Returns:
            str: Ruta del archivo generado
        """
        print(f"🎯 Generando dataset para categoría: {category}")
        
        examples = self.data_processor.get_category_examples(category, count)
        validated_examples = self.quality_validator.validate_dataset(examples)
        formatted_dataset = self.format_converter.to_openai_format(validated_examples)
        
        output_file = self.output_dir / f"legalgpt_{category}_{len(formatted_dataset)}_ejemplos.jsonl"
        self.format_converter.save_jsonl(formatted_dataset, output_file)
        
        print(f"✅ Dataset {category} generado: {output_file}")
        return str(output_file)


def main():
    """Función principal del script"""
    parser = argparse.ArgumentParser(description="Generador de Dataset LegalGPT")
    parser.add_argument("--complete", action="store_true", 
                       help="Genera dataset completo usando RAG")
    parser.add_argument("--interactive", action="store_true",
                       help="Permite revisión manual de respuestas")
    parser.add_argument("--category", type=str, choices=["civil", "comercial", "laboral", "tributario"],
                       help="Genera dataset para categoría específica")
    parser.add_argument("--count", type=int, default=50,
                       help="Número de ejemplos para categoría específica")
    
    args = parser.parse_args()
    
    generator = DatasetGenerator()
    
    try:
        if args.category:
            output_file = generator.generate_specific_dataset(args.category, args.count)
        elif args.complete:
            output_file = asyncio.run(generator.generate_complete_dataset(args.interactive))
        else:
            print("❌ Especifica --complete o --category")
            return
        
        print(f"🎉 Proceso completado exitosamente: {output_file}")
        
    except Exception as e:
        print(f"❌ Error durante la generación: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 