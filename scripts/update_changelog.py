from dotenv import load_dotenv
import os
import re
from jira import JIRA
import subprocess

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Configuración de Jira
JIRA_URL = os.getenv('JIRA_URL')
JIRA_USERNAME = os.getenv('JIRA_USERNAME')
JIRA_API_TOKEN = os.getenv('JIRA_API_TOKEN')

# Ruta al archivo changelog
CHANGELOG_FILE = 'CHANGELOG.md'

# Expresión regular para extraer el identificador de la tarea de Jira del nombre del branch
# BRANCH_PATTERN = r'^(?:feature|bugfix|task)\/([A-Z]+-\d+)-.*$'
BRANCH_PATTERN = r'^(?:feature|bugfix|task)\/([A-Z]+-\d+)$'

# Conexión a Jira
jira = JIRA(server=JIRA_URL, basic_auth=(JIRA_USERNAME, JIRA_API_TOKEN))

# Obtener el nombre del branch actual
output = subprocess.check_output(['git', 'symbolic-ref', '--short', 'HEAD']).decode().strip()
current_branch = output.splitlines()[0]

print(f'Nombre del branch actual: {current_branch}')

# Extraer el identificador de la tarea de Jira del nombre del branch
match = re.match(BRANCH_PATTERN, current_branch)
if match:
    issue_key = match.group(1)
else:
    print(f'El nombre del branch "{current_branch}" no coincide con el patrón esperado.')
    exit(1)

# Obtener información de la tarea de Jira
try:
    issue = jira.issue(issue_key)
    issue_summary = issue.fields.summary
    issue_description = issue.fields.description
    issue_url = f'{JIRA_URL}/browse/{issue_key}'
except Exception as e:
    print(f'Error al obtener información de la tarea de Jira: {str(e)}')
    exit(1)

# Verificar si el registro de la tarea ya existe en el CHANGELOG
changelog_entry = f'[[{issue_key}]]'
commit_added = False

try:
    with open(CHANGELOG_FILE, 'r') as file:
        lines = file.readlines()

    if not any(changelog_entry in line for line in lines):
        # Construir la entrada del changelog
        changelog_entry = f'- [[{issue_key}]]({issue_url}) - {issue_summary}\n'

        # Actualizar el changelog con la nueva entrada
        with open(CHANGELOG_FILE, 'a') as file:
            file.write(changelog_entry)
            print(f'Changelog actualizado para la tarea {issue_key}')
    else:
        print(f'El registro de la tarea {issue_key} ya existe en el changelog.')

    # Hacer un git add para agregar los cambios al área de preparación (stage)
    subprocess.run(['git', 'add', CHANGELOG_FILE])
except Exception as e:
    print(f'Error al actualizar el changelog: {str(e)}')
    exit(1)


