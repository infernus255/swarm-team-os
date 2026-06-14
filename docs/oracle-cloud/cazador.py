import oci
import time
import base64
from datetime import datetime

# --- CONFIGURACIÓN DE TU CUENTA ---
config = {
    "user": "ocid1.user.oc1..aaaaaaaaz66p6oxu6gvraf5mdvadn6xsbdhcvqleaz72rtsr7e6xwi2xnaba",
    "fingerprint": "39:22:62:db:77:ad:95:c7:0c:c2:2a:b1:8e:48:a6:58",
    "tenancy": "ocid1.tenancy.oc1..aaaaaaaats4hfx3wacmo4p57mrsw2g2ufu7po3fgsk53cln7o2xz3y66pgjq",
    "region": "sa-santiago-1",
    "key_file": "./oci_api_key.pem" 
}

# --- DATOS DE LA INFRAESTRUCTURA ---
COMPARTMENT_ID = "ocid1.tenancy.oc1..aaaaaaaats4hfx3wacmo4p57mrsw2g2ufu7po3fgsk53cln7o2xz3y66pgjq"
SUBNET_ID = "ocid1.subnet.oc1.sa-santiago-1.aaaaaaaai2kesnhnejmmvqtp74mzuntvswi5k5e6jq2ytgpoedodrl34d33q"
IMAGE_ID = "ocid1.image.oc1.sa-santiago-1.aaaaaaaac7yorcmugfai73adfcoyfkuvkx4dciv3uahfskaszvwp3d3i53eq"

# --- LLAVE SSH PÚBLICA ---
SSH_PUBLIC_KEY = """ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDmGM0H9vnhwMzJdQTkoW2KVO5ELPbLOHMOX0MxylFxxBb4KUxFQ/4qsyBerHJ7TT95gP+lxwvQJMPfocVGBwCaPeG7GuU1WNoJo2aQDsaiB/h4kDUFXiW1Q/O6OR+W0NviizIszSblIJQcNpqpjydT9mxYQ6DrKtN6po4u5MQl7b4GVb4HIGt3OGcfA+wUanrH11DUSPvd2a4E4//CC/eCyJnxjgTcO0oRaxocG1LX2MV/J9nYP8jk/LX1rmITyhp3xTLBFgxTrcrDTCl2/uCH89WxDyehYKMqXI7q7VKJp7szHlixbbgbYCVntIiBMY7HyqiW2yn5Fp/RSbblFewT ssh-key-2026-06-10"""

# --- SCRIPT DE INICIALIZACIÓN ---
cloud_init_script = """#!/bin/bash
apt-get update
apt-get install -y docker.io docker-compose-plugin git curl
usermod -aG docker ubuntu
"""
encoded_cloud_init = base64.b64encode(cloud_init_script.encode()).decode()

def try_launch():
    try:
        compute = oci.core.ComputeClient(config)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Intentando cazar instancia ARM en Santiago...")
        
        launch_details = oci.core.models.LaunchInstanceDetails(
            compartment_id=COMPARTMENT_ID,
            availability_domain="CLef:SA-SANTIAGO-1-AD-1",
            shape="VM.Standard.A1.Flex",
            shape_config=oci.core.models.LaunchInstanceShapeConfigDetails(ocpus=4, memory_in_gbs=24),
            source_details=oci.core.models.InstanceSourceViaImageDetails(image_id=IMAGE_ID, boot_volume_size_in_gbs=200),
            launch_options=oci.core.models.LaunchOptions(
                boot_volume_type="PARAVIRTUALIZED",
                network_type="PARAVIRTUALIZED",
                firmware="UEFI_64",
                is_pv_encryption_in_transit_enabled=True,
                is_consistent_volume_naming_enabled=True
            ),
            agent_config=oci.core.models.LaunchInstanceAgentConfigDetails(
                is_monitoring_disabled=False,
                is_management_disabled=True,
                plugins_config=[
                    oci.core.models.InstanceAgentPluginConfigDetails(name="Compute Instance Monitoring", desired_state="ENABLED"),
                    oci.core.models.InstanceAgentPluginConfigDetails(name="Block Volume Management", desired_state="ENABLED")
                ]
            ),
            subnet_id=SUBNET_ID,
            metadata={
                "user_data": encoded_cloud_init,
                "ssh_authorized_keys": SSH_PUBLIC_KEY
            }
        )
        
        response = compute.launch_instance(launch_details)
        print("\n\a" + "="*50)
        print("¡¡VICTORIA!! Instancia creada con éxito.")
        print(f"ID: {response.data.id}")
        print("="*50)
        return True
        
    except oci.exceptions.ServiceError as e:
        error_msg = str(e).lower()
        if e.status == 429 or "capacity" in error_msg:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Santiago sin stock. Reintentando...")
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Error de Oracle: {e.message}")
        return False
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Error de conexión o red: {str(e)[:100]}...")
        return False

if __name__ == "__main__":
    print("--- INICIANDO CAZADOR RESISTENTE (SANTIAGO) ---")
    print("El script no se detendrá ante errores de conexión.")
    while True:
        try:
            if try_launch():
                break
        except Exception as e:
            print(f"Error crítico en el bucle: {e}")
        time.sleep(30)
