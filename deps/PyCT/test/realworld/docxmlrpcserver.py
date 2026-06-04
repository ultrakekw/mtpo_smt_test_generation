#######################################################################################
# Remember to modify the source code of line 898 in /usr/lib/python3.8/xmlrpc/server.py
# from: return documenter.page(html.escape(self.server_title), documentation)
#   to: return documenter.page(self.server_title, documentation)
# in order to make this example work! The following code segment has done it for us.
import html, os
html.escape = lambda x: x # disable the functionality
if 'INITIAL_PORT' not in os.environ: os.environ['INITIAL_PORT'] = '8081'
#######################################################################################

from xmlrpc.server import DocXMLRPCServer

def docxmlrpcserver(title, name, documentation):
    p = int(os.environ['INITIAL_PORT']) # avoid starting the server on the same port by PyExZ3
    serv = DocXMLRPCServer(("localhost", p), logRequests=False)
    serv.set_server_title(title) #"DocXMLRPCServer Test Documentation")
    serv.set_server_name(name) #"DocXMLRPCServer Test Docs")
    serv.set_server_documentation(documentation) #"This is an XML-RPC server's documentation")
    serv.register_introspection_functions()
    serv.register_multicall_functions()
    serv.register_function(lambda x, y: x + y)
    serv.register_instance(DocXMLRPCServer(("localhost", p+1)))
    generated = serv.generate_html_documentation()
    os.environ["INITIAL_PORT"] = str(p+2)
    if '<script>' in generated:
        return 'dangerous'
    else:
        return 'safe'
