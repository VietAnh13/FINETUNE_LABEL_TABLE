from utils import *

# Enter name of folder contain image source (SRC) & image dest (DST)
IMAGE_SRC_FOLDER_NAME = 'image test'
IMAGE_DST_FOLDER_NAME = 'image result'

BASE_ADDR = os.getcwd()
SRC_ADDR = join_path(BASE_ADDR, IMAGE_SRC_FOLDER_NAME)
DST_ADDR = join_path(BASE_ADDR, IMAGE_DST_FOLDER_NAME)

# Refresh image dest folder
format_folder(DST_ADDR)

# Get image list & label list
image_list = get_sample_list_from_path(SRC_ADDR, IMAGE_FORMAT)
label_list = get_sample_list_from_path(SRC_ADDR, LABEL_FORMAT)

errors = []
num_processed = 0

#if image_list.size() != label_list.size():

for label in label_list:   

    label_name = get_sample_name_from_sample(label, LABEL_FORMAT)
    #print(label_name)

    # Get tree & root from file .xml
    tree, root = get_tree_and_root_from_file_xml(label)

    # Get table list
    tabel_list = get_class_list_from_root(root, CLASS_TABLE)

    for table in tabel_list:
        
        # Get xmin, ymin, xmax, ymax of table
        xmin_table, ymin_table, xmax_table, ymax_table = get_bounding_box_object(table).values()

        # Get table_row list and sort
        table_row_list = get_class_list_from_root(tree, CLASS_TABLE_ROW)
        sort_object_list_by_element_value(table_row_list, Y_MIN)

        # Get table_column list and sort
        table_column_list = get_class_list_from_root(tree, CLASS_TABLE_COLUMN)
        sort_object_list_by_element_value(table_column_list, X_MIN)

        # Get table_projected_row_header list and sort
        table_projected_row_header_list = get_class_list_from_root(tree, CLASS_TABLE_PROJECTED_ROW_HEADER)
        sort_object_list_by_element_value(table_projected_row_header_list, Y_MIN)

        # Get table_spanning_cell list
        table_spanning_cell_list = get_class_list_from_root(tree, CLASS_TABLE_SPANNING_CELL)
        
        # Get table_column_header list
        table_column_header_list = get_class_list_from_root(tree, CLASS_TABLE_COLUMN_HEADER)

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


        ## TUNING YMIN & YMAX OF ALL TABLE_ROW ##
      
        # Get length of table_row list
        length_table_row_list = len(table_row_list)
        
        # List ymin & ymax of all table_row
        ymin_original_table_row_list = []
        ymin_after_tuning_table_row_list = []
        ymax_original_table_row_list = []
        ymax_after_tuning_table_row_list = []

        # List mean_y original
        mean_y_original_table_row_list = []
        
        # Tuning ymin first table_row
        first_table_row = table_row_list[0]
        ymin_original_table_row_list.append(get_bounding_box_object(first_table_row)[Y_MIN])
        update_element_value_of_object(first_table_row, Y_MIN, ymin_table)
        ymin_after_tuning_table_row_list.append(ymin_table)
        
        # Tuning ymax of table_row[i] & ymin of table_row[j] with j = i + 1
        for i in range(length_table_row_list - 1):

            # get ymax_i & ymin_j
            ymax_table_row_i = get_bounding_box_object(table_row_list[i])[Y_MAX]
            ymin_table_row_j = get_bounding_box_object(table_row_list[i + 1])[Y_MIN]
            
            # mean_y = (ymax_i + ymin_j) / 2
            mean_y = int(round((ymax_table_row_i + ymin_table_row_j) / 2))

            # save ymin & ymax original of table_row
            ymin_original_table_row_list.append(ymin_table_row_j)
            ymax_original_table_row_list.append(ymax_table_row_i)
            
            # update ymin & ymax of table_row value
            update_element_value_of_object(table_row_list[i], Y_MAX, mean_y)
            update_element_value_of_object(table_row_list[i + 1], Y_MIN, mean_y)
            
            # save ymin & ymax after tuning of table_row
            ymin_after_tuning_table_row_list.append(mean_y)
            ymax_after_tuning_table_row_list.append(mean_y)

        # Tuning ymax last table_row
        last_table_row = table_row_list[length_table_row_list - 1]
        ymax_original_table_row_list.append(get_bounding_box_object(last_table_row)[Y_MAX])
        update_element_value_of_object(last_table_row, Y_MAX, ymax_table)
        ymax_after_tuning_table_row_list.append(ymax_table)

        # Update mean_y original list
        for i in range (length_table_row_list):
            mean_y_original = int(round((ymin_original_table_row_list[i] + ymax_original_table_row_list[i]) / 2))
            mean_y_original_table_row_list.append(mean_y_original)
        

        ## TUNING XMIN & XMAX OF ALL TABLE_COLUMN ##
        
        # Get length of table_column_list
        length_table_column_list = len(table_column_list)
        
        # List xmin & xmax of all table column
        xmin_original_table_column_list = []
        xmin_after_tuning_table_column_list = []
        xmax_original_table_column_list = []
        xmax_after_tuning_table_column_list = []

        # List mean_x original
        mean_x_original_table_column_list = []

        # Tuning xmin first table column
        first_table_column = table_column_list[0]
        xmin_original_table_column_list.append(get_bounding_box_object(first_table_column)[X_MIN])
        update_element_value_of_object(first_table_column, X_MIN, xmin_table)
        xmin_after_tuning_table_column_list.append(xmin_table)
        
        # Tuning xmax of table_column[i] & xmin of table_column[j] with j = i + 1
        for i in range(length_table_column_list - 1):
            
            # get xmax_i & xmin_j
            xmax_table_column_i = get_bounding_box_object(table_column_list[i])[X_MAX]
            xmin_table_column_j = get_bounding_box_object(table_column_list[i + 1])[X_MIN]
            
            # mean_x = (xmax_i + xmin_j) / 2
            mean_x = int(round((xmax_table_column_i + xmin_table_column_j) / 2))
            
            # save xmin & xmax original of table_column
            xmin_original_table_column_list.append(xmin_table_column_j)
            xmax_original_table_column_list.append(xmax_table_column_i)
            
            # update xmin & xmax of table_column value
            update_element_value_of_object(table_column_list[i], X_MAX, mean_x)
            update_element_value_of_object(table_column_list[i + 1], X_MIN, mean_x)
            
            # save xmin & xmax after tuning of table_row
            xmin_after_tuning_table_column_list.append(mean_x)
            xmax_after_tuning_table_column_list.append(mean_x)

        # Tuning xmax last table column
        last_table_column = table_column_list[length_table_column_list - 1]
        xmax_original_table_column_list.append(get_bounding_box_object(last_table_column)[X_MAX])
        update_element_value_of_object(last_table_column, X_MAX, xmax_table)
        xmax_after_tuning_table_column_list.append(xmax_table)

        # Update mean_x original list
        for i in range (length_table_column_list):
            mean_x_original = int(round((xmin_original_table_column_list[i] + xmax_original_table_column_list[i]) / 2))
            mean_x_original_table_column_list.append(mean_x_original)


        ## TUNING YMIN & YMAX OF ALL TABLE_PROJECTED_ROW_HEADER ##  

        for table_projected_row_header in table_projected_row_header_list:

            # find ymin of table_projected_row_header
            ymin_original_table_projected_row_header = get_bounding_box_object(table_projected_row_header)[Y_MIN]
            new_ymin_table_projected_row_header = find_element_value_in_element_value_list(ymin_original_table_projected_row_header, Y_MIN, ymin_after_tuning_table_row_list, mean_y_original_table_row_list)

            # find ymax of table_projected_row_header
            ymax_original_table_projected_row_header = get_bounding_box_object(table_projected_row_header)[Y_MAX]
            new_ymax_table_projected_row_header = find_element_value_in_element_value_list(ymax_original_table_projected_row_header, Y_MAX, ymax_after_tuning_table_row_list, mean_y_original_table_row_list)

            # update ymin & ymax of table_projected_row_header value
            update_element_value_of_object(table_projected_row_header, Y_MIN, new_ymin_table_projected_row_header)
            update_element_value_of_object(table_projected_row_header, Y_MAX, new_ymax_table_projected_row_header)

        
        ## TUNING XMIN & XMAX & YMIN & YMAX OF ALL TABLE_SPANNING_CELL ##

        for table_spanning_cell in table_spanning_cell_list:

            # find xmin of table_spanning_cell
            xmin_original_table_spanning_cell = get_bounding_box_object(table_spanning_cell)[X_MIN]
            new_xmin_table_spanning_cell = find_element_value_in_element_value_list(xmin_original_table_spanning_cell, X_MIN, xmin_after_tuning_table_column_list, mean_x_original_table_column_list)

            # find xmax of table_spanning_cell
            xmax_original_table_spanning_cell = get_bounding_box_object(table_spanning_cell)[X_MAX]
            new_xmax_table_spanning_cell = find_element_value_in_element_value_list(xmax_original_table_spanning_cell, X_MAX, xmax_after_tuning_table_column_list, mean_x_original_table_column_list)

            # find ymin of table_spanning_cell
            ymin_original_table_spanning_cell = get_bounding_box_object(table_spanning_cell)[Y_MIN]
            new_ymin_table_spanning_cell = find_element_value_in_element_value_list(ymin_original_table_spanning_cell, Y_MIN, ymin_after_tuning_table_row_list, mean_y_original_table_row_list)

            # find ymax of table_spanning_cell
            ymax_original_table_spanning_cell = get_bounding_box_object(table_spanning_cell)[Y_MAX]
            new_ymax_table_spanning_cell = find_element_value_in_element_value_list(ymax_original_table_spanning_cell, Y_MAX, ymax_after_tuning_table_row_list, mean_y_original_table_row_list)

            # update xmin & xmax & ymin & ymax of table_spanning_cell value
            update_element_value_of_object(table_spanning_cell, X_MIN, new_xmin_table_spanning_cell)
            update_element_value_of_object(table_spanning_cell, X_MAX, new_xmax_table_spanning_cell)
            update_element_value_of_object(table_spanning_cell, Y_MIN, new_ymin_table_spanning_cell)
            update_element_value_of_object(table_spanning_cell, Y_MAX, new_ymax_table_spanning_cell)


        ## TUNING XMIN & XMAX & YMIN & YMAX OF ALL TABLE_COLUMN_HEADER

        for table_column_header in table_column_header_list:

            # find xmin of table_column_header
            xmin_original_table_column_header = get_bounding_box_object(table_column_header)[X_MIN]
            new_xmin_table_column_header = find_element_value_in_element_value_list(xmin_original_table_column_header, X_MIN, xmin_after_tuning_table_column_list, mean_x_original_table_column_list)

            # find xmax of table_column_header
            xmax_original_table_column_header = get_bounding_box_object(table_column_header)[X_MAX]
            new_xmax_table_column_header = find_element_value_in_element_value_list(xmax_original_table_column_header, X_MAX, xmax_after_tuning_table_column_list, mean_x_original_table_column_list)

            # find ymin of table_column_header
            ymin_original_table_column_header = get_bounding_box_object(table_column_header)[Y_MIN]
            new_ymin_table_column_header = find_element_value_in_element_value_list(ymin_original_table_column_header, Y_MIN, ymin_after_tuning_table_row_list, mean_y_original_table_row_list)

            # find ymax of table_column_header 
            ymax_original_table_column_header = get_bounding_box_object(table_column_header)[Y_MAX]
            new_ymax_table_column_header = find_element_value_in_element_value_list(ymax_original_table_column_header, Y_MAX, ymax_after_tuning_table_row_list, mean_y_original_table_row_list)

            # update xmin & xmax & ymin & ymax of table_column_header value
            update_element_value_of_object(table_column_header, X_MIN, new_xmin_table_column_header)
            update_element_value_of_object(table_column_header, X_MAX, new_xmax_table_column_header)
            update_element_value_of_object(table_column_header, Y_MIN, new_ymin_table_column_header)
            update_element_value_of_object(table_column_header, Y_MAX, new_ymax_table_column_header)

    tree.write(join_path(DST_ADDR, label_name))
    # num_processed += 1

print("Finetune the table successfully !!!")
print("Copyright @ProjectHoon")