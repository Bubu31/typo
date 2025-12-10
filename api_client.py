"""Client API Claude pour le traitement du texte."""

import os
from anthropic import Anthropic, APIError, APIConnectionError

from config import MODEL
import prompt_manager
import translations
import settings_manager
import usage_tracker


class APIClientError(Exception):
    """Erreur du client API."""
    pass


def get_client() -> Anthropic:
    """
    Crée et retourne un client Anthropic.

    Raises:
        APIClientError: Si la clé API n'est pas configurée.
    """
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        raise APIClientError(
            "Clé API non configurée.\n"
            "Redémarrez l'application pour configurer votre clé."
        )
    return Anthropic(api_key=api_key)


def process_text(text: str, action: str, language: str = None) -> str:
    """
    Traite le texte avec l'API Claude selon l'action demandée.

    Args:
        text: Le texte à traiter.
        action: L'action à effectuer ('correct', 'format', 'reformulate', 'professional').
        language: Code langue (fr, en, es, de). Si None, utilise la langue configurée.

    Returns:
        Le texte traité.

    Raises:
        APIClientError: En cas d'erreur API.
    """
    # Récupérer la langue configurée si non spécifiée
    if language is None:
        language = settings_manager.get("language", "fr")

    # Essayer d'abord avec prompt_manager (custom prompts ou overrides)
    prompt_template = prompt_manager.get_prompt(action)

    # Si pas trouvé, essayer avec translations (prompts par défaut traduits)
    if prompt_template is None:
        prompt_template = translations.get_prompt(action, language)

    # Si toujours pas trouvé, erreur
    if prompt_template is None:
        raise APIClientError(f"Action inconnue : {action}")

    prompt = prompt_template.format(text=text)

    try:
        client = get_client()
        response = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )

        # Tracker l'utilisation de l'API
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        usage_tracker.track_request(input_tokens, output_tokens)

        return response.content[0].text

    except APIConnectionError as e:
        raise APIClientError(
            "Impossible de se connecter à l'API Claude.\n"
            "Vérifiez votre connexion internet."
        ) from e

    except APIError as e:
        raise APIClientError(
            f"Erreur API Claude : {e.message}"
        ) from e

    except Exception as e:
        raise APIClientError(
            f"Erreur inattendue : {str(e)}"
        ) from e
