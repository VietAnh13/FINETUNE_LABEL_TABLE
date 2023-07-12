import os
import json
import shutil
import xml.etree.ElementTree as ET

from config import *
from glob import glob


errors = []
CONST_K = 1000000

def join_path(base_path, relative_path):
    return os.path.join(base_path, relative_path)

def format_folder(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.mkdir(path)

def get_sample_list_from_path(path, sample_format):
    if os.path.exists(path):
        return glob(join_path(path, f'*{sample_format}'))

def get_sample_name_from_sample(sample, sample_format):
    base_name = os.path.basename(sample)
    sample_name = os.path.splitext(base_name)[0]
    sample_name_and_sample_format = f'{sample_name}.{sample_format}'
    return sample_name_and_sample_format 
    
def get_tree_and_root_from_file_xml(path):
    tree = ET.parse(path)
    return tree, tree.getroot()

def get_class_list_from_root(root, class_name):
    return root.findall(f'.//object[name="{class_name}"]')

def get_object_list_not_include_class_from_root(root, class_name):
    return [object for object in root.findall('.//object') if object.find('name').text != class_name]

def get_element_from_bounding_box_object_with_name(object, element_name):
    return object.find('bndbox').find(element_name)

def get_bounding_box_object(object):
    return {e.tag : int(e.text) for e in object.find('bndbox')}

def sort_object_list_by_element_value(object_list, element_name):
    # length = len(object_list)
    # for i in range(length):
    #     object_min = object_i = object_list[i]
    #     print(get_bounding_box_object(object_min)[element_name])
    # print('------------------------------------------------------------------')
    
    object_list[:] = sorted(object_list, key=lambda object_list: get_bounding_box_object(object_list)[element_name])
    # object_list_true = []
    # length = len(object_list)
    
    # for i in range(length):
    #     object_min = object_i = object_list[i]
    #     print(get_bounding_box_object(object_min)[element_name])
    # print('------------------------------------------------------------------')
    # for i in range(length - 1):
    #     object_min = object_i = copy.deepcopy(object_list[i])
    #     element_value_object_min = get_bounding_box_object(object_min)[element_name]
    #     for j in range(i + 1, length, 1):
    #         object_j = copy.deepcopy(object_list[j])
    #         element_value_object_j = get_bounding_box_object(object_j)[element_name]
    #         if element_value_object_j < element_value_object_min:
    #             object_min = object_j
    #     if object_min != object_i:
    #         object_i_buffer = copy.deepcopy(object_i)
    #         object_min_buffer = copy.deepcopy(object_min)
    #         object_min = object_i_buffer
    #         object_i = object_min_buffer
    #         # copy_of_object_i = ET.Element(object_i.tag, object_i.attrib)
    #         # copy_of_object_i.text = object_i.text
    #         # copy_of_object_min = ET.Element(object_min.tag, object_min.attrib)
    #         # copy_of_object_min.text = object_min.text
    #         # object_i.text = copy_of_object_min.text
    #         # object_min.text = copy_of_object_i.text
    # object_list[:] = object_list.copy()
    # print('------------------------------------------------------------------')
    # for i in range(length ):
    #     object_min = object_i = object_list[i]
    #     print(get_bounding_box_object(object_min)[element_name])

def update_element_value_of_object(object, element_name, new_value):
    element = get_element_from_bounding_box_object_with_name(object, element_name)
    element.text = str(new_value)

def get_true_number_of_bounding_box_object(value, element_name, mean_element_value_original_list):
    if 'min' in element_name:
        i = 0
        for mean_element_value_original in mean_element_value_original_list:
            if value <= mean_element_value_original:    
                return int(i)  
            else: 
                i += 1 
    elif 'max' in element_name:
        i = len(mean_element_value_original_list)
        for mean_element_value_original in reversed(mean_element_value_original_list):    
            if value >= mean_element_value_original:
                return int(i - 1)  
            else: 
                i -= 1

def find_element_value_in_element_value_list(value, element_name, element_value_list, mean_element_value_original_list):
    true_number_of_bounding_box_object = get_true_number_of_bounding_box_object(value, element_name, mean_element_value_original_list)
    return element_value_list[true_number_of_bounding_box_object]

def read_txt_file_to_dict(map_file):
    with open(map_file, 'r') as file:
        return json.load(file)
    
def calc_kx_ky_betw_IBT_RAL_imgs(table_IBT, table_RAL):
    xmin_IBT, ymin_IBT, xmax_IBT, ymax_IBT = get_bounding_box_object(table_IBT).values()
    xmin_RAL, ymin_RAL, xmax_RAL, ymax_RAL = get_bounding_box_object(table_RAL).values()

    delta_x_IBT = xmax_IBT - xmin_IBT
    delta_y_IBT = ymax_IBT - ymin_IBT
    delta_x_RAL = xmax_RAL - xmin_RAL
    delta_y_RAL = ymax_RAL - ymin_RAL

    k_x = int(round((delta_x_RAL / delta_x_IBT - 1) * CONST_K))
    k_y = int(round((delta_y_RAL / delta_y_IBT - 1) * CONST_K))

    return k_x, k_y

def calc_match_point_betw_IBT_and_RAL_images(table_IBT, table_RAL):

    k_x, k_y = calc_kx_ky_betw_IBT_RAL_imgs(table_IBT, table_RAL)
    k_ratio = abs(k_x / k_y)
    match_point = int(round(abs(k_ratio - 1) * CONST_K))

    return match_point

def find_best_point(match_point_average):
    len_match_point_avg = len(match_point_average)
    min_point = match_point_average[0]
    key = 0

    for i in range (1, len_match_point_avg, 1):
        if match_point_average[i] < min_point:
            min_point = match_point_average[i]
            key = i
    return key, min_point

def find_IBT_img_match_RAL_img(IBT_list, RAL_list, num_of_table_per_IBT):
    len_bndbox_IBT_list = len(IBT_list)
    num_of_sample_IBT_per_RAL = int(len_bndbox_IBT_list / num_of_table_per_IBT)

    match_point_total = []
    match_point_average = []

    for i in range (num_of_table_per_IBT):
        match_point_per_table = []
        
        for j in range (num_of_sample_IBT_per_RAL):
            index_IBT = j * num_of_table_per_IBT + i
            index_RAL = i
            table_IBT = IBT_list[index_IBT]
            table_RAL = RAL_list[index_RAL]
            
            match_point = calc_match_point_betw_IBT_and_RAL_images(table_IBT, table_RAL)
            match_point_per_table.append(match_point)
        
        match_point_total.append(match_point_per_table)

    for i in range (num_of_sample_IBT_per_RAL):
        match_point_sum = 0
        for j in range (num_of_table_per_IBT):
            match_point_sum += match_point_total[j][i]
        match_point_average.append(int(round(match_point_sum / num_of_table_per_IBT)))
    
    key, min_point = find_best_point(match_point_average)

    return key

def copy_specific_elements_from_source_root_to_dest_root(source_root, dest_root):
    for element in get_object_list_not_include_class_from_root(source_root, CLASS_TABLE):
        dest_root.append(element)
    new_tree = ET.ElementTree(dest_root)
    return new_tree, dest_root

def calc_new_element_value_of_object(table_IBT, table_RAL, element_name, element_value, k_ratio):
    element_IBT_value = get_bounding_box_object(table_IBT)[element_name]
    element_RAL_value = get_bounding_box_object(table_RAL)[element_name]
    
    delta_e = element_value - element_IBT_value
    new_delta_e = int(round((k_ratio + CONST_K) * delta_e / CONST_K))

    new_element_value = element_RAL_value + new_delta_e
    return new_element_value