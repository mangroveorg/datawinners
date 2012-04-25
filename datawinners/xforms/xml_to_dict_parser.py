import xml.dom.minidom

def xmltodict(xmlstring):
    doc = xml.dom.minidom.parseString(xmlstring)
    document_element = doc.documentElement
    remove_whitespace_nodes(document_element)
    return elementtodict(document_element)

def elementtodict(parent):
    child = parent.firstChild
    if not child:
        return None
    elif child.nodeType == xml.dom.minidom.Node.TEXT_NODE:
        return child.nodeValue

    submission_data_dict={}
    while child is not None:
        if child.nodeType == xml.dom.minidom.Node.ELEMENT_NODE:
            child_tag_name = child.tagName
            try:
                submission_data_dict[child_tag_name]
            except KeyError:
                submission_data_dict[child_tag_name]=[]
            submission_data_dict[child_tag_name].append(elementtodict(child))
        child = child.nextSibling
    return submission_data_dict

def remove_whitespace_nodes(node, unlink=True):
    remove_list = []
    for child in node.childNodes:
        if child.nodeType == xml.dom.Node.TEXT_NODE and not child.data.strip():
            remove_list.append(child)
        elif child.hasChildNodes():
            remove_whitespace_nodes(child, unlink)
    for node in remove_list:
        node.parentNode.removeChild(node)
        if unlink:
            node.unlink()