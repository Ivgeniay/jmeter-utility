from jmx_builder.parsers.elements.base import TreeElementParser
from jmx_builder.models.tree import FtpRequestDefaults
from jmx_builder.parsers.const import *


class FtpRequestDefaultsParser(TreeElementParser):
    @staticmethod
    def parse(xml_content: str) -> FtpRequestDefaults:
        testname = TreeElementParser.extract_attribute(xml_content, ATTR_TESTNAME) or "FTP Request Defaults"
        enabled_attr = TreeElementParser.extract_attribute(xml_content, ATTR_ENABLED)
        enabled = enabled_attr != "false"
        
        element = FtpRequestDefaults(testname=testname, enabled=enabled)
        
        comment = TreeElementParser.extract_simple_prop_value(xml_content, TESTPLAN_COMMENTS)
        if comment:
            element.change_comment(comment)
        
        server = TreeElementParser.extract_simple_prop_value(xml_content, FTPSAMPLER_SERVER)
        if server:
            element.set_server(server)
        
        port = TreeElementParser.extract_simple_prop_value(xml_content, FTPSAMPLER_PORT)
        if port:
            element.set_port(port)
        
        filename = TreeElementParser.extract_simple_prop_value(xml_content, FTPSAMPLER_FILENAME)
        if filename:
            element.set_filename(filename)
        
        localfilename = TreeElementParser.extract_simple_prop_value(xml_content, FTPSAMPLER_LOCALFILENAME)
        if localfilename:
            element.set_localfilename(localfilename)
        
        inputdata = TreeElementParser.extract_simple_prop_value(xml_content, FTPSAMPLER_INPUTDATA)
        if inputdata:
            element.set_inputdata(inputdata)
        
        binarymode = TreeElementParser.extract_simple_prop_value(xml_content, FTPSAMPLER_BINARYMODE)
        if binarymode:
            element.set_binarymode(binarymode.lower() == "true")
        
        saveresponse = TreeElementParser.extract_simple_prop_value(xml_content, FTPSAMPLER_SAVERESPONSE)
        if saveresponse:
            element.set_saveresponse(saveresponse.lower() == "true")
        
        upload = TreeElementParser.extract_simple_prop_value(xml_content, FTPSAMPLER_UPLOAD)
        if upload:
            element.set_upload(upload.lower() == "true")
        
        return element