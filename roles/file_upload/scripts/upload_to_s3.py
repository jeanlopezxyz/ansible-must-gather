import argparse
import boto3
from botocore.config import Config
import logging
import os
import sys

# Configuración de logging
log_file = "upload_to_s3.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger()

# Configuración de argumentos
def parse_arguments():
    parser = argparse.ArgumentParser(description="Upload a file to S3 with metadata.")
    parser.add_argument("--bucket-name", required=True, help="S3 bucket name")
    parser.add_argument("--file-name", required=True, help="Name of the file to upload")
    parser.add_argument("--key", required=True, help="S3 object key")
    parser.add_argument("--access-key", required=True, help="AWS access key")
    parser.add_argument("--secret-key", required=True, help="AWS secret key")
    parser.add_argument("--session-token", required=True, help="AWS session token")
    parser.add_argument("--region", required=True, help="AWS region")
    parser.add_argument("--file-size", required=True, help="Size of the file in bytes")
    return parser.parse_args()

# Verificar existencia del archivo
def validate_file(file_name):
    if not os.path.isfile(file_name):
        logger.error(f"El archivo '{file_name}' no existe.")
        sys.exit(1)

# Crear sesión AWS
def create_aws_session(access_key, secret_key, session_token):
    try:
        session = boto3.session.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            aws_session_token=session_token,
        )
        logger.debug("AWS Session created successfully.")
        return session
    except Exception as e:
        logger.error("Error creating AWS session.", exc_info=True)
        sys.exit(1)

# Crear cliente S3
def create_s3_client(session, region):
    try:
        s3 = session.client(
            "s3",
            region_name=region,
            config=Config(signature_version="s3v4"),
        )
        logger.debug("S3 client created successfully.")
        return s3
    except Exception as e:
        logger.error("Error creating S3 client.", exc_info=True)
        sys.exit(1)

# Subir archivo con metadatos
def upload_file_to_s3(s3_client, bucket_name, file_name, key, file_size):
    try:
        s3_client.upload_file(
            Filename=file_name,
            Bucket=bucket_name,
            Key=key,
            ExtraArgs={
                "ContentType": "application/octet-stream",
                "Metadata": {
                    "x-amz-meta-filename": file_name,
                    "x-amz-meta-bytelength": file_size,
                    "x-amz-meta-content-type": "application/gzip"
                }
            },
        )
        logger.info(f"Archivo '{file_name}' subido correctamente a '{bucket_name}/{key}'.")
    except Exception as e:
        logger.error("Error al subir el archivo.", exc_info=True)
        sys.exit(1)

# Main
if __name__ == "__main__":
    args = parse_arguments()

    # Log de argumentos recibidos
    logger.debug("Received Arguments:")
    for arg, value in vars(args).items():
        logger.debug(f"{arg}: {value}")

    # Validar archivo
    validate_file(args.file_name)

    # Crear sesión y cliente AWS
    session = create_aws_session(args.access_key, args.secret_key, args.session_token)
    s3_client = create_s3_client(session, args.region)

    # Subir archivo a S3
    upload_file_to_s3(
        s3_client=s3_client,
        bucket_name=args.bucket_name,
        file_name=args.file_name,
        key=args.key,
        file_size=args.file_size,
    )

    logger.info(f"Logs guardados en: {os.path.abspath(log_file)}")
