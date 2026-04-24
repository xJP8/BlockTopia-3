import hashlib
import json
import os
import urllib.request
import urllib.error

MODS_FOLDER = "mods"

def sha512(path):
    h = hashlib.sha512()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def buscar_en_modrinth(hashes):
    url = "https://api.modrinth.com/v2/version_files"
    payload = json.dumps({
        "hashes": hashes,
        "algorithm": "sha512"
    }).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "packwiz-detector/1.0"
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"Error HTTP {e.code}: {e.reason}")
        return {}

def main():
    if not os.path.isdir(MODS_FOLDER):
        print(f"No se encontró la carpeta '{MODS_FOLDER}'. Ejecuta este script desde la raíz del modpack.")
        input("\nPulsa Enter para salir...")
        return

    jars = [f for f in os.listdir(MODS_FOLDER) if f.endswith(".jar")]
    if not jars:
        print("No hay archivos .jar en la carpeta mods/")
        input("\nPulsa Enter para salir...")
        return

    print(f"Encontrados {len(jars)} archivos .jar, calculando hashes...\n")

    hash_a_archivo = {}
    for jar in jars:
        path = os.path.join(MODS_FOLDER, jar)
        h = sha512(path)
        hash_a_archivo[h] = jar

    print("Consultando API de Modrinth...\n")
    resultados = buscar_en_modrinth(list(hash_a_archivo.keys()))

    encontrados = []
    no_encontrados = []

    for h, archivo in hash_a_archivo.items():
        if h in resultados:
            slug = resultados[h]["project_id"]
            nombre = resultados[h].get("name", archivo)
            encontrados.append((archivo, slug, nombre))
        else:
            no_encontrados.append(archivo)

    print("=" * 60)
    print(f"✅ ENCONTRADOS EN MODRINTH ({len(encontrados)}/{len(jars)})")
    print("=" * 60)
    for archivo, slug, nombre in encontrados:
        print(f"  {nombre}  →  {archivo}")

    print()
    print("=" * 60)
    print("📋 COMANDOS PACKWIZ A EJECUTAR")
    print("=" * 60)
    for _, slug, _ in encontrados:
        print(f"packwiz mr add {slug}")

    # Guardar comandos en archivo
    with open("añadir_mods.bat", "w", encoding="utf-8") as f:
        f.write("@echo off\n")
        for _, slug, _ in encontrados:
            f.write(f"packwiz mr add {slug}\n")
        f.write("packwiz refresh\n")
        f.write("echo Listo!\n")
        f.write("pause\n")

    print()
    print(f"✅ Se ha generado 'añadir_mods.bat' con todos los comandos.")

    if no_encontrados:
        print()
        print("=" * 60)
        print(f"❌ NO ENCONTRADOS EN MODRINTH ({len(no_encontrados)}/{len(jars)})")
        print("   (Puede que estén solo en CurseForge o sean mods privados)")
        print("=" * 60)
        for archivo in no_encontrados:
            print(f"  {archivo}")

        with open("no_encontrados.txt", "w", encoding="utf-8") as f:
            for archivo in no_encontrados:
                f.write(archivo + "\n")
        print()
        print("📄 Lista guardada en 'no_encontrados.txt'")

    print()
    input("Pulsa Enter para salir...")

if __name__ == "__main__":
    main()