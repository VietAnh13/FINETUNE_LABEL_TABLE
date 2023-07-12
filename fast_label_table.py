from utils import *

# Enter name of folder contain image base type (IBT) & image raw auto label (RAL) 
IMAGE_IBT_FOLDER_NAME = 'image base type'
IMAGE_RAL_FOLDER_NAME = 'image raw auto label'

# Enter name of folder contain image auto label (IAL)
IMAGE_IAL_FOLDER_NAME = 'image auto label'

BASE_ADDR = os.getcwd()
IBT_ADDR = join_path(BASE_ADDR, IMAGE_IBT_FOLDER_NAME)
RAL_ADDR = join_path(BASE_ADDR, IMAGE_RAL_FOLDER_NAME)
IAL_ADDR = join_path(BASE_ADDR, IMAGE_IAL_FOLDER_NAME)

MAP_FILE_IBT_TO_RAL = 'ibt_to_ral_map.txt'
MAP_ADDR = join_path(BASE_ADDR, MAP_FILE_IBT_TO_RAL)

# Read map file from IBT to RAL
map_file = read_txt_file_to_dict(MAP_ADDR)

for ibt_fol, ral_fol in map_file.items():

    IBT_TYPE_X_ADDR = join_path(IBT_ADDR, ibt_fol)
    RAL_TYPE_X_ADDR = join_path(RAL_ADDR, ral_fol)

    # Get image list & label list of IBT & RAL
    label_IBT_list = get_sample_list_from_path(IBT_TYPE_X_ADDR, LABEL_FORMAT)
    label_RAL_list = get_sample_list_from_path(RAL_TYPE_X_ADDR, LABEL_FORMAT)

    IBT_list = []
    num_of_table_per_IBT = 0
    flag_update_num_of_table_per_IBT = False    
    
    for label_IBT in label_IBT_list:

        # Get tree & root from file .xml
        IBT_tree, IBT_root = get_tree_and_root_from_file_xml(label_IBT)

        # Get table list
        tabel_IBT_list = get_class_list_from_root(IBT_root, CLASS_TABLE)

        if flag_update_num_of_table_per_IBT != True:
            num_of_table_per_IBT = len(tabel_IBT_list)
            flag_update_num_of_table_per_IBT = True

        for table_IBT in tabel_IBT_list:

            # Get bounding_box of table
            IBT_list.append(table_IBT)

    # Refresh image auto label folder
    TYPE_IAL_ADDR = join_path(IAL_ADDR, ral_fol)
    format_folder(TYPE_IAL_ADDR)    

    for label_RAL in label_RAL_list:

        RAL_list = []

        label_name_RAL = get_sample_name_from_sample(label_RAL, LABEL_FORMAT)

        # Get tree & root from file .xml
        RAL_tree, RAL_root = get_tree_and_root_from_file_xml(label_RAL)

        # Get table list
        tabel_RAL_list = get_class_list_from_root(RAL_root, CLASS_TABLE)

        for table_RAL in tabel_RAL_list:

            # Get bounding_box of table
            RAL_list.append(table_RAL)
        
        # Find which IBT image matches the RAL image best
        match_index = find_IBT_img_match_RAL_img(IBT_list, RAL_list, num_of_table_per_IBT)
        
        # Parse the match IBT XML file
        match_IBT_tree_ = ET.parse(label_IBT_list[match_index])
        match_IBT_root = match_IBT_tree_.getroot()
        
        # Copy specific elements from the source root to the destination root
        RAL_tree, RAL_root = copy_specific_elements_from_source_root_to_dest_root(match_IBT_root, RAL_root)

        # Calculate new value for all class
        for i in range (num_of_table_per_IBT):
            index_IBT = match_index * num_of_table_per_IBT + i
            index_RAL = i
            table_IBT = IBT_list[index_IBT]
            table_RAL = RAL_list[index_RAL]
            
            # kx, ky
            k_x, k_y = calc_kx_ky_betw_IBT_RAL_imgs(table_IBT, table_RAL)

            # get xmin, ymin, xmax, ymax of table
            xmin_table, ymin_table, xmax_table, ymax_table = get_bounding_box_object(table_RAL).values()

            # need fix for multi table in one image
            # because the class is same level, we need find what class is 'in' class 'table'
            # code below is used for one table per image
            # TODO: write function get all class_name is 'in' class 'table'

            # Get table_row list and sort
            table_row_list = get_class_list_from_root(RAL_tree, CLASS_TABLE_ROW)
            sort_object_list_by_element_value(table_row_list, Y_MIN)

            # Get table_column list and sort
            table_column_list = get_class_list_from_root(RAL_tree, CLASS_TABLE_COLUMN)
            sort_object_list_by_element_value(table_row_list, X_MIN)

            # Get table_projected_row_header list and sort
            table_projected_row_header_list = get_class_list_from_root(RAL_tree, CLASS_TABLE_PROJECTED_ROW_HEADER)
            sort_object_list_by_element_value(table_projected_row_header_list, Y_MIN)

            # Get table_spanning_cell list
            table_spanning_cell_list = get_class_list_from_root(RAL_tree, CLASS_TABLE_SPANNING_CELL)
            
            # Get table_column_header list
            table_column_header_list = get_class_list_from_root(RAL_tree, CLASS_TABLE_COLUMN_HEADER)

            # code below from line 115 to 128 is use tuning follow bounding box table
            # maybe change to use k_ratio to calculate new value

            # Tuning xmin & xmax of all table_row by xmin & xmax of table
            for table_row in table_row_list:
                update_element_value_of_object(table_row, X_MIN, xmin_table)
                update_element_value_of_object(table_row, X_MAX, xmax_table)

            # Tuning ymin & ymax of all table_column by ymin & ymax of table
            for table_column in table_column_list:
                update_element_value_of_object(table_column, Y_MIN, ymin_table)
                update_element_value_of_object(table_column, Y_MAX, ymax_table)

            # Tuning xmin & xmax of all table_projected_row_header by xmin & xmax of table
            for table_projected_row_header in table_projected_row_header_list:
                update_element_value_of_object(table_projected_row_header, X_MIN, xmin_table)
                update_element_value_of_object(table_projected_row_header, X_MAX, xmax_table)


            ## UPDATE YMIN & YMAX OF ALL TABLE_ROW ##

            for table_row in table_row_list:

                # get ymin & ymax
                ymin_table_row = get_bounding_box_object(table_row)[Y_MIN]
                ymax_table_row = get_bounding_box_object(table_row)[Y_MAX]

                new_ymin_table_row = calc_new_element_value_of_object(table_IBT, table_RAL, Y_MIN, ymin_table_row, k_y)
                new_ymax_table_row = calc_new_element_value_of_object(table_IBT, table_RAL, Y_MAX, ymax_table_row, k_y)

                # update ymin & ymax of table_row value
                update_element_value_of_object(table_row, Y_MIN, new_ymin_table_row)
                update_element_value_of_object(table_row, Y_MAX, new_ymax_table_row)

       
            ## UPDATE XMIN & XMAX OF ALL TABLE_COLUMN ##

            for table_column in table_column_list:

                # get xmin & xmax
                xmin_table_column = get_bounding_box_object(table_column)[X_MIN]
                xmax_table_column = get_bounding_box_object(table_column)[X_MAX]

                new_xmin_table_column = calc_new_element_value_of_object(table_IBT, table_RAL, X_MIN, xmin_table_column, k_x)
                new_xmax_table_column = calc_new_element_value_of_object(table_IBT, table_RAL, X_MAX, xmax_table_column, k_x)

                # update xmin & xmax of table_column value
                update_element_value_of_object(table_column, X_MIN, new_xmin_table_column)
                update_element_value_of_object(table_column, X_MAX, new_xmax_table_column)


            ## UPDATE YMIN & YMAX OF ALL TABLE_PROJECTED_ROW_HEADER ##  

            for table_projected_row_header in table_projected_row_header_list:

                # get ymin & ymax
                ymin_table_projected_row_header = get_bounding_box_object(table_projected_row_header)[Y_MIN]
                ymax_table_projected_row_header = get_bounding_box_object(table_projected_row_header)[Y_MAX]

                new_ymin_table_projected_row_header = calc_new_element_value_of_object(table_IBT, table_RAL, Y_MIN, ymin_table_projected_row_header, k_y)
                new_ymax_table_projected_row_header = calc_new_element_value_of_object(table_IBT, table_RAL, Y_MAX, ymax_table_projected_row_header, k_y)

                # update ymin & ymax of table_projected_row_header value
                update_element_value_of_object(table_projected_row_header, Y_MIN, new_ymin_table_projected_row_header)
                update_element_value_of_object(table_projected_row_header, Y_MAX, new_ymax_table_projected_row_header)

        
            ## UPDATE XMIN & XMAX & YMIN & YMAX OF ALL TABLE_SPANNING_CELL ##

            for table_spanning_cell in table_spanning_cell_list:

                # get xmin & xmax & ymin & ymax
                xmin_table_spanning_cell = get_bounding_box_object(table_spanning_cell)[X_MIN]
                xmax_table_spanning_cell = get_bounding_box_object(table_spanning_cell)[X_MAX]
                ymin_table_spanning_cell = get_bounding_box_object(table_spanning_cell)[Y_MIN]
                ymax_table_spanning_cell = get_bounding_box_object(table_spanning_cell)[Y_MAX]

                new_xmin_table_spanning_cell = calc_new_element_value_of_object(table_IBT, table_RAL, X_MIN, xmin_table_spanning_cell, k_x)
                new_xmax_table_spanning_cell = calc_new_element_value_of_object(table_IBT, table_RAL, X_MAX, xmax_table_spanning_cell, k_x)
                new_ymin_table_spanning_cell = calc_new_element_value_of_object(table_IBT, table_RAL, Y_MIN, ymin_table_spanning_cell, k_y)
                new_ymax_table_spanning_cell = calc_new_element_value_of_object(table_IBT, table_RAL, Y_MAX, ymax_table_spanning_cell, k_y)

                # update xmin & xmax & ymin & ymax table_spanning_cell value
                update_element_value_of_object(table_spanning_cell, X_MIN, new_xmin_table_spanning_cell)
                update_element_value_of_object(table_spanning_cell, X_MAX, new_xmax_table_spanning_cell)
                update_element_value_of_object(table_spanning_cell, Y_MIN, new_ymin_table_spanning_cell)
                update_element_value_of_object(table_spanning_cell, Y_MAX, new_ymax_table_spanning_cell)


            ## UPDATE XMIN & XMAX & YMIN & YMAX OF ALL TABLE_COLUMN_HEADER ##

            for table_column_header in table_column_header_list:

                # get xmin & xmax & ymin & ymax
                xmin_table_column_header = get_bounding_box_object(table_column_header)[X_MIN]
                xmax_table_column_header = get_bounding_box_object(table_column_header)[X_MAX]
                ymin_table_column_header = get_bounding_box_object(table_column_header)[Y_MIN]
                ymax_table_column_header = get_bounding_box_object(table_column_header)[Y_MAX]

                new_xmin_table_column_header = calc_new_element_value_of_object(table_IBT, table_RAL, X_MIN, xmin_table_column_header, k_x)
                new_xmax_table_column_header = calc_new_element_value_of_object(table_IBT, table_RAL, X_MAX, xmax_table_column_header, k_x)
                new_ymin_table_column_header = calc_new_element_value_of_object(table_IBT, table_RAL, Y_MIN, ymin_table_column_header, k_y)
                new_ymax_table_column_header = calc_new_element_value_of_object(table_IBT, table_RAL, Y_MAX, ymax_table_column_header, k_y)

                # update xmin & xmax & ymin & ymax table_column_header value
                update_element_value_of_object(table_column_header, X_MIN, new_xmin_table_column_header)
                update_element_value_of_object(table_column_header, X_MAX, new_xmax_table_column_header)
                update_element_value_of_object(table_column_header, Y_MIN, new_ymin_table_column_header)
                update_element_value_of_object(table_column_header, Y_MAX, new_ymax_table_column_header)
        
        
        RAL_tree.write(join_path(TYPE_IAL_ADDR, label_name_RAL))


## NOTE: IDEA ##
# (1) Get root of image base type
# (2) Get root of image raw auto label
# (3) Calculate ratio_x = rx, ratio_y = ry between table (IBT) & table (RAL)
# (4) Recalculate all table row, column, column header, projected row header, spanning cell of table RAL (using root of table IBT)
# (5) Save result with name of table RAL
## PROJECT HOON
