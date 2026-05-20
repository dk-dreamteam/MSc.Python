import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'cityreport-secret-key')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'postgresql://sa:77java&&@db:5432/cityreport'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    AZURITE_CONNECTION_STRING = os.environ.get(
        'AZURITE_CONNECTION_STRING',
        'DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;'
        'AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq'
        '/K1SZFPTOtr/KBHBeksoGMGw==;'
        'BlobEndpoint=http://azurite:10000/devstoreaccount1;'
    )
    AZURITE_CONTAINER_NAME = os.environ.get('AZURITE_CONTAINER_NAME', 'photos')

    GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
    GROQ_MODEL = os.environ.get('GROQ_MODEL', 'mixtral-8x7b-32768')

    NTFY_TOPIC = os.environ.get('NTFY_TOPIC', 'cityreport-notifications')
    NTFY_URL = os.environ.get('NTFY_URL', 'https://ntfy.sh')
