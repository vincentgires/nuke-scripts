import nukescripts
from connection_manager import ConnectionManagerWidget  # noqa: F401

nukescripts.panels.registerWidgetAsPanel(
    'ConnectionManagerWidget', 'Connection Manager', 'ConnectionManagerWindow')
