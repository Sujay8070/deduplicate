import os
import argparse
import warnings
import shutil
import cv2
import similarity_utils as su


def similarity_score(image_1, image_2, tolerance):
    gray1 = su.preprocess_image_change_detection(image_1, [5,7,11])
    gray2 = su.preprocess_image_change_detection(image_2, [5,7,11])
    sim_score, _, _ = su.compare_frames_change_detection(gray1, gray2, tolerance)
    
    return sim_score

def check_image_similarity(img_dir: str, contour_threshold: int):
    """Returns a dictionary with three items - min_contour_area, 
        unique_image_files list and duplicate_image_files list

    Args:
        img_dir (str): folder path with all the images
        contour_threshold (int): minimum area in pixels to
                                define two images as dissimilar

    Returns:
        dict: a three element dictonary with contour_threshold, 
                unique_image_files list and duplicate_image_files list
    """
    corrupt_files = []
    file_name_ls = []
    im_arr_ls = []
    unique_im_arr_ls = []
    similarity_dict = {'min_area_threshold': contour_threshold,
                       'unique_image_files': [],
                       'duplicate_image_files': [],
                    }
    new_im_size = (500, 500)

    if len(os.listdir(img_dir)) == 0:
        warnings.warn("\tThe image folder is EMPTY!", UserWarning)
        return unique_im_arr_ls
       
    for file in os.listdir(img_dir):
        if file.endswith(".jpg") or file.endswith(".png"):
            im_arr = cv2.imread(os.path.join(img_dir,file))
            
            # an image should be readable and at least 32x32
            if im_arr is None:
                print(f"\tError opening file: {file}")
                corrupt_files.append(file)
                continue
            elif im_arr.size < 1024:
                print(f"\tInsufficient image-size: {file}")
                continue

            im_resized = cv2.resize(im_arr,
                                    new_im_size,
                                    interpolation = cv2.INTER_AREA)
            im_arr_ls.append(im_resized)
            file_name_ls.append(file)

    if len(file_name_ls) == 0:
        warnings.warn("\tNo '.png' or '.jpg' files found in the folder", UserWarning)
        return unique_im_arr_ls

    print("\t### checking similar image frames...")
    for idx, filename in enumerate(file_name_ls):
        is_similar = False
        ## check similarity with previous image
        if idx >= 1:
            sim_score = similarity_score(im_arr_ls[idx], 
                                            im_arr_ls[idx-1], 
                                            contour_threshold)
            if sim_score == 0:
                is_similar = True
                similarity_dict['duplicate_image_files'].append(filename)
                continue
                        
        ## check similarity with all unique images
        for uniq_im in unique_im_arr_ls:
            sim_score = similarity_score(im_arr_ls[idx], 
                                            uniq_im,
                                            contour_threshold)
            if sim_score == 0:
                is_similar = True
                similarity_dict['duplicate_image_files'].append(filename)
                break
        if not is_similar:
            unique_im_arr_ls.append(im_arr_ls[idx])
            similarity_dict['unique_image_files'].append(filename)

    print(f"\t### found {len(similarity_dict['unique_image_files'])} unique frames")
    return similarity_dict


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", type=os.path.abspath, required=True,
                        help="Provide absolute path to the image folder")
    parser.add_argument("-a", "--min_contour_area", type=int, default=5000,
                        help="Provide minimum area of pixels to differentiate two images")
    args = parser.parse_args()

    im_similarity_dict = check_image_similarity(args.path, args.min_contour_area)
    
    shutil.rmtree(args.path + '/unique', ignore_errors=True)
    os.makedirs(args.path + '/unique')
    for i, im_file in enumerate(im_similarity_dict['unique_image_files']):
        im = cv2.imread(os.path.join(args.path, im_file))
        cv2.imwrite(os.path.join(args.path + '/unique', im_file), im)
