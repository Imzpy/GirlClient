from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QListWidget

RESULT = "result"
COMMAND = "command"
CLASSLIST = "classes"
REFRESH_ALL_CLASS = "GET_ALL_CLASS"

#由类名获取方法
REFRESH_ALL_METHODS = "GET_ALL_METHODS"
CLASSNAME = "class_name"
METHODS = "methods"

GET_ALL_HOOKS = "GET_ALL_HOOKS"



def message_handler(ui, json_Data):
    print(json_Data)
    if json_Data[RESULT] != 1:
        return False
    if json_Data[COMMAND] == REFRESH_ALL_CLASS:
        classname_list = json_Data[CLASSLIST]
        ui.classnameorg_model.setStringList(classname_list)
    if json_Data[COMMAND] == REFRESH_ALL_METHODS:
        methods_list = json_Data[METHODS]
        ui.methodsorg_model.setStringList(methods_list)
        ui.tip_classname.setText('类名:' + json_Data[CLASSNAME])
        ui.tip_classname.setToolTip('类名:' + json_Data[CLASSNAME])
    return True


