from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QListWidget

RESULT = "result"
COMMAND = "command"
CLASSLIST = "classes"
REFRESH_ALL_CLASS = "GET_ALL_CLASS"

#由类名获取方法
REFRESH_ALL_METHODS = "GET_ALL_METHODS"
CLASSNAME = "class_name"
METHODS = "methods"

#安装hook
INSTALL_HOOK = "INSTALL_HOOK"
INSTALLED_HOOK_INFO = "installed_hook_info"

#获取所有hook信息
GET_ALL_HOOKS = "GET_ALL_HOOKS"
HOOKS = "hooks"


#LOG
TCPLOG = "TCP_Log"
LOGCONTENT = "logs"

#卸载Hook
UNINSTALL_HOOK = "UNINSTALL_HOOK"
UNINSTALL_FULLNAME = "UNINSTALL_FULLNAME"

#dump
DUMP_DEX = "DUMP_DEX"

def message_handler(mainapp, json_Data):
    print(json_Data)
    if json_Data[RESULT] == 0:
        return False
    if json_Data[COMMAND] == REFRESH_ALL_CLASS:
        classname_list = json_Data[CLASSLIST]
        mainapp.ui.classnameorg_model.setStringList(classname_list)
    if json_Data[COMMAND] == REFRESH_ALL_METHODS:
        methods_list = json_Data[METHODS]
        mainapp.ui.methodsorg_model.setStringList(methods_list)
        mainapp.ui.tip_classname.setText('类名:' + json_Data[CLASSNAME])
        mainapp.ui.tip_classname.setToolTip('类名:' + json_Data[CLASSNAME])
        mainapp.operating_class_name = json_Data[CLASSNAME]
    if json_Data[COMMAND] == INSTALL_HOOK:
        #安装hook的结果
        json_Data.pop(RESULT)
        installed_hook = json_Data[INSTALLED_HOOK_INFO]
        do_add = True
        index = 0
        target_index = 0
        for installed_one in mainapp.installed_hookList:
            if installed_one['org_fullname'] == installed_hook['org_fullname']:
                do_add = False
                target_index = index
            index+=1
        if do_add:
            mainapp.installed_hookList.append(installed_hook)
        else:
            mainapp.installed_hookList[target_index] = installed_hook
        mainapp.show_installed_hooks()
    if json_Data[COMMAND] == GET_ALL_HOOKS:
        arr = json_Data[HOOKS]
        mainapp.installed_hookList = arr
        mainapp.show_installed_hooks()
    if json_Data[COMMAND] == UNINSTALL_HOOK:
        #卸载hook的结果
        fullename = json_Data[UNINSTALL_FULLNAME]
        target_index = 0
        index = 0
        for hook in mainapp.installed_hookList:
            if hook['org_fullname'] == fullename:
                target_index = index
                break
            index+=1
        del mainapp.installed_hookList[target_index]
        mainapp.show_installed_hooks()
        
    if json_Data[COMMAND] == TCPLOG:
        logcontent = json_Data[LOGCONTENT]
        mainapp.safe_append_log(logcontent)
    
    return True


