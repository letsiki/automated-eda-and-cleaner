from .log_setup.setup import setup, logging

logger = logging.getLogger(__name__)
setup(logger)

def generate_plots(df):
    """
    This need to be able to generate plots in a folder
    but needs to be used in a jupyter notebook context also
    """
    pass