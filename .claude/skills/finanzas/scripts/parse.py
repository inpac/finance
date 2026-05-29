#!/usr/bin/env python3
"""
Convierte archivos financieros a markdown usando markitdown.
Claude lee el output e interpreta los datos financieros.

Uso:
  python3 parse.py --file extracto.pdf --persona "Ana García"
  python3 parse.py --file gastos.xlsx --persona ana
"""

import argparse
import sys
from pathlib import Path


def convert_to_markdown(file_path: str) -> str:
    try:
        from markitdown import MarkItDown
        md = MarkItDown()
        result = md.convert(file_path)
        return result.text_content
    except ImportError:
        return f"[ERROR] markitdown no instalado. Corre: pip install markitdown"
    except Exception as e:
        return f"[ERROR] No se pudo convertir {file_path}: {e}"


def main():
    parser = argparse.ArgumentParser(description="Convierte archivos financieros a markdown")
    parser.add_argument("--file", required=True, help="Ruta al archivo a convertir")
    parser.add_argument("--persona", default="", help="Nombre de la persona (para contexto)")
    args = parser.parse_args()

    file_path = Path(args.file).expanduser()
    if not file_path.exists():
        print(f"[ERROR] Archivo no encontrado: {file_path}", file=sys.stderr)
        sys.exit(1)

    print(f"=== ARCHIVO: {file_path.name} ===")
    print(f"=== PERSONA: {args.persona or 'no especificada'} ===")
    print(f"=== TIPO: {file_path.suffix.upper()} ===\n")
    print("=== CONTENIDO CONVERTIDO A MARKDOWN ===\n")

    markdown = convert_to_markdown(str(file_path))
    print(markdown)

    print("\n=== FIN DE CONVERSIÓN ===")
    print("Claude: lee el markdown de arriba y extrae los datos financieros relevantes.")
    print("Luego actualiza las tablas del perfil.md con la información encontrada.")


if __name__ == "__main__":
    main()
