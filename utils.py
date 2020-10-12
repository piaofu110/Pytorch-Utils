import os
import xml.etree.ElementTree as ET

from xml.dom.minidom import Document


def load_classes(path):
    fp = open(path, 'r')
    names = fp.read().split('\n')[:-1]
    return names


def convert_txt_format(txt_path, isLF):
    """
    :param isLF: True means converting to Unix(LF), False means converting to Windows(CRLF)
    """

    def to_lf(path, isLF, encoding='utf-8'):
        newline = '\n' if isLF else '\r\n'
        tp = 'Unix(LF)' if isLF else 'Windows(CRLF)'

        with open(path, newline=None, encoding=encoding) as infile:
            str_ = infile.readlines()
            with open(path, 'w', newline=newline, encoding=encoding) as outfile:
                outfile.writelines(str_)
                print("file converting success, format: {0}; encoding: {1}; path: {2}".format(tp, encoding, path))
    
    path_list = os.listdir(txt_path)
    for filename in path_list:
        path = os.path.join(txt_path, filename)
        to_lf(path, isLF)


def xml2txt(xml_path, txt_path):
    """
    Converting xml files to txt files. Num in line means [label, cen_x, cen_y, w, h]
    """
    def getBbox(bndbox, str_list):
        bbox = []
        for text in str_list:
            element = bndbox.find(text)
            bbox.append(int(element.text))
        
        return bbox
    
    xml_file = os.listdir(xml_path)
    for xml in xml_file:
        # find the xml path and locate the txt save path
        xml_ = os.path.join(xml_path, xml)
        save_path = os.path.join(txt_path, xml.split('.')[0]+'.txt')
        # os.make(save_path, exist_ok=True)

        tree = ET.parse(xml_)
        root = tree.getroot()

        # obtain height and width
        size = root.find("size")
        height = float(size.find("height").text)
        width = float(size.find("width").text)

        with open(save_path, mode='a+') as fp:

            # obtain the bbox info
            for object in tree.iter(tag="object"):

                # an object occupy a line, first locate the category info
                line = ""
                name = object.find("name").text
                line += str(class_names.index(name))

                # Then locate the bbox info and changes them to [x, y, w, h]
                bndbox = object.find("bndbox")
                bbox = [float(0) for _ in range(4)]
                xmin, ymin, xmax, ymax = getBbox(bndbox, ["xmin", "ymin", "xmax", "ymax"])

                w = xmax - xmin
                h = ymax - ymin
                center_x = xmin + w // 2
                center_y = ymin + h // 2

                bbox[0] = round(center_x / width, 6)
                bbox[1] = round(center_y / height, 6)
                bbox[2] = round(center_x / width, 6)
                bbox[3] = round(center_y / height, 6)

                for box in bbox:
                    line += ' ' + str(box)
                line += '\n'
                fp.writelines(line)

def parse_data_config(path):
    options = dict()

    options['gpus'] = '0, 1, 2, 3'
    options['num_workers'] = '0'

    with open(path, 'r') as fp:
        lines = fp.readlines()

    for line in lines:
        line = line.strip()
        if line == '' or line.startswith('#'):
            continue

        key, value = line.split('=')
        options[key.strip()] = value.strip()

    return options


data_config = parse_data_config("config/ships/702.data")
class_names = load_classes(data_config["name"])
xml2txt("data/ships/xmls", "data/ships/labels")