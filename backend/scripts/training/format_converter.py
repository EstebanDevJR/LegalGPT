#!/usr/bin/env python3
"""
🔄 Format Converter - LegalGPT Fine-Tuning

Convertidor de formatos para datasets de entrenamiento.
Maneja conversiones entre diferentes formatos de datos.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Union

class FormatConverter:
    """Convertidor de formatos para datasets"""
    
    def __init__(self):
        self.openai_system_message = "Eres un experto en derecho colombiano especializado en asesoría legal para PyMEs."
    
    def to_openai_format(self, examples: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convierte ejemplos al formato requerido por OpenAI
        
        Args:
            examples: Lista de ejemplos en formato interno
            
        Returns:
            Lista de ejemplos en formato OpenAI
        """
        openai_examples = []
        
        for example in examples:
            # Verificar que tenga la estructura correcta
            if "messages" not in example:
                continue
            
            messages = example["messages"]
            
            # Asegurar que el mensaje del sistema sea consistente
            if len(messages) >= 1 and messages[0]["role"] == "system":
                messages[0]["content"] = self.openai_system_message
            
            openai_example = {
                "messages": messages
            }
            
            # Agregar metadata opcional para tracking
            if "category" in example:
                openai_example["metadata"] = {
                    "category": example["category"],
                    "confidence": example.get("confidence", 0.8),
                    "complexity": example.get("complexity", "medium")
                }
            
            openai_examples.append(openai_example)
        
        return openai_examples
    
    def to_huggingface_format(self, examples: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convierte ejemplos al formato HuggingFace
        
        Args:
            examples: Lista de ejemplos en formato interno
            
        Returns:
            Lista de ejemplos en formato HuggingFace
        """
        hf_examples = []
        
        for example in examples:
            if "messages" not in example:
                continue
            
            messages = example["messages"]
            
            # Extraer pregunta y respuesta
            user_message = ""
            assistant_message = ""
            
            for msg in messages:
                if msg["role"] == "user":
                    user_message = msg["content"]
                elif msg["role"] == "assistant":
                    assistant_message = msg["content"]
            
            if user_message and assistant_message:
                hf_example = {
                    "instruction": user_message,
                    "output": assistant_message,
                    "input": "",  # Para formato Alpaca
                    "category": example.get("category", "general")
                }
                hf_examples.append(hf_example)
        
        return hf_examples
    
    def to_conversational_format(self, examples: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convierte ejemplos a formato conversacional simple
        
        Args:
            examples: Lista de ejemplos en formato interno
            
        Returns:
            Lista de conversaciones
        """
        conversations = []
        
        for example in examples:
            if "messages" not in example:
                continue
            
            messages = example["messages"]
            
            conversation = {
                "id": f"legal_{len(conversations) + 1}",
                "conversations": []
            }
            
            for msg in messages:
                conversation["conversations"].append({
                    "from": msg["role"],
                    "value": msg["content"]
                })
            
            # Agregar metadata
            conversation["category"] = example.get("category", "general")
            conversation["source"] = "LegalGPT"
            
            conversations.append(conversation)
        
        return conversations
    
    def save_jsonl(self, examples: List[Dict[str, Any]], output_path: Union[str, Path]):
        """
        Guarda ejemplos en formato JSONL
        
        Args:
            examples: Lista de ejemplos
            output_path: Ruta del archivo de salida
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for example in examples:
                json_line = json.dumps(example, ensure_ascii=False)
                f.write(json_line + '\n')
        
        print(f"💾 Guardado: {output_path} ({len(examples)} ejemplos)")
    
    def save_json(self, examples: List[Dict[str, Any]], output_path: Union[str, Path]):
        """
        Guarda ejemplos en formato JSON
        
        Args:
            examples: Lista de ejemplos
            output_path: Ruta del archivo de salida
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(examples, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Guardado: {output_path} ({len(examples)} ejemplos)")
    
    def load_jsonl(self, input_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """
        Carga ejemplos desde formato JSONL
        
        Args:
            input_path: Ruta del archivo de entrada
            
        Returns:
            Lista de ejemplos cargados
        """
        input_path = Path(input_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {input_path}")
        
        examples = []
        
        with open(input_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    example = json.loads(line)
                    examples.append(example)
                except json.JSONDecodeError as e:
                    print(f"⚠️ Error en línea {line_num}: {e}")
                    continue
        
        print(f"📂 Cargado: {input_path} ({len(examples)} ejemplos)")
        return examples
    
    def merge_datasets(self, *dataset_paths: Union[str, Path]) -> List[Dict[str, Any]]:
        """
        Combina múltiples datasets
        
        Args:
            dataset_paths: Rutas de los datasets a combinar
            
        Returns:
            Dataset combinado
        """
        merged = []
        
        for path in dataset_paths:
            try:
                dataset = self.load_jsonl(path)
                merged.extend(dataset)
                print(f"✅ Agregado: {path} ({len(dataset)} ejemplos)")
            except Exception as e:
                print(f"❌ Error cargando {path}: {e}")
        
        print(f"🔗 Dataset combinado: {len(merged)} ejemplos totales")
        return merged
    
    def split_dataset(self, examples: List[Dict[str, Any]], 
                     train_ratio: float = 0.8, 
                     val_ratio: float = 0.1,
                     test_ratio: float = 0.1) -> Dict[str, List[Dict[str, Any]]]:
        """
        Divide dataset en conjuntos de entrenamiento, validación y prueba
        
        Args:
            examples: Lista de ejemplos
            train_ratio: Proporción para entrenamiento
            val_ratio: Proporción para validación
            test_ratio: Proporción para prueba
            
        Returns:
            Diccionario con los conjuntos divididos
        """
        import random
        
        # Validar proporciones
        total_ratio = train_ratio + val_ratio + test_ratio
        if abs(total_ratio - 1.0) > 0.001:
            raise ValueError(f"Las proporciones deben sumar 1.0, suma actual: {total_ratio}")
        
        # Mezclar ejemplos
        shuffled = examples.copy()
        random.shuffle(shuffled)
        
        total = len(shuffled)
        train_end = int(total * train_ratio)
        val_end = train_end + int(total * val_ratio)
        
        splits = {
            "train": shuffled[:train_end],
            "validation": shuffled[train_end:val_end],
            "test": shuffled[val_end:]
        }
        
        print(f"📊 Dataset dividido:")
        print(f"  Entrenamiento: {len(splits['train'])} ejemplos ({len(splits['train'])/total*100:.1f}%)")
        print(f"  Validación: {len(splits['validation'])} ejemplos ({len(splits['validation'])/total*100:.1f}%)")
        print(f"  Prueba: {len(splits['test'])} ejemplos ({len(splits['test'])/total*100:.1f}%)")
        
        return splits
    
    def export_for_platform(self, examples: List[Dict[str, Any]], 
                           platform: str, 
                           output_dir: Union[str, Path]):
        """
        Exporta dataset para plataforma específica
        
        Args:
            examples: Lista de ejemplos
            platform: Plataforma destino ('openai', 'huggingface', 'conversational')
            output_dir: Directorio de salida
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if platform.lower() == 'openai':
            formatted = self.to_openai_format(examples)
            output_path = output_dir / "openai_dataset.jsonl"
            self.save_jsonl(formatted, output_path)
        
        elif platform.lower() == 'huggingface':
            formatted = self.to_huggingface_format(examples)
            output_path = output_dir / "huggingface_dataset.json"
            self.save_json(formatted, output_path)
        
        elif platform.lower() == 'conversational':
            formatted = self.to_conversational_format(examples)
            output_path = output_dir / "conversational_dataset.json"
            self.save_json(formatted, output_path)
        
        else:
            raise ValueError(f"Plataforma no soportada: {platform}")
        
        print(f"🚀 Dataset exportado para {platform}: {output_path}")
    
    def validate_openai_format(self, examples: List[Dict[str, Any]]) -> bool:
        """
        Valida que los ejemplos cumplan con el formato OpenAI
        
        Args:
            examples: Lista de ejemplos a validar
            
        Returns:
            True si el formato es válido
        """
        for i, example in enumerate(examples):
            # Verificar estructura básica
            if "messages" not in example:
                print(f"❌ Ejemplo {i}: Falta campo 'messages'")
                return False
            
            messages = example["messages"]
            if not isinstance(messages, list):
                print(f"❌ Ejemplo {i}: 'messages' debe ser una lista")
                return False
            
            # Verificar mensajes
            for j, message in enumerate(messages):
                if "role" not in message or "content" not in message:
                    print(f"❌ Ejemplo {i}, mensaje {j}: Falta 'role' o 'content'")
                    return False
                
                if message["role"] not in ["system", "user", "assistant"]:
                    print(f"❌ Ejemplo {i}, mensaje {j}: Rol inválido '{message['role']}'")
                    return False
        
        print(f"✅ Formato OpenAI válido ({len(examples)} ejemplos)")
        return True 