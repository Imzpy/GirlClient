from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QListWidget

RESULT = "result"
COMMAND = "command"
CLASSLIST = "classes"
REFRESH_ALL_CLASS = "GET_ALL_CLASS"
GET_ALL_HOOKS = "GET_ALL_HOOKS"


def message_handler(ui, json_Data):
    if json_Data[RESULT] != 1:
        return False
    if json_Data[COMMAND] == REFRESH_ALL_CLASS:
        classname_list = json_Data[CLASSLIST]
        ui.classnameorg_model.setStringList(classname_list)

