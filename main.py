import os
import cv2
import argparse
import warnings
import similarity_utils as du


def similarity_score(image_1, image_2, tolerance):
    gray1 = du.preprocess_image_change_detection(image_1, [3,5,7])
    gray2 = du.preprocess_image_change_detection(image_2, [3,5,7])    
    sim_score, _, _ = du.compare_frames_change_detection(gray1, gray2, tolerance)
    
    return sim_score

def fetch_unique_images(img_dir, contour_threshold):
    
    corrupt_files = []
    file_name_ls = []
    im_arr_ls = []
    unique_im_arr_ls = []
    similarity_dict = {'min_are_threshold': contour_threshold,
                       'unique_image_files': [],
                       'duplicate_image_files': [],
                    }
    new_im_size = (500, 500)

    if len(os.listdir(img_dir)) == 0:
        warnings.warn("The image folder is EMPTY!", UserWarning)
        return unique_im_arr_ls
    else:
        
        for file in os.listdir(img_dir):
            if file.endswith(".jpg") or file.endswith(".png"):
                im_arr = cv2.imread(os.path.join(img_dir,file))

                # an image should be readable and at least 64x64
                if im_arr is None:
                    print(f"Error opening file: {file}")
                    corrupt_files.append(file)
                    continue
                elif im_arr.size < 4096:
                    print(f"Image file: {file} does not have sufficient size")
                    continue

                im_resized = cv2.resize(im_arr, 
                                        new_im_size, 
                                        interpolation = cv2.INTER_AREA)
                im_arr_ls.append(im_resized)
                file_name_ls.append(file)

                    
        if len(file_name_ls) == 0:
            warnings.warn("No '.png' or '.jpg' files found in the folder", UserWarning)
            return unique_im_arr_ls

        print("### checking similar image frames...")
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
            
        return similarity_dict['unique_image_files']



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=os.path.abspath, 
                        help="Provide absolute path to the image folder")
    args = parser.parse_args()

    least_contour_area = 2000
    unique_im_files = fetch_unique_images(args.path, least_contour_area)
    print(len(unique_im_files))

    for i, im_file in enumerate(unique_im_files):
        im = cv2.imread(os.path.join(args.path, im_file))
        cv2.imwrite(os.path.join(args.path + '/unique', im_file), im)
    

