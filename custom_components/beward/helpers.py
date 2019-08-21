"""Helpers for Beward device component."""

from . import DOMAIN


def service_signal(service, ident=None):
    """Encode service and identifier into signal."""
    signal = "{}_{}".format(DOMAIN, service)
    if ident:
        signal += "_{}".format(ident.replace(".", "_"))
    return signal
