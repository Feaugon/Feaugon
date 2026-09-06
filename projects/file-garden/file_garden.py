"""Organize arquivos locais com prévia e sem substituir destinos existentes."""
import argparse
import json
import os
from pathlib import Path

CATEGORIES = {
    "Imagens": {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".heic"},
    "Documentos": {".pdf", ".txt", ".md", ".docx", ".xlsx", ".pptx", ".csv"},
    "Audio": {".mp3", ".wav", ".flac", ".ogg", ".m4a"},
    "Video": {".mp4", ".mov", ".mkv", ".avi", ".webm"},
    "Compactados": {".zip", ".rar", ".7z", ".gz", ".tar"},
    "Codigo": {".py", ".js", ".ts", ".dart", ".html", ".css", ".json"},
}


def category(path):
    return next((name for name, exts in CATEGORIES.items() if path.suffix.lower() in exts), "Outros")


def plan(folder):
    root = Path(folder).resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Informe uma pasta.")
    moves, reserved = [], set()
    for source in sorted(root.iterdir(), key=lambda p: p.name.casefold()):
        if source.is_symlink() or not source.is_file() or source.name.startswith("."):
            continue
        directory = root / category(source)
        if directory.is_symlink() or (directory.exists() and not directory.is_dir()):
            raise ValueError(f"Destino inválido: {directory.name}")
        target = directory / source.name
        number = 1
        while target.exists() or target.is_symlink() or str(target).casefold() in reserved:
            target = directory / f"{source.stem} ({number}){source.suffix}"
            number += 1
        reserved.add(str(target).casefold())
        moves.append((source, target))
    return moves


def apply(moves):
    results = []
    for source, target in moves:
        try:
            if source.is_symlink() or not source.is_file():
                raise ValueError("Origem mudou; gere uma nova prévia.")
            if target.parent.is_symlink():
                raise ValueError("Destino não pode ser um link simbólico.")
            target.parent.mkdir(exist_ok=True)
            # link() falha se o destino já existe: nunca sobrescreve outro arquivo.
            # As duas entradas apontam aos mesmos bytes até unlink() concluir.
            os.link(source, target)
            try:
                source.unlink()
            except OSError as exc:
                raise OSError(f"Cópia vinculada criada; original preservado: {exc}") from exc
            results.append({"source": str(source), "target": str(target), "status": "moved"})
        except (OSError, ValueError) as exc:
            results.append({"source": str(source), "target": str(target), "status": "error", "error": str(exc)})
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description="File Garden · organize por tipo, com prévia por padrão.")
    parser.add_argument("folder", type=Path, help="Pasta local para organizar")
    parser.add_argument("--apply", action="store_true", help="Executar os movimentos exibidos na prévia")
    args = parser.parse_args(argv)
    try:
        moves = plan(args.folder)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    if not args.apply:
        print("FILE GARDEN / PRÉVIA — nenhum arquivo foi alterado\n")
        for source, target in moves:
            print(f"  {source.name}  ->  {target.parent.name}/{target.name}")
        print(f"\n{len(moves)} arquivo(s). Use --apply para executar.")
        return 0
    results = apply(moves)
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return int(any(result["status"] == "error" for result in results))


if __name__ == "__main__":
    raise SystemExit(main())
