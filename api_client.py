"""Client API Claude pour le traitement du texte."""

import os
from anthropic import Anthropic, APIError, APIConnectionError

from config import MODEL, PROMPTS


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


def process_text(text: str, action: str) -> str:
    """
    Traite le texte avec l'API Claude selon l'action demandée.

    Args:
        text: Le texte à traiter.
        action: L'action à effectuer ('correct', 'format', 'reformulate', 'professional').

    Returns:
        Le texte traité.

    Raises:
        APIClientError: En cas d'erreur API.
    """
    if action not in PROMPTS:
        raise APIClientError(f"Action inconnue : {action}")

    prompt = PROMPTS[action].format(text=text)

    try:
        client = get_client()
        response = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )
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
