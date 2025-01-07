# Ansible Must-Gather Automation

Este repositorio contiene una solución automatizada para generar, comprimir y cargar los resultados de must-gather de OpenShift a un caso de soporte de Red Hat utilizando Ansible.

## Características
- Automatiza el proceso de generación de datos must-gather.
- Comprime los datos en un archivo tarball para facilitar la carga.
- Carga automáticamente el archivo tarball en un caso de soporte de Red Hat utilizando credenciales S3.

---

## Requisitos Previos

### 1. Entorno de Ejecución (Execution Environment)
- Asegúrate de construir y subir el entorno de ejecución necesario al registro de contenedores (e.g., Quay.io).

### 2. Herramientas Requeridas
- `ansible-navigator`
- `podman` (para construir y gestionar imágenes de contenedores)

### 3. Acceso
- Una cuenta de Red Hat con acceso a casos de soporte.
- Ansible Automation Platform o CLI de Ansible instalado localmente.

---

## Configuración

### Variables a Modificar

#### 1. Modificar el archivo `vars/main.yaml`

Abre el archivo `vars/main.yaml` y configura las siguientes variables:

```yaml
# Información del caso de soporte
case_number: "<CASE_NUMBER>"
debug_enabled: true

# Constantes
file_path: "/tmp/must-gather.tar.gz"
script_path: "../scripts/upload_to_s3.py"
client_id: "rhsm-api"
token_url: "https://sso.redhat.com/auth/realms/redhat-external/protocol/openid-connect/token"
case_details_url: "https://api.access.redhat.com/support/v1/cases/{{ case_number }}"
bucket_url: "https://access.redhat.com/hydra/rest/cases/{{ case_number }}/attachments/upload/credentials"
```

#### 2. Modificar el archivo `vars/credentials.yaml`

Abre el archivo `vars/credentials.yaml` y configura las siguientes variables:

```yaml
#OCP
ocp_user: "<USER_OCP>"
ocp_password: "<PASSWORD_OCP>"
ocp_url: "https://<API_OPENSHIFT>:6443"

#Token
refresh_token: <TOKEN_API>
```

### Obtener el Token de Acceso

1. Ve a [Red Hat API Management](https://access.redhat.com/management/api) para obtener tu token de acceso.
2. Copia el token proporcionado y reemplaza `<TOKEN_API>` en `vars/credentials.yaml`.

### Proteger las Credenciales

1. Protege las credenciales utilizando Ansible Vault para evitar exponer información sensible:
   ```bash
   ansible-vault encrypt vars/credentials.yaml
   ```
2. Crea un archivo llamado `vault_password` que contenga la contraseña del vault para que pueda ser utilizada durante la ejecución del playbook.
   ```bash
   echo "<VAULT_PASSWORD>" > vault_password
   ```
   **Nota:** Reemplaza `<VAULT_PASSWORD>` con la contraseña real que usaste al cifrar las credenciales.

Es importante proteger este archivo ya que contiene información confidencial como tokens y credenciales.

---

## Generación del Execution Environment

Antes de ejecutar este comando, asegúrate de que el archivo `execution-environment.yml` esté correctamente configurado.

1. Construye el entorno de ejecución con el archivo `execution-environment.yml` proporcionado:

```bash
ansible-builder build -t ee-ocp:latest
```

2. Etiqueta la imagen para subirla a tu repositorio de contenedores (reemplaza `<user>` con tu usuario en Quay.io):

```bash
podman tag ee-ocp:latest quay.io/<user>/ee-ocp:1.0
```

3. Sube la imagen al repositorio:

```bash
podman push quay.io/<user>/ee-ocp:1.0
```

---

## Ejecución del Playbook

1. Navega al directorio del proyecto que contiene el archivo `ansible-navigator.yml`.

2. Ejecuta el playbook utilizando `ansible-navigator`:

```bash
ansible-navigator run main.yaml --pae false --mode stdout \
  --eei quay.io/<user>/ee-ocp:1.0 --vault-password-file=vault_password
```

### Funcionalidades del Playbook

- Generará el tarball de must-gather si `execute_generate_must_gather` está configurado como `true`.
- Subirá el tarball al caso de soporte de Red Hat si `execute_upload_must_gather` está configurado como `true`.

Si la ejecución falla, revisa los logs generados en la consola para identificar el problema.

---

## Estructura del Repositorio

```plaintext
├── ansible
│   ├── inventories
│   ├── playbooks
│   ├── roles
│   └── vars
│       ├── main.yaml
│       └── credentials.yaml
├── execution-environment
│   ├── configs
│   │   └── ansible.cfg
│   ├── rpm
│   │   └── openshift-clients-4.16.0.rpm
│   └── execution-environment.yml
├── scripts
│   └── upload_to_s3.py
└── README.md
```

---

## Notas Adicionales

- **Verifica las credenciales**: Antes de ejecutar, asegúrate de que todas las credenciales y URLs en el archivo `credentials.yaml` sean correctas.
- **Logs de depuración**: Si `debug_enabled` está configurado como `true`, se mostrarán logs detallados durante la ejecución del playbook.
- **Protección de archivos sensibles**: Asegúrate de cifrar `vars/credentials.yaml` después de modificarlo para garantizar la seguridad de la información.
