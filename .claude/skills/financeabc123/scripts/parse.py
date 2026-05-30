#!/usr/bin/env python3
"""
Convierte archivos financieros a markdown y los guarda en la carpeta del perfil.

Uso:
  python3 parse.py --file extracto.pdf --persona "Ian"
  python3 parse.py --init --persona "Ian"   # solo crea la carpeta
"""

import argparse
import shutil
import sys
from datetime import date
from pathlib import Path


BASE_DIR = Path.home() / "finanzas"


def init_profile_dir(persona: str) -> Path:
    """Crea la carpeta del perfil si no existe. Retorna la ruta."""
    slug = persona.lower().replace(" ", "_") if persona else "usuario"
    profile_dir = BASE_DIR / slug
    profile_dir.mkdir(parents=True, exist_ok=True)

    docs_dir = profile_dir / "documentos"
    docs_dir.mkdir(exist_ok=True)

    perfil_path = profile_dir / "perfil.md"
    if not perfil_path.exists():
        perfil_path.write_text(f"""# Perfil Financiero: {persona or 'Usuario'}
**Moneda:** MXN | **Creado:** {date.today()} | **Actualizado:** {date.today()}

## Ingresos
| Fuente | Categoría | Bruto/mes | Impuesto | Neto/mes |
|--------|-----------|-----------|----------|----------|

## Gastos
| Concepto | Categoría | Tipo | Actual/mes | Mínimo Lean |
|----------|-----------|------|-----------|-------------|

## Deudas
| Deuda | Tipo | Balance | APR | Pago mín./mes | Ingreso que genera |
|-------|------|---------|-----|--------------|-------------------|

## Tarjetas de Crédito
| Tarjeta | Límite | Balance | Utilización | APR | Vence |
|---------|--------|---------|-------------|-----|-------|

## Inversiones
| Inversión | Clase | Valor actual | Contribución/mes | Retorno esp. | Ingreso/mes |
|-----------|-------|-------------|-----------------|-------------|------------|

## Activos Físicos
| Activo | Tipo | Valor | Nota |
|--------|------|-------|------|

## Scorecard
| Métrica | Valor | Estado |
|---------|-------|--------|
| PAW Status | — | — |
| FI Number | — | — |
| Años para IF | — | — |
| Tasa de ahorro | — | — |
| DTI | — | — |
| Utilización crédito | — | — |
| Fondo emergencia | — | — |

## Plan de Acción
| Paso | Acción | Estado | Fecha |
|------|--------|--------|-------|

## Historial de Documentos
| Fecha | Archivo | Tipo |
|-------|---------|------|

## Notas
""")

    return profile_dir


def convert_to_markdown(file_path: str) -> str:
    try:
        from markitdown import MarkItDown
        md = MarkItDown()
        result = md.convert(file_path)
        return result.text_content
    except ImportError:
        return "[ERROR] markitdown no instalado. Corre: pip install markitdown"
    except Exception as e:
        return f"[ERROR] No se pudo convertir {file_path}: {e}"


def save_document(file_path: Path, profile_dir: Path) -> Path:
    """Copia el archivo a ~/finanzas/<persona>/documentos/ con fecha."""
    docs_dir = profile_dir / "documentos"
    dated_name = f"{date.today()}_{file_path.name}"
    dest = docs_dir / dated_name
    shutil.copy2(file_path, dest)
    return dest


def main():
    parser = argparse.ArgumentParser(description="Parsea archivos financieros y gestiona perfil")
    parser.add_argument("--file", help="Ruta al archivo a convertir")
    parser.add_argument("--persona", default="usuario", help="Nombre de la persona")
    parser.add_argument("--init", action="store_true", help="Solo inicializar carpeta de perfil")
    args = parser.parse_args()

    profile_dir = init_profile_dir(args.persona)
    print(f"📁 Carpeta del perfil: {profile_dir}")
    print(f"   ├── perfil.md")
    print(f"   └── documentos/")

    if args.init:
        perfil_path = profile_dir / "perfil.md"
        if perfil_path.stat().st_size > 500:
            print(f"\n✅ Perfil existente encontrado — cargando datos...")
        else:
            print(f"\n✅ Perfil nuevo creado en {profile_dir}")
        return

    if not args.file:
        print("[ERROR] Especifica --file o usa --init", file=sys.stderr)
        sys.exit(1)

    file_path = Path(args.file).expanduser()
    if not file_path.exists():
        print(f"[ERROR] Archivo no encontrado: {file_path}", file=sys.stderr)
        sys.exit(1)

    # Save document to profile folder
    saved_path = save_document(file_path, profile_dir)
    print(f"\n💾 Archivo guardado en: {saved_path}")
    print(f"\n=== CONVIRTIENDO: {file_path.name} ===\n")

    markdown = convert_to_markdown(str(file_path))
    print(markdown)

    print("\n=== FIN DE CONVERSIÓN ===")
    print(f"\nClaude: extrae los datos financieros del contenido de arriba.")
    print(f"Luego actualiza {profile_dir}/perfil.md con la información encontrada.")
    print(f"Registra este documento en la sección 'Historial de Documentos' del perfil.")


if __name__ == "__main__":
    main()
