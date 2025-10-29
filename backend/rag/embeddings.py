from langchain_openai import AzureOpenAIEmbeddings

from backend.config import get_settings


def create_embeddings() -> AzureOpenAIEmbeddings:
    """Instantiate an Azure OpenAI embeddings client using environment settings."""

    settings = get_settings()
    return AzureOpenAIEmbeddings(
        azure_deployment=settings.azure_openai_embedding_deployment,
        api_version=settings.azure_openai_api_version,
        azure_endpoint=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_api_key,
    )
