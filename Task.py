#!/usr/bin/env python
# coding: utf-8

# This code calculates the percentage match and determines the correctness status for various attributes (volume, bounding box coordinates, faces) between a target.json and attemptx.json. The EPSILON is used to handle small differences due to floating-point precision. The compare_coordinates function checks if coordinates are close enough within the defined epsilon.

# In[1]:


import json

# A small value to account for floating-point precision issues
EPSILON = 1e-5

def calculate_percentage_match(target, attempt):
    # Calculate the total number of attributes to be considered
    total_attributes = len(target) + len(target['bbMin']) + len(target['bbMax']) + len(target['faces'][0])

    # Initialize counters for matching attributes and correctness status
    matching_attributes = 0

    # Dictionary to track correctness status of various attributes
    correct_attributes = {
        'volume': False,
        'bbMin': False,
        'bbMax': False,
        'faces': [{'area': False, 'bbMin': False, 'bbMax': False, 'centroid': False} for _ in target['faces']]
    }

    # Check volume: Compare the volume of the target and attempt
    if abs(target['volume'] - attempt['volume']) < EPSILON:
        matching_attributes += 1
        correct_attributes['volume'] = True

    # Check bounding box details: Compare the coordinates of bbMin and bbMax
    correct_attributes['bbMin'] = compare_coordinates(target['bbMin'], attempt['bbMin'])
    correct_attributes['bbMax'] = compare_coordinates(target['bbMax'], attempt['bbMax'])

    # Check faces: Compare coordinates and area for each face
    target_faces = target['faces']
    attempt_faces = attempt['faces']

    for i, (target_face, attempt_face) in enumerate(zip(target_faces, attempt_faces)):
        correct_attributes['faces'][i]['bbMin'] = compare_coordinates(target_face['bbMin'], attempt_face['bbMin'])
        correct_attributes['faces'][i]['bbMax'] = compare_coordinates(target_face['bbMax'], attempt_face['bbMax'])
        correct_attributes['faces'][i]['centroid'] = compare_coordinates(target_face['centroid'], attempt_face['centroid'])
        correct_attributes['faces'][i]['area'] = abs(target_face['area'] - attempt_face['area']) < EPSILON

    # Calculate the percentage match based on the number of matching attributes
    percentage_match = min((matching_attributes / total_attributes) * 100, 100.0)

    # Return the percentage match and correctness status
    return percentage_match, correct_attributes

def compare_coordinates(coord1, coord2):
    # Check if all coordinates are within a small epsilon difference
    return all(abs(c1 - c2) < EPSILON for c1, c2 in zip(coord1, coord2))


# This function reads target and attempt data from JSON files, calculates the percentage match, and provides a detailed comparison with correctness status for different components. The output is formatted to enhance readability.

# In[2]:


import json

def print_percentage_match(target_path, attempt_paths):
    # Read the target data from the specified file
    with open(target_path, 'r') as target_file:
        target_data = json.load(target_file)
    
    # Loop through each attempt file
    for attempt_path in attempt_paths:
        # Read the attempt data from the current attempt file
        with open(attempt_path, 'r') as attempt_file:
            attempt_data = json.load(attempt_file)

        # Calculate the percentage match and get correctness attributes
        percentage_match, correct_attributes = calculate_percentage_match(target_data, attempt_data)

        # Print a separator line for better readability
        print("=====================================================================")

        # Display a header for the detailed comparison
        print(f"The Detailed Comparison between '{attempt_path}' and 'target.json':")

        # Print correctness of different components
        print("Correctness of different components:")
        print("Volume:", correct_attributes['volume'])
        print("Bounding Box Min:", correct_attributes['bbMin'])
        print("Bounding Box Max:", correct_attributes['bbMax'])

        # Count the number of matched faces
        matched_faces = sum(all(face_correctness[key] for key in ['bbMin', 'bbMax', 'centroid', 'area'])
                            for face_correctness in correct_attributes['faces'])
        print(f"Matched Faces: {matched_faces}/{len(target_data['faces'])}")

        # Count true and false occurrences for each face component
        true_counts = {key: sum(face_correctness[key] for face_correctness in correct_attributes['faces']) 
                       for key in ['bbMin', 'bbMax', 'centroid', 'area']}

        false_counts = {key: len(correct_attributes['faces']) - true_counts[key] for key in ['bbMin', 'bbMax', 'centroid', 'area']}

        # Display details for each face
        for i, face_correctness in enumerate(correct_attributes['faces']):
            print(f"Face {i + 1}:")
            for key in ['bbMin', 'bbMax', 'centroid', 'area']:
                print(f"  {key.capitalize()}: {face_correctness[key]}")

        # Display true counts for each face component
        print("\nTrue Counts:")
        for key in ['bbMin', 'bbMax', 'centroid', 'area']:
            print(f"  {key.capitalize()}: {true_counts[key]}")
        print(f"  Total True Count: {sum(true_counts.values())}")

        # Display false counts for each face component
        print("False Counts:")
        for key in ['bbMin', 'bbMax', 'centroid', 'area']:
            print(f"  {key.capitalize()}: {false_counts[key]}")
        print(f"  Total False Count: {sum(false_counts.values())}\n")

        # Calculate and display the percentage of correctness and incorrectness
        percentage_true = (sum(true_counts.values()) / (sum(true_counts.values()) + sum(false_counts.values()))) * 100
        print(f"The percentage of correctness is: {percentage_true:.2f}%")
        print(f"The percentage of incorrectness is: {100 - percentage_true:.2f}%\n")
        
        # Check if the attempt has a scored above a certain threshold
        if percentage_true >= 80:
            print(f"The correct file is '{attempt_path}'")

# Example usage
target_file_path = 'target.json'
attempt_files_paths = ['attempt1.json', 'attempt2.json', 'attempt3.json', 'attempt4.json']

print_percentage_match(target_file_path, attempt_files_paths)


# The correct file is 'attempt4.json'

# In[ ]:




