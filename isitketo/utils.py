import structlog


def get_isitketo_logger(name):
    """This will add a `isitketo` prefix to logger for easy configuration."""

    return structlog.get_logger(f"isitketo.{name}")
