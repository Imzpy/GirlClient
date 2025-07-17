
local info = {"h.y.c.e0.c1","a","LL", true,0}
local test = createJavaString("test",0)
local args = {test}
local ret = call_java_function(info, args)
print(type(ret))
print(ret)
return ret
