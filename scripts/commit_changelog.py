import os
import re
from dotenv import load_dotenv
import subprocess

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Ruta al archivo changelog
CHANGELOG_FILE = 'CHANGELOG.md'

# Si SKIP_POST_COMMIT es verdadero, salimos del script inmediatamente
if os.getenv('SKIP_POST_COMMIT') == 'true':
    exit(0)

commit_message = subprocess.check_output(['git', 'log', '-1', '--pretty=%B'], text=True).strip()
commit_message = re.sub(r'\[[A-Z]+-\d+\]\s*', '', commit_message)

try:
    with open(CHANGELOG_FILE, 'r') as file:
        lines = file.readlines()

    with open(CHANGELOG_FILE, 'w') as file:
        for line in lines:
            if "[[" in line and "]]" in line:  # Aquí asumimos que todas las entradas de JIRA comienzan con [[
                file.write(f'{line.rstrip()}\n\t- {commit_message}\n')
            else:
                file.write(line)

    # Hacer un git add para agregar los cambios al área de preparación (stage)
    subprocess.run(['git', 'add', CHANGELOG_FILE])

    # Hacer un segundo commit con el archivo de registro de cambios actualizado
    os.environ['SKIP_POST_COMMIT'] = 'true'
    subprocess.run(['git', 'commit', '--amend', '--no-edit'])
    os.environ['SKIP_POST_COMMIT'] = 'false'
except Exception as e:
    print(f'Error al actualizar el changelog: {str(e)}')
    exit(1)
