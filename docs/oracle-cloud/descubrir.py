import oci
import sys

# --- CONFIGURACIÓN DE TU CUENTA ---
config = {
    "user": "ocid1.user.oc1..aaaaaaaaz66p6oxu6gvraf5mdvadn6xsbdhcvqleaz72rtsr7e6xwi2xnaba",
    "fingerprint": "39:22:62:db:77:ad:95:c7:0c:c2:2a:b1:8e:48:a6:58",
    "tenancy": "ocid1.tenancy.oc1..aaaaaaaats4hfx3wacmo4p57mrsw2g2ufu7po3fgsk53cln7o2xz3y66pgjq",
    "region": "sa-santiago-1",
    "key_file": "./oci_api_key.pem" 
}

print("--- INICIANDO DIAGNÓSTICO DE OCI ---")

try:
    identity = oci.identity.IdentityClient(config)
    compute = oci.core.ComputeClient(config)
    network = oci.core.VirtualNetworkClient(config)

    # 1. Verificar ADs
    ads = identity.list_availability_domains(config["tenancy"]).data
    print("\n[1] Availability Domains (ADs):")
    for ad in ads:
        print(f"  - {ad.name}")

    # 2. Verificar Subnets (buscando en el compartment root)
    subnets = network.list_subnets(config["tenancy"]).data
    print("\n[2] Subnets en el Tenancy:")
    if not subnets:
        print("  - No se encontraron subnets directamente en el Tenancy root.")
    for sub in subnets:
        print(f"  - {sub.display_name}: {sub.id}")

    # 3. Buscar Imagen de Ubuntu 24.04 ARM
    print("\n[3] Buscando Imágenes de Ubuntu 24.04 ARM...")
    images = compute.list_images(config["tenancy"], operating_system="Canonical Ubuntu", operating_system_version="24.04").data
    found_img = False
    for img in images:
        if "aarch64" in img.display_name or "ARM" in img.display_name:
            print(f"  - ENCONTRADA: {img.display_name}")
            print(f"    OCID: {img.id}")
            found_img = True
    if not found_img:
        print("  - No se encontró imagen Ubuntu 24.04 ARM con los filtros estándar.")

except oci.exceptions.ServiceError as e:
    print(f"\n❌ ERROR DE SERVICIO OCI: {e.message}")
except Exception as e:
    print(f"\n❌ ERROR INESPERADO: {str(e)}")
