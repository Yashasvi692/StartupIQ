from fastapi import Request

from backend.pipeline.validation_pipeline import ValidationPipeline

_pipeline: ValidationPipeline | None = None


def get_pipeline(request: Request) -> ValidationPipeline:
    global _pipeline
    try:
        return request.app.state.pipeline
    except (AttributeError, KeyError):
        if _pipeline is None:
            _pipeline = ValidationPipeline()
        return _pipeline
