from isitketo.utils import get_isitketo_logger

logger = get_isitketo_logger(__name__)


def create_product(product_name: str):
    logger.info("Creating Product", product_name=product_name)
    return
