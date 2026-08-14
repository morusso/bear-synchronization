import argparse


class ColorHelpFormatter(argparse.RawDescriptionHelpFormatter, argparse.ArgumentDefaultsHelpFormatter):
    """Help formatter that preserves description formatting and shows argument defaults."""
