import os
import xml.etree.ElementTree as ET

def convert_annotation(xml_path, classes):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    image_path = os.path.splitext(xml_path)[0] + '.jpg'
    image_size = root.find('size')
    width = int(image_size.find('width').text)
    height = int(image_size.find('height').text)

    with open(os.path.splitext(xml_path)[0] + '.txt', 'w') as txt_file:
        for obj in root.iter('object'):
            difficult = obj.find('difficult').text
            cls = obj.find('name').text
            if cls not in classes or int(difficult) == 1:
                continue
            cls_id = classes.index(cls)

            bbox = obj.find('bndbox')
            xmin = float(bbox.find('xmin').text)
            ymin = float(bbox.find('ymin').text)
            xmax = float(bbox.find('xmax').text)
            ymax = float(bbox.find('ymax').text)

            x_center = (xmin + xmax) / (2.0 * width)
            y_center = (ymin + ymax) / (2.0 * height)
            x_width = (xmax - xmin) / width
            y_height = (ymax - ymin) / height

            txt_file.write(f"{cls_id} {x_center} {y_center} {x_width} {y_height}\n")

if __name__ == "__main__":
    # 設定你的類別
    classes = ['cat']

    # 設定包含XML檔的資料夾路徑
    xml_folder = r'C:\Users\Ada\Desktop\test\test'

    # 遍歷資料夾中的所有XML檔案，進行轉換
    for filename in os.listdir(xml_folder):
        if filename.endswith('.xml'):
            xml_path = os.path.join(xml_folder, filename)
            convert_annotation(xml_path, classes)
